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

async def _duration(path: str) -> float:
    try:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL,
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
                if os.path.exists(path): os.remove(path)
            except OSError: pass

async def _join(client: Client, chat_id: int):
    state, call = await _bridge(client)
    async with state.lock:
        await call.play(chat_id, None, config=GroupCallConfig(auto_start=False))
        state.joined.add(chat_id)
        state.current = chat_id

@Client.on_message(filters.command("allvc", ".") & filters.me)
async def all_vc(client: Client, message: Message):
    if len(message.command) < 2 or message.command[1].lower() not in {"join", "leave"}:
        return await message.reply("Usage: `.allvc join` / `.allvc leave`")
    state, call = await _bridge(client)
    action = message.command[1].lower()
    if action == "leave":
        async with state.lock:
            await _cancel_fight(state)
            left = 0
            for chat_id in list(state.joined):
                try:
                    await call.leave_call(chat_id); left += 1
                except Exception: pass
            state.joined.clear(); state.current = None
        return await message.reply(f"🚪 Left `{left}` VC(s).")
    ok, failed = 0, 0
    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if not chat: continue
        chat_type = getattr(chat.type, "value", chat.type)
        if chat_type not in (ChatType.GROUP.value, ChatType.SUPERGROUP.value): continue
        try:
            await call.play(chat.id, None, config=GroupCallConfig(auto_start=False))
            state.joined.add(chat.id); state.current = chat.id; ok += 1
        except Exception:
            failed += 1
    await message.reply(f"✅ **ALL VC JOIN DONE**\nJoined: `{ok}`\nFailed/No active VC: `{failed}`")

@Client.on_message(filters.command("fight", ".") & filters.me)
async def fight(client: Client, message: Message):
    state, call = await _bridge(client)
    if not state.current:
        return await message.reply("❌ Pehle `.join <group_id>` karke VC join karo.")
    if message.chat and message.chat.id != state.current:
        return await message.reply(f"❌ Fighting selected VC wale group me chalegi.\nSelected group: `{state.current}`")
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
        except OSError: pass
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
        state.current = next(iter(state.joined), None)
    await message.reply(f"🚪 VC left: `{target}`")

@Client.on_message(filters.command("vcstatus", ".") & filters.me)
async def vc_status(client: Client, message: Message):
    state, _ = await _bridge(client)
    joined = "\n".join(f"• `{x}`" for x in list(state.joined)[:50]) or "• None"
    await message.reply(f"📊 **VC Fighter Status**\n\nCurrent VC: `{state.current}`\nJoined VCs: `{len(state.joined)}`\nFight: {'🟢 Playing' if state.fight_running else '🔴 Stopped'}\n\n{joined}")


add_command_help("VcFight", [
    ["join", "Join a specific active voice chat: `.join <group_id>`"],
    ["allvc", "Join or leave all active voice chats: `.allvc join` / `.allvc leave`"],
    ["fight", "Reply to an audio/voice and repeat it in the selected VC."],
    ["fightstop", "Stop fight audio without leaving the VC."],
    ["vcleave", "Leave the selected VC without using the normal chat-leave command."],
    ["vcstatus", "Show selected/joined VCs and fight status."],
])
