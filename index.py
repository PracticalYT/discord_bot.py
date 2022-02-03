import os
import discord
from utils import default
from utils.data import Bot, HelpFormat
import win32com.client as comclt
import logging
import threading
import time
import pyautogui

config = default.config()
print("Logging in...")

from problox import Problox

# https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid
rbx = Problox.from_cookiefile("cookies.txt")

#-------------------------------
import ctypes

SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
   _fields_ = [("wVk", ctypes.c_ushort),
               ("wScan", ctypes.c_ushort),
               ("dwFlags", ctypes.c_ulong),
               ("time", ctypes.c_ulong),
               ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
   _fields_ = [("uMsg", ctypes.c_ulong),
               ("wParamL", ctypes.c_short),
               ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
   _fields_ = [("dx", ctypes.c_long),
               ("dy", ctypes.c_long),
               ("mouseData", ctypes.c_ulong),
               ("dwFlags", ctypes.c_ulong),
               ("time",ctypes.c_ulong),
               ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
   _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]

class Input(ctypes.Structure):
   _fields_ = [("type", ctypes.c_ulong),
               ("ii", Input_I)]

def PressKey(hexKeyCode):
   extra = ctypes.c_ulong(0)
   ii_ = Input_I()
   ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
   x = Input( ctypes.c_ulong(1), ii_ )
   ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
   extra = ctypes.c_ulong(0)
   ii_ = Input_I()
   ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
   x = Input( ctypes.c_ulong(1), ii_ )
   ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


#-------------------------------

user_info = rbx.request(
    method="GET",
    url="https://users.roblox.com/v1/users/authenticated"
    ).json()
print(f"Authenticated as {user_info['name']}")

client = rbx.join_game(5805850838, locale="fr_fr")
print(f"Launched client with PID {client.pid}")
wsh = comclt.Dispatch("WScript.Shell")

count = 5
while (count == 5):
   pyautogui.typewrite('/')
   pyautogui.typewrite('/e dance')
   time.sleep(10)
   PressKey(0x1C) # 0x1C = enter
   ReleaseKey(0x1C)
   # time.sleep(random.randint(5,20)
   time.sleep(5)

client.wait()
print(f"Client was closed")

bot = Bot(
    command_prefix=config["prefix"], prefix=config["prefix"],
    owner_ids=config["owners"], command_attrs=dict(hidden=True), help_command=HelpFormat(),
    allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False),
    intents=discord.Intents(  # kwargs found at https://discordpy.readthedocs.io/en/latest/api.html?highlight=intents#discord.Intents
        guilds=True, members=True, messages=True, reactions=True, presences=True
    )
)

for file in os.listdir("cogs"):
    if file.endswith(".py"):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

try:
    bot.run(config["token"])
except Exception as e:
    print(f"Error when logging in: {e}")
