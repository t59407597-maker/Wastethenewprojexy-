import asyncio
import logging
import os
import random
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
from Shashank.modules.bot.start import subscriptions_col, settings_col, OWNER_USERNAME

log = logging.getLogger(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_SUB_CACHE_TTL = 5.0
_SCAN_INTERVAL = 20
_CHAT_INTERVAL = 60

CHAT_SEQUENCE = [
    (0, "hellow"),
    (60, "ignore mardia ?"),
    (120, "shi hai maro maro ignore"),
    (180, "👀"),
    (240, "🙂"),
    (300, "😭"),
    (360, "kkrh?"),
    (420, "😂"),
]
REACTION_POOL = ["👀", "😭", "😂", "😐", "🔥"]


@dataclass
class VCState:
    joined: set = field(default_factory=set)
    current: Optional[int] = None
    fight_running: bool = False
    fight_file: Optional[str] = None
    fight_task: Optional[asyncio.Task] = None
    started: bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    auto_allvc: bool = False
    scan_task: Optional[asyncio.Task] = None
    chat_tasks: Dict[int, asyncio.Task] = field(default_factory=dict)


_states: Dict[int, VCState] = {}
_bridges: Dict[int, PyTgCalls] = {}
_sub_cache: Dict[int, tuple] = {}


def _vc_chat_map(client: Client) -> dict:
    """Per-VC text destinations. These are deliberately separate from the VC group chat."""
    value = getattr(client, "_vc_chat_map", None)
    if not isinstance(value, dict):
        value = {}
        setattr(client, "_vc_chat_map", value)
    return value


def _load_vc_chat_map(client: Client):
    uid = getattr(client, "_waste_owner_uid", None)
    if not uid:
        return
    try:
        doc = settings_col.find_one({"_id": int(uid)}) or {}
        raw = doc.get("vc_chat_map", {})
        if isinstance(raw, dict):
            _vc_chat_map(client).update({str(k): int(v) for k, v in raw.items()})
    except Exception:
        pass


def _vc_destination(client: Client, vc_id: int) -> Optional[int]:
    target = _vc_chat_map(client).get(str(vc_id))
    return int(target) if target is not None else None


def _key(client: Client) -> int:
    return id(client)


async def _subscription_active(client: Client) -> bool:
    key = _key(client)
    now = asyncio.get_running_loop().time()
    cached = _sub_cache.get(key)
    if cached and now - cached[0] < _SUB_CACHE_TTL:
        return cached[1]

    uid = getattr(client, "_waste_owner_uid", None)
    if not uid:
        try:
            me = await client.get_me()
            uid = me.id
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
        "Free users `.join <group_id>` se ek VC join kar sakte hain.\n"
        "`.allvc`, automatic VC joining aur VC chat automation ke liye subscription chahiye.\n\n"
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
            await call.play(target, path, config=GroupCallConfig(auto_start=False))
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


async def _join(client: Client, chat_id: int, retries: int = 4):
    state, call = await _bridge(client)
    async with state.lock:
        already_joined = chat_id in state.joined
        premium = await _subscription_active(client)
        if not premium and state.joined and not already_joined:
            raise PermissionError(_premium_message())
        if already_joined:
            state.current = chat_id
            return True

        last_exc = None
        for attempt in range(retries):
            try:
                await call.play(chat_id, None, config=GroupCallConfig(auto_start=False))
                state.joined.add(chat_id)
                state.current = chat_id
                _load_vc_chat_map(client)
                _start_chat_task(client, chat_id, state)
                return True
            except Exception as exc:
                last_exc = exc
                await asyncio.sleep(min(5, 1 + attempt))
        raise last_exc or RuntimeError("VC join failed")


async def _join_one(client: Client, call: PyTgCalls, chat_id: int):
    # A few retries catch transient Telegram/PyTgCalls timing errors.
    for attempt in range(4):
        try:
            await call.play(chat_id, None, config=GroupCallConfig(auto_start=False))
            return chat_id, True
        except Exception as exc:
            if attempt == 3:
                return chat_id, exc
            await asyncio.sleep(1 + attempt)
    return chat_id, False


async def _active_group_ids(client: Client):
    """Return group dialogs worth checking. PyTgCalls confirms which ones actually have an active VC."""
    ids = []
    seen = set()
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if not chat or chat.id in seen:
            continue
        ctype = getattr(chat.type, "value", chat.type)
        if ctype in (ChatType.GROUP.value, ChatType.SUPERGROUP.value):
            seen.add(chat.id)
            ids.append(chat.id)
    return ids


async def _vc_chat_loop(client: Client, chat_id: int, state: VCState):
    """Send the VC automation sequence ONLY to the separately configured VC chat."""
    try:
        destination = _vc_destination(client, chat_id)
        if destination is None:
            log.info("No separate VC chat configured for %s; VC chat automation skipped.", chat_id)
            return

        for minute, text in CHAT_SEQUENCE:
            if chat_id not in state.joined:
                return
            if minute:
                await asyncio.sleep(60)
            if chat_id not in state.joined:
                return
            try:
                await client.send_message(destination, text)
            except Exception as exc:
                log.debug("VC chat message failed in %s -> %s: %s", chat_id, destination, exc)

        # From minute 8 onward: exactly one reaction/message every minute.
        while chat_id in state.joined:
            await asyncio.sleep(60)
            if chat_id not in state.joined:
                return
            try:
                await client.send_message(destination, random.choice(REACTION_POOL))
            except Exception as exc:
                log.debug("VC reaction failed in %s -> %s: %s", chat_id, destination, exc)
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        log.debug("VC chat task ended for %s: %s", chat_id, exc)


def _start_chat_task(client: Client, chat_id: int, state: VCState):
    old = state.chat_tasks.get(chat_id)
    if old and not old.done():
        return
    state.chat_tasks[chat_id] = asyncio.create_task(_vc_chat_loop(client, chat_id, state))


async def _cancel_chat_tasks(state: VCState):
    tasks = list(state.chat_tasks.values())
    state.chat_tasks.clear()
    for task in tasks:
        if task and not task.done():
            task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


async def _allvc_scanner(client: Client, state: VCState, call: PyTgCalls):
    """Keep premium .allvc mode alive and discover newly active VCs in joined groups."""
    try:
        while state.auto_allvc:
            if not await _subscription_active(client):
                state.auto_allvc = False
                break
            try:
                ids = await _active_group_ids(client)
                # Don't hammer Telegram: only groups not already joined are attempted.
                candidates = [x for x in ids if x not in state.joined]
                if candidates:
                    results = await asyncio.gather(
                        *(_join_one(client, call, chat_id) for chat_id in candidates),
                        return_exceptions=False,
                    )
                    for chat_id, result in results:
                        if result is True:
                            state.joined.add(chat_id)
                            state.current = chat_id
                            _load_vc_chat_map(client)
                            _start_chat_task(client, chat_id, state)
            except Exception as exc:
                log.debug("Automatic VC scan failed: %s", exc)
            await asyncio.sleep(_SCAN_INTERVAL)
    except asyncio.CancelledError:
        raise


async def enable_auto_allvc(client: Client):
    state, call = await _bridge(client)
    if state.scan_task and not state.scan_task.done():
        state.auto_allvc = True
        return
    state.auto_allvc = True
    state.scan_task = asyncio.create_task(_allvc_scanner(client, state, call))


async def disable_auto_allvc(client: Client):
    state, _ = await _bridge(client)
    state.auto_allvc = False
    task = state.scan_task
    state.scan_task = None
    if task and not task.done():
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


async def start_background_for_client(client: Client):
    """Called by the session host after login/restore. It only auto-scans if premium + enabled."""
    try:
        state, call = await _bridge(client)
        if await _subscription_active(client):
            # Setting is loaded from Mongo in start.py and attached to the client.
            if getattr(client, "_auto_allvc_enabled", False):
                await enable_auto_allvc(client)
    except Exception as exc:
        log.debug("Could not start VC background for client: %s", exc)


@Client.on_message(filters.command("vcchat", ".") & filters.me)
async def vc_chat_command(client: Client, message: Message):
    """Configure a separate Telegram chat where VC automation messages are sent.

    Usage inside the VC's group: .vcchat <destination_chat_id>
    Disable: .vcchat off
    """
    uid = getattr(client, "_waste_owner_uid", None)
    if not await _subscription_active(client):
        return await message.reply(_premium_message())
    args = message.command[1:] if len(message.command) > 1 else []
    vc_id = message.chat.id if message.chat else None
    if vc_id is None:
        return await message.reply("❌ Ye command group ke andar use karo.")
    if not args:
        current = _vc_destination(client, vc_id)
        return await message.reply(
            f"📡 **VC Chat:** `{current}`" if current else
            "📡 **VC Chat:** Not configured\n\nUse `.vcchat <chat_id>` to set a separate destination."
        )
    if args[0].lower() == "off":
        _vc_chat_map(client).pop(str(vc_id), None)
        if uid:
            settings_col.update_one({"_id": int(uid)}, {"$unset": {f"vc_chat_map.{vc_id}": ""}}, upsert=True)
        task = _states.get(_key(client), VCState()).chat_tasks.get(vc_id)
        if task and not task.done():
            task.cancel()
        return await message.reply("🛑 Separate VC chat disabled for this VC.")
    try:
        destination = int(args[0])
    except ValueError:
        return await message.reply("❌ Chat ID number hona chahiye.")
    try:
        await client.get_chat(destination)
    except Exception as exc:
        return await message.reply(f"❌ Destination chat access nahi ho raha: `{type(exc).__name__}`")
    _vc_chat_map(client)[str(vc_id)] = destination
    if uid:
        settings_col.update_one(
            {"_id": int(uid)},
            {"$set": {f"vc_chat_map.{vc_id}": destination}},
            upsert=True,
        )
    state = _states.get(_key(client))
    if state and vc_id in state.joined:
        _start_chat_task(client, vc_id, state)
    return await message.reply(
        "✅ **Separate VC Chat set.**\n"
        f"VC: `{vc_id}`\n"
        f"Messages will go only to: `{destination}`"
    )


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
        uid = getattr(client, "_waste_owner_uid", None)
        if uid:
            settings_col.update_one({"_id": int(uid)}, {"$set": {"allvc_auto": False}}, upsert=True)
        await disable_auto_allvc(client)
        async with state.lock:
            await _cancel_fight(state)
            joined = list(state.joined)
        results = await asyncio.gather(
            *(call.leave_call(chat_id) for chat_id in joined),
            return_exceptions=True,
        )
        async with state.lock:
            state.joined.clear()
            state.current = None
        await _cancel_chat_tasks(state)
        left = sum(not isinstance(r, Exception) for r in results)
        return await message.reply(f"🚪 Left `{left}` VC(s). Automatic VC joining disabled.")

    uid = getattr(client, "_waste_owner_uid", None)
    if uid:
        settings_col.update_one({"_id": int(uid)}, {"$set": {"allvc_auto": True}}, upsert=True)
    state.auto_allvc = True
    status = await message.reply("🔊 **Scanning and joining active VCs...**")
    ids = await _active_group_ids(client)
    results = await asyncio.gather(
        *(_join_one(client, call, chat_id) for chat_id in ids),
        return_exceptions=False,
    )
    ok_ids = [chat_id for chat_id, result in results if result is True]
    async with state.lock:
        _load_vc_chat_map(client)
        state.joined.update(ok_ids)
        for chat_id in ok_ids:
            _start_chat_task(client, chat_id, state)
        if ok_ids:
            state.current = ok_ids[-1]
    await enable_auto_allvc(client)
    failed = len(results) - len(ok_ids)
    try:
        await status.edit(
            "✅ **ALL VC JOIN MODE ON**\n"
            f"Joined now: `{len(ok_ids)}`\n"
            f"Skipped/inactive/unavailable: `{failed}`\n\n"
            "New active VCs will be checked automatically every 20 seconds."
        )
    except Exception:
        pass


@Client.on_message(filters.command("fight", ".") & filters.me)
async def fight(client: Client, message: Message):
    state, call = await _bridge(client)
    if not state.joined:
        return await message.reply("❌ Pehle `.join <group_id>` ya premium `.allvc join` karo.")
    if message.chat and message.chat.id in state.joined:
        state.current = message.chat.id
    if not state.current:
        return await message.reply("❌ No selected VC.")
    replied = message.reply_to_message
    if not replied or not (replied.audio or replied.voice):
        return await message.reply("❌ `.fight` ko audio/voice message ke reply me bhejo.")
    status = await message.reply("⬇️ Audio download ho raha hai…")
    path = os.path.join(DOWNLOAD_DIR, f"fight_{uuid.uuid4().hex}{'.ogg' if replied.voice else '.mp3'}")
    try:
        await replied.download(file_name=path)
        async with state.lock:
            await _cancel_fight(state)
            state.fight_file = path
            state.fight_running = True
            state.fight_task = asyncio.create_task(_fight_loop(state, call, state.current, path))
        await status.edit("🔥 **FIGHT started**\nAudio repeat hoga. `.fightstop` se stop hoga; account VC me rahega.")
    except Exception as exc:
        try:
            if os.path.exists(path): os.remove(path)
        except OSError:
            pass
        await status.edit(f"❌ **Fight failed**\n`{type(exc).__name__}: {exc}`")


@Client.on_message(filters.command("fightstop", ".") & filters.me)
async def fight_stop(client: Client, message: Message):
    state, call = await _bridge(client)
    async with state.lock:
        target = state.current
        if target is not None:
            try: await call.pause(target)
            except Exception: pass
        await _cancel_fight(state)
        state.fight_file = None
    await message.reply("🛑 **Fight audio stopped.** Account VC me connected hai.")


@Client.on_message(filters.command("vcleave", ".") & filters.me)
async def vcleave(client: Client, message: Message):
    state, call = await _bridge(client)
    target = state.current
    if len(message.command) > 1:
        try: target = int(message.command[1])
        except ValueError: return await message.reply("❌ Group ID must be a number.")
    if target is None:
        return await message.reply("ℹ️ No selected VC.")
    async with state.lock:
        if target == state.current: await _cancel_fight(state)
        try: await call.leave_call(target)
        except Exception: pass
        state.joined.discard(target)
        task = state.chat_tasks.pop(target, None)
        if task and not task.done(): task.cancel()
        state.current = next(iter(state.joined), None)
    await message.reply(f"🚪 VC left: `{target}`")


@Client.on_message(filters.command("vcstatus", ".") & filters.me)
async def vc_status(client: Client, message: Message):
    state, _ = await _bridge(client)
    joined = "\n".join(f"• `{x}`" for x in list(state.joined)[:50]) or "• None"
    await message.reply(
        f"📊 **VC Fighter Status**\n\n"
        f"Current VC: `{state.current}`\n"
        f"Joined VCs: `{len(state.joined)}`\n"
        f"Auto ALLVC: {'🟢 ON' if state.auto_allvc else '🔴 OFF'}\n"
        f"Fight: {'🟢 Playing' if state.fight_running else '🔴 Stopped'}\n\n{joined}"
    )


add_command_help("VcFight", [
    ["join", "Join one active VC: `.join <group_id>` (free)."],
    ["allvc", "Premium: `.allvc join` / `.allvc leave`; keeps discovering new active VCs."],
    ["fight", "Reply to audio/voice and repeat it in the selected VC."],
    ["fightstop", "Stop fight audio without leaving the VC."],
    ["vcleave", "Leave selected VC."],
    ["vcstatus", "Show joined VCs, auto mode and fight status."],
    ["vcchat", "Set a separate chat for VC automation: `.vcchat <chat_id>` / `.vcchat off`."],
])
