import discord
from discord.ext import commands
from utils.gemini import ask_gemini

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ask(self, ctx, *, prompt: str):
        """Ask Gemini a question."""
        await ctx.send("Thinking...")
        reply = ask_gemini(prompt)
        await ctx.send(reply)

async def setup(bot):
    await bot.add_cog(AI(bot))
