import discord
from discord.ext import commands
import random
import re
import asyncio
import os
import chess
from dotenv import load_dotenv
load_dotenv()
print("✅ .env loaded")
token = os.getenv("DISCORD_TOKEN")
active_games = {}  # key: challenger_id, value: {'board': chess.Board(), 'white': user_id, 'black': opponent_id, 'turn': 'white'}
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hey random citizen! 🎉 Your bot is working!')
@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

@bot.command()
async def greet(ctx):
    await ctx.send(f"Hello {ctx.author.name}, hope you're having an awesome day!")
@bot.command()
async def waffle(ctx, member: discord.Member):
    try:
        await member.edit(nick="waffle")
        await ctx.send(f"{member.mention} is now known as waffle 🧇")
    except discord.Forbidden:
        await ctx.send("I don't have permission to change that user's nickname.")
    except discord.HTTPException:
        await ctx.send("Something went wrong while trying to change the nickname.")
@bot.command()
async def unwaffle(ctx, member: discord.Member):
    try:
        await member.edit(nick=None)
        await ctx.send(f"{member.mention} is no longer a waffle 🧇")
    except discord.Forbidden:
        await ctx.send("I don't have permission to change that user's nickname.")
    except discord.HTTPException:
        await ctx.send("Something went wrong while trying to reset the nickname.")
@bot.command()
async def wisdom(ctx):
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
@bot.command()
async def crowley(ctx):
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
@bot.command()
async def waffow(ctx):
    await ctx.send("DID I HEAR THAT RIGHT??? TWO TIME??? AS IN TWO TIME FROM THE HIT GAME FORSAKEN WHAT OH MY SPAWN OH MY SPAWN. I . LOVE TWO TIME SO MUCH I AM DOWNRIGHT INSANE FOR THEM MY OBSESSION WITH TWO TIME 222IS EXTREMELY CONCERNING AND MIGHT BE ENOUGH TO PUT ME IN A PSYCH WARD BUT THAT'S OKAY BECAUSE EVERYTHING IS A TWO TIME REFERENCE TRUST 😎😎I LOVE THEM LIKE MY CHILD I LOVE THEM EVERYDAY THEY ARE MY ENTIRE LIFE PURPOSE IF THEY WERE TO BE DELETED I WOULD PROBABALY GO INSANE😵😵😵AND KILLMYSELF 😂😂😂😂I LOVE TWO TIME I LOVE TWO TIME I LOVE TWO TIMETWOTIMETWOTIMETWOTIME")
@bot.command()
async def jd(ctx):
    await ctx.send("If u have a user named after a food and a fast food place gtfo")
@bot.command()
async def engi(ctx):
    await ctx.send("YOURE a retard! And YOURE a retard! EVERYONES A RETARD!")
@bot.command()
async def wAffLes(ctx):
    await ctx.send("pushin shut up")

@bot.command()
async def ayan(ctx, *, question: str):
    # Try to detect and solve simple math expressions
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
        # If it's not math, respond with a goofy reply
        responses = [
            f"Ayan says: '{question}' is a mystery even to the gods.",
            f"Ayan says: I would answer, but that would break the simulation.",
            f"Ayan says: Ask again when the moon is full.",
            f"Ayan says: I know the answer, but I'm not telling 😏"
        ]
        import random
        await ctx.send(random.choice(responses))
@bot.command()
async def boop(ctx, member: discord.Member, *, duration: str):
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
@bot.command()
async def zleepy(ctx):
    await ctx.send("https://tenor.com/view/guts-hood-berserk-1997-gif-27601744")
@bot.command()
async def banans(ctx):
    await ctx.send("Real love isnt easy, easy love isnt real. If you don't have love, sucks to suck")
@bot.command()
async def llama(ctx):
    visible_members = [
        m for m in ctx.guild.members
        if not m.bot and ctx.channel.permissions_for(m).read_messages
    ]

    if not visible_members:
        await ctx.send("🦙 The Llama sees no one worthy.")
        return

    chosen = random.choice(visible_members)
    await ctx.send(f"🦙 The Llama has spoken.\n{chosen.mention}, your fate is uncertain...")
@bot.command()
async def vital(ctx):
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
@bot.command()
async def goose(ctx):
    await ctx.send("Eminem")
@bot.command()
async def woopi(ctx):
    await ctx.send("I love boobies")
@bot.command()
async def flami(ctx):
    await ctx.send("idk")
@bot.command()
async def lebron(ctx):
    gifs = [
        "https://tenor.com/view/lebron-james-dunk-nba-basketball-sports-gif-26475833",
        "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379086",
        "https://tenor.com/view/lebron-james-lakers-nba-basketball-gif-26379087",
        "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379088",
        "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379089",
        "https://tenor.com/view/lebron-james-nba-lakers-basketball-gif-26379090",
    ]
    await ctx.send(random.choice(gifs))
@bot.command()
async def braincell(ctx, member: discord.Member = None):
    target = member or ctx.author
    count = random.randint(0, 100)
    await ctx.send(f"🧠 {target.mention} has {count} braincells today.")
@bot.command()
async def frogify(ctx, member: discord.Member = None):
    target = member or ctx.author
    await ctx.send(f"🐸 {target.mention} has been frogified. Ribbit.")
@bot.command()
async def dice(ctx):
    outcomes = [
        "You trip over your own ego.",
        "You gain +3 charisma but lose your wallet.",
        "You summon a duck army.",
        "You become invisible but only to cats.",
        "You now speak only in riddles.",
    ]
    await ctx.send(f"🎲 {random.choice(outcomes)}")
