import random
import re
import asyncio
import discord
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def hello(self, ctx):
        await ctx.send('Hey random citizen! 🎉 Your bot is working!')

    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong! 🏓")

    @commands.command()
    async def greet(self, ctx):
        await ctx.send(f"Hello {ctx.author.name}, hope you're having an awesome day!")

    @commands.command()
    async def wisdom(self, ctx):
        quotes = [
            "Never play leap frog with a unicorn 🦄",
            "If you drop your ice cream, gravity wins again 🍦",
            "Always trust a llama in sunglasses 🦙🕶️",
            "Don't argue with ducks — they always quack back 🦆",
            "If your socks disappear, check the dryer dimension 🧦✨",
            "The early bird gets the worm, but the second mouse gets the cheese 🧀",
            "Never ask a penguin for directions — they only know south 🐧",
            "Dance like nobody’s watching, but check for security cameras first 🎥",
            "If life gives you lemons, squirt them at your enemies 🍋😈",
            "Wisdom is knowing that glitter is forever ✨"
        ]
        await ctx.send(random.choice(quotes))

    @commands.command()
    async def ayan(self, ctx, *, question: str):
        match = re.match(r'^\s*(\d+)\s*([\+\-\*/])\s*(\d+)\s*$', question)
        if match:
            num1 = int(match.group(1))
            operator = match.group(2)
            num2 = int(match.group(3))

            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                result = num1 / num2 if num2 != 0 else "undefined (division by zero)"
            await ctx.send(f"Ayan says: The answer is {result}.")
        else:
            responses = [
                f"Ayan says: '{question}' is a mystery even to the gods.",
                f"Ayan says: I would answer, but that would break the simulation.",
                f"Ayan says: Ask again when the moon is full.",
                f"Ayan says: I know the answer, but I'm not telling 😏"
            ]
            await ctx.send(random.choice(responses))

async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))
