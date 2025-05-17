# -*- coding: utf-8 -*-
import discord
from discord.ext import commands
import os
from keep_alive import keep_alive
import google.generativeai as genai
from dotenv import load_dotenv
import json
from datetime import datetime

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

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    #print(f"Message received: {message.content}")
    log_chat_txt(message.author.name, message.content)
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
        log_chat_txt("bot", gemini_response.text)
        await ctx.send(gemini_response.text)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")

keep_alive() # เรียกใช้เว็บเซิร์ฟเวอร์
bot.run(DISCORD_TOKEN)