import random
import asyncio
import discord
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def crowley(self, ctx):
        quotes = [
            "Saitama solos Goku with one sneeze 💨",
            "Naruto is just anime Harry Potter 🧙‍♂️🍜",
            "Zoro could beat Levi blindfolded and drunk 🗡️🍷",
            "Luffy > Superman. Don’t @ me 🦸‍♂️🧢",
            "Gojo is just Kakashi with better skincare 💅",
            "Deku cries more than Tanjiro and Shinji combined 😭",
            "Ichigo is the most forgettable main character ever 🧼",
            "Madara solos the entire MCU with one eye 👁️🔥",
            "Eren did nothing wrong. Actually. 🐺",
            "Dragon Ball GT > Dragon Ball Super. I said what I said 🐉"
        ]
        await ctx.send(random.choice(quotes))

    @commands.command()
    async def waffow(self, ctx):
        await ctx.send("DID I HEAR THAT RIGHT??? TWO TIME??? AS IN TWO TIME FROM THE HIT GAME FORSAKEN WHAT OH MY SPAWN...")

    @commands.command()
    async def jd(self, ctx):
        await ctx.send("If u have a user named after a food and a fast food place gtfo")

    @commands.command()
    async def engi(self, ctx):
        await ctx.send("YOURE a retard! And YOURE a retard! EVERYONES A RETARD!")

    @commands.command()
    async def wAffLes(self, ctx):
        await ctx.send("pushin shut up")

    @commands.command()
    async def zleepy(self, ctx):
        await ctx.send("https://tenor.com/view/guts-hood-berserk-1997-gif-27601744")

    @commands.command()
    async def banans(self, ctx):
        await ctx.send("Real love isnt easy, easy love isnt real. If you don't have love, sucks to suck")

    @commands.command()
    async def llama(self, ctx):
        visible_members = [
            m for m in ctx.guild.members
            if not m.bot and ctx.channel.permissions_for(m).read_messages
        ]
        if not visible_members:
            await ctx.send("🦙 The Llama sees no one worthy.")
            return
        chosen = random.choice(visible_members)
        await ctx.send(f"🦙 The Llama has spoken.\n{chosen.mention}, your fate is uncertain...")

    @commands.command()
    async def vital(self, ctx):
        quotes = [
            "Vital's house burned down successfully",
            "Vital has been yeeted into the sun ",
            "Vital is now a potato ",
            "Vital has been turned into a llama ",
            "Vital is banned from Discord ",
            "Vital died succesfully",
            "Vital blown up successfully ",
        ]
        await ctx.send(random.choice(quotes))

    @commands.command()
    async def goose(self, ctx):
        await ctx.send("Eminem")

    @commands.command()
    async def woopi(self, ctx):
        await ctx.send("I love boobies")

    @commands.command()
    async def flami(self, ctx):
        await ctx.send("idk")

    @commands.command()
    async def lebron(self, ctx):
        gifs = [
            "https://tenor.com/view/lebron-james-dunk-nba-basketball-sports-gif-26475833",
            "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379086",
            "https://tenor.com/view/lebron-james-lakers-nba-basketball-gif-26379087",
            "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379088",
            "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379089",
            "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379090",
        ]
        await ctx.send(random.choice(gifs))

    @commands.command()
    async def braincell(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        count = random.randint(0, 100)
        await ctx.send(f"🧠 {target.mention} has {count} braincells today.")

    @commands.command()
    async def frogify(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        await ctx.send(f"🐸 {target.mention} has been frogified. Ribbit.")

    @commands.command()
    async def fortune(self, ctx):
        outcomes = [
            "You trip over your own ego.",
            "You gain +3 charisma but lose your wallet.",
            "You summon a duck army.",
            "You become invisible but only to cats.",
            "You now speak only in riddles.",
        ]
        await ctx.send(f"🎲 {random.choice(outcomes)}")

    @commands.command()
    async def juice(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        juices = ["Apple", "Orange", "Grape", "Cursed Beetroot", "Quantum Mango"]
        await ctx.send(f"🧃 {target.mention} receives a glass of {random.choice(juices)} juice.")

    @commands.command()
    async def explode(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        await ctx.send(f"💣 {target.mention} has been armed. Explosion in 5 seconds...")

        await asyncio.sleep(1)
        await ctx.send("⏳ 4...")
        await asyncio.sleep(1)
        await ctx.send("⏳ 3...")
        await asyncio.sleep(1)
        await ctx.send("⏳ 2...")
        await asyncio.sleep(1)
        await ctx.send("⏳ 1...")
        await asyncio.sleep(1)

        explosions = [
            "💥 Kaboom! Nothing remains but pixels.",
            "🔥 A glorious detonation. The server trembles.",
            "🎆 That was beautiful. And destructive.",
            "🧨 Boomers",
            "🚀 They’ve been launched into orbit.",
        ]
        await ctx.send(f"{target.mention} {random.choice(explosions)}")

    @commands.command()
    async def defuse(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        outcome = random.choice(["success", "fail"])

        if outcome == "success":
            await ctx.send(f"🧯 {target.mention} has survived by throwing the bomb at Vital. YIPEEE!")
        else:
            await ctx.send(f"💥 {target.mention} cut the wrong wire. Explosion triggered anyway.")

    @commands.command()
    async def pookie(self, ctx):
        await ctx.send("zen ᴡɪʟʟ ꜱᴡɪɴɢ his ʙᴀʟʟꜱ ᴀᴄʀᴏꜱꜱ ʏᴏ ꜰᴀᴄᴇ ʟɪᴋᴇ ᴀ ɢʀᴀɴᴅꜰᴀᴛʜᴇʀ ᴄʟᴏᴄᴋ...")

    @commands.command()
    async def revive(self, ctx):
        prompts = [
            "If you could teleport anywhere right now, where would you go and why?",
            "What’s a weird food combo you secretly love?",
            "What’s the most unhinged thing you’ve ever seen in this server?",
            "If you were a villain, what would your evil plan be?",
            "What’s a hill you’ll die on, no matter how unpopular?",
            "What’s your go-to comfort show or game?",
            "If you had to swap lives with a fictional character for a day, who would it be?",
            "What’s a conspiracy theory you *kinda* believe?",
            "What’s your most cursed hot take?",
            "What’s something you believed as a kid that turned out to be hilariously wrong?",
        ]
        await ctx.send(random.choice(prompts))

    @commands.command()
    async def vzium(self, ctx):
        await ctx.send("you guys ever buy one of those drink hats then connect the tube to ur ass...")

    @commands.command()
    async def city(self, ctx):
        await ctx.send("What if one day you decided to decapitate a person and then put his head in a toilet...")

    @commands.command()
    async def barin(self, ctx):
        print("botmove command registered")
        await ctx.send("The kids you beat up, come and go, but friends... friends are forever")

    @commands.command()
    async def pushin(self, ctx):
        await ctx.send("I got sunshine in a bag, noodle i would smash 🔥🔥🔥🔥🔥")

    @commands.command()
    async def spike(self, ctx):
        await ctx.send("pretend nothings here")

    @commands.command()
    async def spaghettiapple(self, ctx):
        await ctx.send("Pizza Banana!")
    @commands.command()
    async def mashallah(self, ctx):
        await ctx.send("very halal")
    @commands.command()
    async def anwar(self, ctx):
            await ctx.send("yeah ik that guy hes very haram")
    @commands.command()
    async def yanis(self, ctx):
            await ctx.send("idir is geeked")
    @commands.command()
    async def shaan(self, ctx):
            await ctx.send("OMG OMG OMG OMG SHAAN HES MY HERO AND MY GOAT AND HES SO SMART AND HES SO HANDSOME AND HES SO FUNNY I LOVE SHAAN I WISH I CAN GET HIS AUTOGRAPH 🔥")
    @commands.command()
    async def ben(self, ctx):
            await ctx.send("https://giphy.com/gifs/DIIOBGixFnxKeTFwYD")
async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))
