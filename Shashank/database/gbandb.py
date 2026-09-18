# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

from typing import Dict, List, Union
from Shashank.database import dbb as db

gbansdb = db.gban


async def gban_list() -> list:
    users = gbansdb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return users

async def gban_count() -> int:
    users = gbansdb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)

async def gban_info(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True

async def gban_user(user_id: int):
    is_gbanned = await gban_info(user_id)
    if is_gbanned:
        return
    return await gbansdb.insert_one({"user_id": user_id})

async def ungban_user(user_id: int):
    is_gbanned = await gban_info(user_id)
    if not is_gbanned:
        return
    return await gbansdb.delete_one({"user_id": user_id})
