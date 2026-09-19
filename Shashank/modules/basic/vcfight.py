import asyncio
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import GroupCallConfig

from Shashank.modules.help import add_command_help
from Shashank.modules.bot.start import subscriptions_col, OWNER_USERNAME

log = logging.getLogger(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Number of VC join attempts that can run at the same time.
# There is NO total VC-count cap for premium users; this only controls simultaneous network work.
# No total VC-count limit for premium .allvc.
_SUB_CACHE_TTL = 5.0


@dataclass
class VCState:
    joined: set = field(default_factory=set)
    current: Optional[int] = None
    fight_running: bool = False
    fight_file: Optional[str] = None
    fight_task: Optional[asyncio.Task] = None
    started: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


_states: Dict[int, VCState] = {}
_bridges: Dict[int, PyTgCalls] = {}
_sub_cache: Dict[int, tuple] = {}


def _key(client: Client) -> int:
    return id(client)


async def _subscription_active(client: Client) -> bool:
    """Cached premium check so repeated VC commands don't block on Mongo."""
    key = _key(client)
    now = asyncio.get_running_loop().time()
    cached = _sub_cache.get(key)
    if cached and now - cached[0] < _SUB_CACHE_TTL:
        return cached[1]

    uid = getattr(client, "_waste_owner_uid", None)
    if not uid:
        # Main owner/self account is not automatically treated as premium.
        # Subscription is checked from the same collection as /subscription.
        try:
            uid = client.me.id if client.me else None
        except Exception:
            uid = None

    active = False
    if uid:
        def check():
            doc = subscriptions_col.find_one({"_id": int(uid)})
            if not doc:
                return False
            expires = doc.get("expires_at")
            if isinstance(expires, datetime):
                if expires.tzinfo is None:
                    expires = expires.replace(tzinfo=timezone.utc)
                if expires > datetime.now(timezone.utc):
                    return True
                try:
                    subscriptions_col.delete_one({"_id": int(uid)})
                except Exception:
                    pass
            return False

        try:
            active = await asyncio.to_thread(check)
        except Exception:
            active = False

    _sub_cache[key] = (now, active)
    return active


def _premium_message():
    return (
        "💎 **Subscription Required**\n\n"
        "Free users can join only **one VC** at a time.\n"
        f"Multiple VC / `.allvc` ke liye subscription chahiye.\n\n"
        f"Contact owner: @{OWNER_USERNAME}"
    )


async def _bridge(client: Client):
    key = _key(client)
    state = _states.setdefault(key, VCState())
    call = _bridges.get(key)
    if call is None:
        call = PyTgCalls(client)
        _bridges[key] = call
    if not state.started:
        await call.start()
        state.started = True
    return state, call


async def _duration(path: str) -> float:
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        out, _ = await proc.communicate()
        value = float(out.decode().strip())
        if value > 0:
            return value
    except Exception:
        pass
    return 30.0


async def _cancel_fight(state: VCState):
    state.fight_running = False
    task = state.fight_task
    state.fight_task = None
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def _fight_loop(state: VCState, call: PyTgCalls, target: int, path: str):
    try:
        while state.fight_running and state.current == target:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            duration = await _duration(path)
            await call.play(
                target, path, config=GroupCallConfig(auto_start=False)
            )
            await asyncio.sleep(max(1.0, duration - 0.25))
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        log.warning("VC fight stopped: %s", exc)
        state.fight_running = False
    finally:
        if not state.fight_running:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


async def _join(client: Client, chat_id: int):
    """Join one VC. Free accounts are limited to one active VC."""
    state, call = await _bridge(client)

    async with state.lock:
        already_joined = chat_id in state.joined
        premium = await _subscription_active(client)

        if not premium and state.joined and not already_joined:
            raise PermissionError(_premium_message())

        # Do not unnecessarily call PyTgCalls again for an already joined VC.
        if already_joined:
            state.current = chat_id
            return

        await call.play(
            chat_id, None, config=GroupCallConfig(auto_start=False)
        )
        state.joined.add(chat_id)
        state.current = chat_id


async def _join_one(call: PyTgCalls, chat_id: int):
    try:
        await call.play(
            chat_id, None, config=GroupCallConfig(auto_start=False)
        )
        return chat_id, True
    except Exception as exc:
        return chat_id, exc


@Client.on_message(filters.command("allvc", ".") & filters.me)
async def all_vc(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1].lower() not in {"join", "leave"}:
        return await message.reply("Usage: `.allvc join` / `.allvc leave`")

    premium = await _subscription_active(client)
    if not premium:
        return await message.reply(_premium_message())

    state, call = await _bridge(client)
    action = message.command[1].lower()

    if action == "leave":
        async with state.lock:
            await _cancel_fight(state)
            joined = list(state.joined)

        async def leave_one(chat_id):
            try:
                await call.leave_call(chat_id)
                return True
            except Exception:
                return False

        results = await asyncio.gather(
            *(leave_one(chat_id) for chat_id in joined),
            return_exceptions=False,
        )
        left = sum(results)

        async with state.lock:
            state.joined.clear()
            state.current = None

        return await message.reply(f"🚪 Left `{left}` VC(s).")

    # Reply immediately so the user does not wait for dialog scanning.
    status = await message.reply("🔊 **I am joining all active VC...**")

    chat_ids = []
    seen = set()
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if not chat:
            continue
        chat_type = getattr(chat.type, "value", chat.type)
        if chat_type not in (ChatType.GROUP.value, ChatType.SUPERGROUP.value):
            continue
        if chat.id not in seen:
            seen.add(chat.id)
            chat_ids.append(chat.id)

    # Premium has no application-level VC count limit.
    # Launch all discovered VC join attempts concurrently.
    results = await asyncio.gather(
        *(_join_one(call, chat_id) for chat_id in chat_ids),
        return_exceptions=False,
    )

    ok_ids = [chat_id for chat_id, result in results if result is True]
    failed = len(results) - len(ok_ids)

    async with state.lock:
        state.joined.update(ok_ids)
        if ok_ids:
            state.current = ok_ids[-1]

    try:
        await status.edit(
            "✅ **ALL VC JOIN DONE**\n"
            f"Joined: `{len(ok_ids)}`\n"
            f"Failed/No active VC: `{failed}`"
        )
    except Exception:
        pass


@Client.on_message(filters.command("fight", ".") & filters.me)
async def fight(client: Client, message: Message):
    state, call = await _bridge(client)

    if not state.joined:
        return await message.reply(
            "❌ Pehle `.join <group_id>` karke VC join karo."
        )

    # The group where .fight is sent becomes the selected VC.
    if message.chat and message.chat.id in state.joined:
        state.current = message.chat.id

    if not state.current:
        return await message.reply("❌ No selected VC.")

    replied = message.reply_to_message
    if not replied or not (replied.audio or replied.voice):
        return await message.reply(
            "❌ `.fight` ko audio/voice message ke reply me bhejo."
        )

    status = await message.reply("⬇️ Audio download ho raha hai…")
    path = os.path.join(
        DOWNLOAD_DIR,
        f"fight_{uuid.uuid4().hex}{'.ogg' if replied.voice else '.mp3'}",
    )

    try:
        await replied.download(file_name=path)
        async with state.lock:
            await _cancel_fight(state)
            state.fight_file = path
            state.fight_running = True
            state.fight_task = asyncio.create_task(
                _fight_loop(state, call, state.current, path)
            )

        await status.edit(
            "🔥 **FIGHT started**\n"
            "Audio repeat hoga. `.fightstop` se stop hoga; account VC me rahega."
        )
    except Exception as exc:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            pass
        await status.edit(f"❌ **Fight failed**\n`{type(exc).__name__}: {exc}`")


@Client.on_message(filters.command("fightstop", ".") & filters.me)
async def fight_stop(client: Client, message: Message):
    state, call = await _bridge(client)
    async with state.lock:
        target = state.current
        if target is not None:
            try:
                await call.pause(target)
            except Exception:
                pass
        await _cancel_fight(state)
        state.fight_file = None

    await message.reply("🛑 **Fight audio stopped.** Account VC me connected hai.")


@Client.on_message(filters.command("vcleave", ".") & filters.me)
async def vcleave(client: Client, message: Message):
    state, call = await _bridge(client)
    target = state.current

    if len(message.command) > 1:
        try:
            target = int(message.command[1])
        except ValueError:
            return await message.reply("❌ Group ID must be a number.")

    if target is None:
        return await message.reply("ℹ️ No selected VC.")

    async with state.lock:
        if target == state.current:
            await _cancel_fight(state)
        try:
            await call.leave_call(target)
        except Exception:
            pass
        state.joined.discard(target)
        state.current = next(iter(state.joined), None)

    await message.reply(f"🚪 VC left: `{target}`")


@Client.on_message(filters.command("vcstatus", ".") & filters.me)
async def vc_status(client: Client, message: Message):
    state, _ = await _bridge(client)
    joined = "\n".join(
        f"• `{x}`" for x in list(state.joined)[:50]
    ) or "• None"

    await message.reply(
        f"📊 **VC Fighter Status**\n\n"
        f"Current VC: `{state.current}`\n"
        f"Joined VCs: `{len(state.joined)}`\n"
        f"Fight: {'🟢 Playing' if state.fight_running else '🔴 Stopped'}\n\n"
        f"{joined}"
    )


add_command_help("VcFight", [
    ["join", "Join one active VC: `.join <group_id>` (free) / multiple VCs (premium)."],
    ["allvc", "Premium only: `.allvc join` / `.allvc leave` all active VCs."],
    ["fight", "Reply to an audio/voice and repeat it in the selected VC."],
    ["fightstop", "Stop fight audio without leaving the VC."],
    ["vcleave", "Leave the selected VC."],
    ["vcstatus", "Show selected/joined VCs and fight status."],
])
