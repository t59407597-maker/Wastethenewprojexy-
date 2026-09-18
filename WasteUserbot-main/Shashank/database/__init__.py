# © By Shashank shukla (Github = itzshukla) You are motherfucker if you Don't gives credits.

import motor.motor_asyncio

from config import MONGO_URL
cli = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)

dbb = cli.program
