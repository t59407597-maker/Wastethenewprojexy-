import asyncio
import logging
import os
import random
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import GroupCallConfig

from Shashank.modules.help import add_command_help

log = logging.getLogger(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


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


def _key(client: Client) -> int:
    return id(client)


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


async def _subscription_active(client: Client):
    """Return (active, owner_username) without blocking the event loop."""
    try:
        from Shashank.modules.bot.start import _sub_active, OWNER_USERNAME
        uid = getattr(client, "_waste_owner_uid", None)
        if uid is None:
            me = await client.get_me()
            uid = me.id
        active, _ = await asyncio.to_thread(_sub_active, int(uid))
        return active, OWNER_USERNAME
    except Exception:
        return False, "II_JPEXO_II"


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


async def _join(client: Client, chat_id: int):
    """Join one VC for free users; premium users can keep multiple VCs."""
    state, call = await _bridge(client)
    active, owner = await _subscription_active(client)

    async with state.lock:
        # Free users are limited to one VC. Do not switch automatically:
        # attempting another VC requires subscription.
        if not active and state.joined and chat_id not in state.joined:
            raise PermissionError(
                f"Subscription required for multiple VCs.\n"
                f"Contact @{owner} to activate your subscription."
            )

        await call.play(chat_id, None, config=GroupCallConfig(auto_start=False))
        state.joined.add(chat_id)
        state.current = chat_id


async def _join_one(call, chat_id: int):
    try:
        await call.play(chat_id, None, config=GroupCallConfig(auto_start=False))
        return chat_id, True
    except Exception:
        return chat_id, False


@Client.on_message(filters.command("allvc", ".") & filters.me)
async def all_vc(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1].lower() not in {"join", "leave"}:
        return await message.reply("Usage: `.allvc join` / `.allvc leave`")

    active, owner = await _subscription_active(client)
    if not active:
        return await message.reply(
            f"💎 **Subscription Required**\n\n"
            f"` .allvc {message.command[1].lower()} ` is available for subscribed users.\n"
            f"Contact @{owner} to activate your subscription."
        )

    state, call = await _bridge(client)
    action = message.command[1].lower()

    if action == "leave":
        status = await message.reply("🚪 **I am leaving all joined VC...**")
        async with state.lock:
            await _cancel_fight(state)
            joined_ids = list(state.joined)
            state.joined.clear()
            state.current = None

        async def leave_one(chat_id):
            try:
                await call.leave_call(chat_id)
                return True
            except Exception:
                return False

        results = await asyncio.gather(*(leave_one(x) for x in joined_ids), return_exceptions=True)
        left = sum(r is True for r in results)
        return await status.edit(f"🚪 **ALL VC LEAVE DONE**\nLeft: `{left}`")

    # Give immediate feedback before scanning/connecting to dialogs.
    status = await message.reply("🔊 **I am joining all active VC...**")

    dialogs = []
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if not chat:
            continue
        chat_type = getattr(chat.type, "value", chat.type)
        if chat_type in (ChatType.GROUP.value, ChatType.SUPERGROUP.value):
            dialogs.append(chat.id)

    # A small concurrency limit keeps Telegram/PyTgCalls stable while
    # making all-vc joining noticeably faster than sequential calls.
    sem = asyncio.Semaphore(5)

    async def join_limited(chat_id):
        async with sem:
            return await _join_one(call, chat_id)

    results = await asyncio.gather(*(join_limited(x) for x in dialogs), return_exceptions=True)
    ok = 0
    failed = 0
    for result in results:
        if isinstance(result, tuple) and result[1]:
            state.joined.add(result[0])
            state.current = result[0]
            ok += 1
        else:
            failed += 1

    await status.edit(
        f"✅ **ALL VC JOIN DONE**\n"
        f"Joined: `{ok}`\n"
        f"Failed/No active VC: `{failed}`"
    )


@Client.on_message(filters.command("fight", ".") & filters.me)
async def fight(client: Client, message: Message):
    state, call = await _bridge(client)
    if not state.current:
        return await message.reply("❌ Pehle `.join <group_id>` karke VC join karo.")
    if message.chat and message.chat.id != state.current:
        return await message.reply(
            f"❌ Fighting selected VC wale group me chalegi.\nSelected group: `{state.current}`"
        )
    replied = message.reply_to_message
    if not replied or not (replied.audio or replied.voice):
        return await message.reply("❌ `.fight` ko audio/voice message ke reply me bhejo.")

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
    joined = "\n".join(f"• `{x}`" for x in list(state.joined)[:50]) or "• None"
    await message.reply(
        f"📊 **VC Fighter Status**\n\n"
        f"Current VC: `{state.current}`\n"
        f"Joined VCs: `{len(state.joined)}`\n"
        f"Fight: {'🟢 Playing' if state.fight_running else '🔴 Stopped'}\n\n"
        f"{joined}"
    )


add_command_help(
    "VcFight",
    [
        ["join", "Join a specific active voice chat: `.join <group_id>`"],
        ["allvc", "Premium: join or leave all active voice chats."],
        ["fight", "Reply to an audio/voice and repeat it in the selected VC."],
        ["fightstop", "Stop fight audio without leaving the VC."],
        ["vcleave", "Leave the selected VC without using the normal chat-leave command."],
        ["vcstatus", "Show selected/joined VCs and fight status."],
    ],
)
