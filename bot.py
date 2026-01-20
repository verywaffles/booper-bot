import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
print("✅ .env loaded")
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def setup_hook():
    # Load your cogs here
    await bot.load_extension("cogs.general")
    await bot.load_extension("cogs.fun")
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.economy")
    await bot.load_extension("cogs.chess")
    # later: await bot.load_extension("cogs.economy"), etc.

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Booper is booping with cogs...")

if __name__ == "__main__":
    print("Booper is booping...")
    bot.run(token)




