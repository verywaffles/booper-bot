import re
import asyncio
import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def waffle(self, ctx, member: discord.Member):
        try:
            await member.edit(nick="waffle")
            await ctx.send(f"{member.mention} is now known as waffle 🧇")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change that user's nickname.")
        except discord.HTTPException:
            await ctx.send("Something went wrong while trying to change the nickname.")

    @commands.command()
    async def unwaffle(self, ctx, member: discord.Member):
        try:
            await member.edit(nick=None)
            await ctx.send(f"{member.mention} is no longer a waffle 🧇")
        except discord.Forbidden:
            await ctx.send("I don't have permission to change that user's nickname.")
        except discord.HTTPException:
            await ctx.send("Something went wrong while trying to reset the nickname.")

    @commands.command()
    async def boop(self, ctx, member: discord.Member, *, duration: str):
        match = re.match(r"(\d+)(s|m|hr|d|y)", duration)
        if not match:
            await ctx.send("❌ Invalid duration format. Use like 1s, 5m, 2hr, 1d, 1y.")
            return

        amount, unit = int(match.group(1)), match.group(2)
        unit_seconds = {"s": 1, "m": 60, "hr": 3600, "d": 86400, "y": 31536000}
        total_seconds = amount * unit_seconds[unit]

        role_name = f"Muted-{ctx.channel.id}"
        mute_role = discord.utils.get(ctx.guild.roles, name=role_name)

        if not mute_role:
            mute_role = await ctx.guild.create_role(name=role_name)
            await ctx.channel.set_permissions(mute_role, send_messages=False, speak=False)

        await member.add_roles(mute_role)
        await ctx.send(f"🔇 {member.mention} has been booped for {duration} in this channel!")

        await asyncio.sleep(total_seconds)
        await member.remove_roles(mute_role)
        await ctx.send(f"✅ {member.mention} is now unbooped.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def nofun(self, ctx, member: discord.Member):
        guild = ctx.guild
        role_name = "No Fun"

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            role = await guild.create_role(name=role_name, reason="Created by Booper for No Fun mode")
            for channel in guild.text_channels:
                await channel.set_permissions(
                    role,
                    send_messages=True,
                    attach_files=False,
                    embed_links=False,
                    use_external_emojis=False,
                    use_external_stickers=False,
                    add_reactions=False,
                    send_messages_in_threads=True,
                    create_public_threads=False,
                    create_private_threads=False
                )

        await member.add_roles(role)
        await ctx.send(f"🚫 {member.mention} has been banished to No Fun mode.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def funagain(self, ctx, member: discord.Member):
        guild = ctx.guild
        role_name = "No Fun"
        role = discord.utils.get(guild.roles, name=role_name)
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"🎉 {member.mention} has been restored to full fun privileges.")
        else:
            await ctx.send(f"🤔 {member.mention} isn’t in No Fun mode.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def xonfusle(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="xonfusled")
        if not role:
            await ctx.send("The xonfusled role doesn't exist. Please create it manually.")
            return

        try:
            await member.add_roles(role, reason="Temporarily xonfusled")
            await ctx.send(f"{member.mention} has been xonfusled for 15 seconds 😵‍💫")
            await asyncio.sleep(15)
            await member.remove_roles(role, reason="Unxonfusled")
            await ctx.send(f"{member.mention} is no longer xonfusled 🎩")
        except discord.Forbidden:
            await ctx.send("Booper doesn't have permission to assign the xonfusled role.")

    @commands.command()
    async def sudotest(self, ctx, *, command: str):
        await ctx.send(f"Booper would have run `!{command}`… but this is just a test 🤖")

    @commands.command()
    async def sudo(self, ctx, *, command: str):
        parts = command.split()
        if len(parts) == 1:
            await ctx.send(f"Booper is running `!{parts[0]}`…")
            await ctx.invoke(self.bot.get_command(parts[0]))
        elif len(parts) == 2 and parts[1].startswith("<@"):
            action = parts[0]
            target = parts[1]
            await ctx.send(f"{target} has been {action}ed 🎩")
        else:
            cmd_name = parts[0]
            args = " ".join(parts[1:])
            cmd = self.bot.get_command(cmd_name)
            if cmd:
                fake_ctx = await self.bot.get_context(ctx.message)
                fake_ctx.message.content = f"!{cmd_name} {args}"
                await self.bot.invoke(cmd, *args.split())

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
