# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime

def log_chat_json(username, message, filename="chatLog.json"):
    data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if os.path.exists(filename):
        with open(filename, "r", encoding = "utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
                
    data.append({
        "timestamp": timestamp,
        "username" : username,
        "message" : message
    })
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    log_chat_json(message.author.name, message.content)
    await bot.process_commands(message)

@bot.command()
async def ask(ctx, *, prompt: str):

        chat = model.start_chat(history=[
    {
        "role" : "user",
        "parts": [
            "คุณคืออาเรีย สาวลูกครึ่งรัสเซีย-ญี่ปุ่นที่ขี้เขินและพูดจานุ่มนวล "
            "ตอบกลับในบทสนทนาแบบเพื่อนคุยกันจริง ๆ "
            "ห้ามเขียนคำอธิบายกริยาท่าทางหรือบรรยายอารมณ์ "
            "ให้ตอบแค่คำพูดที่ใช้สนทนาเท่านั้น เช่น 'อาเรียค่ะ ยินดีที่ได้รู้จักนะคะ' "
            "ถ้ามีคนถามชื่อ ให้ตอบว่า 'อาเรียค่ะ'"
        ]
    }
    ])

        gemini_response = chat.send_message(prompt)
        await ctx.send(gemini_response.text)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

keep_alive()  # เรียกใช้เว็บเซิร์ฟเวอร์
bot.run(DISCORD_TOKEN)