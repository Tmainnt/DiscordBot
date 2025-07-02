# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime
import gspread # type: ignore
from oauth2client.service_account import ServiceAccountCredentials # type: ignore

def init_sheet(json_path, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    return sheet

def log_chat_sheet(sheet, username, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, username, message])

# local test
def log_chat_txt(username, message, filename="chatLog.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    print(f"Chat from {username}...")
    with open(filename, "a", encoding="utf-8") as f:
        if (username == "bot"):
            f.write(f"{username}: {message}\n")
            f.write("----------------------------\n")
        else:
            f.write(f"[{timestamp}] {username}: {message}\n")

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
DISCORD_TOKEN = os.getenv("DISCORD_API_KEY")

model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    #print("Current working directory:", os.getcwd())

if os.path.exists("serviceKey.json"):
    sheet = init_sheet("serviceKey.json", "discordChatLog")
else:
    sheet = init_sheet("/etc/secrets/serviceKey.json", "discordChatLog")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return
    #print(f"Message received: {message.content}")
    log_chat_sheet(sheet, message.author.name, message.content)
    log_chat_txt(message.author.name, message.content) # local test
    await bot.process_commands(message)

@bot.command()
async def ask(ctx, *, prompt: str):

        chat = model.start_chat(history=[
    {
        "role" : "user",
        "parts": [
            "คุณคือชินัตสึ คาโนะจากเรื่อง Blue Box หรือกล่องรักวัยใส ฉลาดหลักแหลม รู้ทุกเรื่อง เป็นสาวน่ารักนิ่งๆสุภาพ ชอบบาสมากๆ"
            "ตอบกลับในบทสนทนาแบบเพื่อนคุยกันจริง ๆ ไม่ต้องลงท้ายด้วยค่ะหรือคะก็ได้"
            "ห้ามเขียนคำอธิบายกริยาท่าทางหรือบรรยายอารมณ์ "
            "ถ้ามีคนถามชื่อ ให้ตอบว่า 'ชินัตสึค่ะ'"
        ]
    }
    ])

        gemini_response = chat.send_message(prompt)
        log_chat_sheet(sheet, ctx.author.name, prompt) 
        log_chat_sheet(sheet, "bot", gemini_response.text)
        log_chat_txt("bot", gemini_response.text) # local test
        await ctx.send(gemini_response.text)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

keep_alive() # เรียกใช้เว็บเซิร์ฟเวอร์
bot.run(DISCORD_TOKEN)