@bot.command()
async def juice(ctx, member: discord.Member = None):
    target = member or ctx.author
    juices = ["Apple", "Orange", "Grape", "Cursed Beetroot", "Quantum Mango"]
    await ctx.send(f"🧃 {target.mention} receives a glass of {random.choice(juices)} juice.")
@bot.command()
async def explode(ctx, member: discord.Member = None):
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
@bot.command()
async def defuse(ctx, member: discord.Member = None):
    target = member or ctx.author
    outcome = random.choice(["success", "fail"])

    if outcome == "success":
        await ctx.send(f"🧯 {target.mention} has survived by throwing the bomb at Vital. YIPEEE!")
    else:
        await ctx.send(f"💥 {target.mention} cut the wrong wire. Explosion triggered anyway.")
@bot.command()
async def pookie(ctx):
    await ctx.send("zen ᴡɪʟʟ ꜱᴡɪɴɢ his ʙᴀʟʟꜱ ᴀᴄʀᴏꜱꜱ ʏᴏ ꜰᴀᴄᴇ ʟɪᴋᴇ ᴀ ɢʀᴀɴᴅꜰᴀᴛʜᴇʀ ᴄʟᴏᴄᴋ 🕰️🙏🏻 ᴅᴏɴ’ᴛ ᴇᴠᴇʀ ʟᴇᴛ him ᴄᴀᴛᴄʜ ᴜ yapping ᴀɢᴀɪɴ ʟɪʟ ʙʀᴏ💯🔥😭")
@bot.command()
async def revive(ctx):
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
    await ctx.send("{random.choice(prompts)}")
@bot.command()
async def vzium(ctx):
    await ctx.send("you guys ever buy one of those drink hats then connect the tube to ur ass and start shitting out diarrhea to drink it")
@bot.command()
async def city(ctx):
    await ctx.send("What if one day you decided to decapitate a person and then put his head in a toilet, will he become a skibidi toilet?")
@bot.command()
@commands.has_permissions(manage_roles=True)
async def nofun(ctx, member: discord.Member):
    guild = ctx.guild
    role_name = "No Fun"

    # Check if role exists
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        # Create the role with restricted permissions
        role = await guild.create_role(name=role_name, reason="Created by Booper for No Fun mode")

        # Apply role restrictions to all text channels
        for channel in guild.text_channels:
            await channel.set_permissions(role,
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

    # Assign role to the member
    await member.add_roles(role)
    await ctx.send(f"🚫 {member.mention} has been banished to No Fun mode.")
@bot.command()
@commands.has_permissions(manage_roles=True)
async def funagain(ctx, member: discord.Member):
    guild = ctx.guild
    role_name = "No Fun"

    # Find the role
    role = discord.utils.get(guild.roles, name=role_name)
    if role in member.roles:
        await member.remove_roles(role)
        await ctx.send(f"🎉 {member.mention} has been restored to full fun privileges.")
    else:
        await ctx.send(f"🤔 {member.mention} isn’t in No Fun mode.")
@bot.command()
async def barin(ctx):
    print("botmove command registered")
    await ctx.send("The kids you beat up, come and go, but friends... friends are forever")
@bot.command()
async def pushin(ctx):
    await ctx.send("I got sunshine in a bag, noodle i would smash 🔥🔥🔥🔥🔥")
@bot.command()
async def spike(ctx):
    await ctx.send("pretend nothings here")
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)
@bot.command()
@commands.has_permissions(manage_roles=True)
async def xonfusle(ctx, member: discord.Member):
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

@bot.command()
async def rain(ctx):
    await ctx.send("I don’t like coffee; it’s too bitter, but if my beloved Reze makes it, I might drink it, maybe. I mean, when she makes it, she makes it sweet, but even if it’s bitter, I think it’s fine. But coffees are usually bitter, but if I want, I think she’d make it sweet. But I don’t think she knows how to make Turkish coffee because she’s Russian, and why would Russians drink Turkish coffee, am I wrong? I think not, but if I want, she could probably make it. But why would I want Turkish coffee? I think I’d want a much sweeter coffee. But why would she make sweet coffee for me? I think instead of making sweet coffee, she could make tea. But teas become sweet when you add sugar, but I don’t think every tea has to have sugar. So, if I want, she could make the tea sweet, but why would she? I think I could add the sugar myself, but I think sugar is too expensive, so I should drink tea without sugar. But I think tea without sugar isn’t really tea, so I won’t drink tea. That’s why I’d ask my beloved Reze for water.")

@bot.command()
async def sudotest(ctx, *, command: str):
    await ctx.send(f"Booper would have run `!{command}`… but this is just a test 🤖")

@bot.command()
async def sudo(ctx, *, command: str):
    parts = command.split()
    if len(parts) == 1:
        # Just a command name
        await ctx.send(f"Booper is running `!{parts[0]}`…")
        await ctx.invoke(bot.get_command(parts[0]))
    elif len(parts) == 2 and parts[1].startswith("<@"):
        # Action + mention
        action = parts[0]
        target = parts[1]
        await ctx.send(f"{target} has been {action}ed 🎩")
    else:
        # Full command with args
        cmd_name = parts[0]
        args = " ".join(parts[1:])
        cmd = bot.get_command(cmd_name)
        if cmd:
            fake_ctx = await bot.get_context(ctx.message)
            fake_ctx.message.content = f"!{cmd_name} {args}"
            await bot.invoke(cmd, *args.split())
@bot.command()
async def spaghettiapple(ctx):
    await ctx.send("Pizza Banana!")

if __name__ == "__main__":
    print("Booper is booping...")
    bot.run(token)



