
  import time
import random
import discord
from discord.ext import commands
from .utils import database as db


class Economy(commands.Cog):
    # -----------------------------
    # Constants / Config
    # -----------------------------
    DAILY_AMOUNT = 250
    WEEKLY_AMOUNT = 2000
    WORK_MIN = 50
    WORK_MAX = 150

    DAILY_COOLDOWN = 60 * 60 * 24        # 24 hours
    WEEKLY_COOLDOWN = 60 * 60 * 24 * 7   # 7 days
    WORK_COOLDOWN = 60 * 60              # 1 hour

    # Job definitions
    JOBS = {
        "beggar": {
            "base_pay": 50,
            "max_level": 3,
            "promotion_cost": 200
        },
        "cashier": {
            "base_pay": 120,
            "max_level": 5,
            "promotion_cost": 500
        },
        "miner": {
            "base_pay": 200,
            "max_level": 7,
            "promotion_cost": 900
        },
        "programmer": {
            "base_pay": 350,
            "max_level": 10,
            "promotion_cost": 1500
        }
    }

    # Simple investment assets (in-memory prices)
    INVEST_ASSETS = {
        "boopcoin": 100,
        "waffle": 250,
        "starlight": 500
    }

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        db.init_db()  # ensures tables exist

    # -----------------------------
    # Helper functions
    # -----------------------------
    def _get_timestamp(self, user_id: int, field: str):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(f"SELECT {field} FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return row[field] if row else None

    def _set_timestamp(self, user_id: int, field: str, value: int):
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            f"UPDATE users SET {field} = ? WHERE user_id = ?",
            (value, user_id),
        )
        conn.commit()
        conn.close()

    # -----------------------------
    # Balance / Bank
    # -----------------------------
    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        """Check your or someone else's balance."""
        member = member or ctx.author
        db.ensure_user(member.id)
        wallet, bank = db.get_balance(member.id)

        embed = discord.Embed(
            title=f"{member.display_name}'s Balance",
            color=discord.Color.gold()
        )
        embed.add_field(name="Wallet", value=f"{wallet} 🪙")
        embed.add_field(name="Bank", value=f"{bank} 🏦")
        embed.add_field(name="Net Worth", value=f"{wallet + bank} 💰", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="deposit", aliases=["dep"])
    async def deposit(self, ctx, amount: int):
        """Deposit money from wallet to bank."""
        db.ensure_user(ctx.author.id)
        wallet, bank = db.get_balance(ctx.author.id)

        if amount <= 0:
            return await ctx.send("Enter a positive amount.")
        if amount > wallet:
            return await ctx.send("You don't have that much in your wallet.")

        db.change_wallet(ctx.author.id, -amount)
        db.change_bank(ctx.author.id, amount)

        await ctx.send(f"Deposited {amount} 🪙 into your bank.")

    @commands.command(name="withdraw", aliases=["with"])
    async def withdraw(self, ctx, amount: int):
        """Withdraw money from bank to wallet."""
        db.ensure_user(ctx.author.id)
        wallet, bank = db.get_balance(ctx.author.id)

        if amount <= 0:
            return await ctx.send("Enter a positive amount.")
        if amount > bank:
            return await ctx.send("You don't have that much in your bank.")

        db.change_bank(ctx.author.id, -amount)
        db.change_wallet(ctx.author.id, amount)

        await ctx.send(f"Withdrew {amount} 🪙 into your wallet.")

    # -----------------------------
    # Daily / Weekly
    # -----------------------------
    @commands.command()
    async def daily(self, ctx):
        """Claim your daily reward."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        now = int(time.time())
        last = self._get_timestamp(user_id, "last_daily")

        if last is not None and now - last < self.DAILY_COOLDOWN:
            remaining = self.DAILY_COOLDOWN - (now - last)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            return await ctx.send(
                f"You already claimed your daily. Try again in {hours}h {minutes}m."
            )

        db.change_wallet(user_id, self.DAILY_AMOUNT)
        self._set_timestamp(user_id, "last_daily", now)

        await ctx.send(f"You claimed your daily {self.DAILY_AMOUNT} 🪙!")

    @commands.command()
    async def weekly(self, ctx):
        """Claim your weekly reward."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        now = int(time.time())
        last = self._get_timestamp(user_id, "last_weekly")

        if last is not None and now - last < self.WEEKLY_COOLDOWN:
            remaining = self.WEEKLY_COOLDOWN - (now - last)
            days = remaining // 86400
            hours = (remaining % 86400) // 3600
            return await ctx.send(
                f"You already claimed your weekly. Try again in {days}d {hours}h."
            )

        db.change_wallet(user_id, self.WEEKLY_AMOUNT)
        self._set_timestamp(user_id, "last_weekly", now)

        await ctx.send(f"You claimed your weekly {self.WEEKLY_AMOUNT} 🪙!")

    # -----------------------------
    # Basic Work Command
    # -----------------------------
    @commands.command()
    async def work(self, ctx):
        """Work and earn money (1 hour cooldown)."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        now = int(time.time())

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT last_used FROM cooldowns WHERE user_id = ? AND command = ?",
            (user_id, "work"),
        )
        row = cur.fetchone()

        if row is not None:
            last_used = row["last_used"]
            if now - last_used < self.WORK_COOLDOWN:
                remaining = self.WORK_COOLDOWN - (now - last_used)
                minutes = remaining // 60
                seconds = remaining % 60
                conn.close()
                return await ctx.send(
                    f"You are tired. Try working again in {minutes}m {seconds}s."
                )

        amount = random.randint(self.WORK_MIN, self.WORK_MAX)
        db.change_wallet(user_id, amount)

        if row is None:
            cur.execute(
                "INSERT INTO cooldowns (user_id, command, last_used) VALUES (?, ?, ?)",
                (user_id, "work", now),
            )
        else:
            cur.execute(
                "UPDATE cooldowns SET last_used = ? WHERE user_id = ? AND command = ?",
                (now, user_id, "work"),
            )

        conn.commit()
        conn.close()

        await ctx.send(f"You worked and earned {amount} 🪙!")

    # -----------------------------
    # Jobs / Promotions
    # -----------------------------
    @commands.command()
    async def jobs(self, ctx):
        """List available jobs."""
        embed = discord.Embed(title="Available Jobs", color=discord.Color.blue())

        for job, data in self.JOBS.items():
            embed.add_field(
                name=job.capitalize(),
                value=f"Base Pay: {data['base_pay']} 🪙\nMax Level: {data['max_level']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def apply(self, ctx, job: str):
        """Apply for a job."""
        job = job.lower()

        if job not in self.JOBS:
            return await ctx.send("❌ That job does not exist.")

        user_id = ctx.author.id
        db.ensure_user(user_id)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET job = ?, job_level = 1 WHERE user_id = ?", (job, user_id))
        conn.commit()
        conn.close()

        await ctx.send(f"✅ You are now a **Level 1 {job.capitalize()}**!")

    @commands.command()
    async def promote(self, ctx):
        """Promote your job level (costs money)."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT job, job_level FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()

        job = row["job"] if row else None
        level = row["job_level"] if row else 1

        if job is None:
            return await ctx.send("❌ You don't have a job. Use `!apply <job>` first.")

        job_data = self.JOBS[job]

        if level >= job_data["max_level"]:
            return await ctx.send("⭐ You are already at the **maximum level** for this job.")

        cost = job_data["promotion_cost"] * level
        wallet, bank = db.get_balance(user_id)

        if wallet < cost:
            return await ctx.send(f"❌ You need **{cost} 🪙** to get promoted.")

        db.change_wallet(user_id, -cost)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET job_level = ? WHERE user_id = ?", (level + 1, user_id))
        conn.commit()
        conn.close()

        await ctx.send(
            f"🎉 **Promotion!** You are now a **Level {level + 1} {job.capitalize()}**.\n"
            f"Cost: {cost} 🪙"
        )

    @commands.command()
    async def workjob(self, ctx):
        """Work your job and earn money based on job + level."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT job, job_level FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()

        job = row["job"] if row else None
        level = row["job_level"] if row else 1

        if job is None:
            return await ctx.send("❌ You don't have a job. Use `!apply <job>` first.")

        job_data = self.JOBS[job]
        base = job_data["base_pay"]
        pay = base + (level * 20)

        db.change_wallet(user_id, pay)

        await ctx.send(
            f"💼 You worked as a **Level {level} {job.capitalize()}** and earned **{pay} 🪙**!"
        )

    @commands.command()
    async def quitjob(self, ctx):
        """Quit your current job."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET job = NULL, job_level = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()

        await ctx.send("🛑 You have quit your job.")

    # -----------------------------
    # Casino Commands
    # -----------------------------
    @commands.command(aliases=["cf"])
    async def coinflip(self, ctx, amount: int, choice: str):
        """Bet on a coinflip. Usage: !coinflip <amount> <heads/tails>"""
        user_id = ctx.author.id
        db.ensure_user(user_id)
        choice = choice.lower()

        if choice not in ["heads", "tails"]:
            return await ctx.send("Choose `heads` or `tails`.")

        wallet, bank = db.get_balance(user_id)
        if amount <= 0:
            return await ctx.send("Bet a positive amount.")
        if amount > wallet:
            return await ctx.send("You don't have that much in your wallet.")

        result = random.choice(["heads", "tails"])

        if result == choice:
            db.change_wallet(user_id, amount)
            await ctx.send(f"🪙 The coin landed on **{result}**. You **won {amount}**!")
        else:
            db.change_wallet(user_id, -amount)
            await ctx.send(f"🪙 The coin landed on **{result}**. You **lost {amount}**...")

    @commands.command()
    async def dice(self, ctx, amount: int):
        """Roll dice vs Booper. Higher roll wins. Usage: !dice <amount>"""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        wallet, bank = db.get_balance(user_id)
        if amount <= 0:
            return await ctx.send("Bet a positive amount.")
        if amount > wallet:
            return await ctx.send("You don't have that much in your wallet.")

        user_roll = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if user_roll > bot_roll:
            db.change_wallet(user_id, amount)
            await ctx.send(
                f"🎲 You rolled **{user_roll}**, Booper rolled **{bot_roll}**.\n"
                f"You **won {amount} 🪙**!"
            )
        elif user_roll < bot_roll:
            db.change_wallet(user_id, -amount)
            await ctx.send(
                f"🎲 You rolled **{user_roll}**, Booper rolled **{bot_roll}**.\n"
                f"You **lost {amount} 🪙**..."
            )
        else:
            await ctx.send(
                f"🎲 You rolled **{user_roll}**, Booper rolled **{bot_roll}**.\n"
                f"It's a **tie**. No money lost."
            )

    @commands.command()
    async def slots(self, ctx, amount: int):
        """Play slots. Usage: !slots <amount>"""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        wallet, bank = db.get_balance(user_id)
        if amount <= 0:
            return await ctx.send("Bet a positive amount.")
        if amount > wallet:
            return await ctx.send("You don't have that much in your wallet.")

        symbols = ["🍒", "🍋", "🍉", "⭐", "7️⃣"]
        roll = [random.choice(symbols) for _ in range(3)]

        await ctx.send(f"🎰 {' | '.join(roll)}")

        if roll[0] == roll[1] == roll[2]:
            winnings = amount * 5
            db.change_wallet(user_id, winnings)
            await ctx.send(f"JACKPOT! You won **{winnings} 🪙**!")
        elif roll[0] == roll[1] or roll[1] == roll[2] or roll[0] == roll[2]:
            winnings = amount * 2
            db.change_wallet(user_id, winnings)
            await ctx.send(f"Nice! You won **{winnings} 🪙**!")
        else:
            db.change_wallet(user_id, -amount)
            await ctx.send(f"No match. You lost **{amount} 🪙**.")

    # -----------------------------
    # Leaderboards
    # -----------------------------
    @commands.command(aliases=["lb"])
    async def leaderboard(self, ctx, category: str = "money"):
        """Show leaderboards. Usage: !leaderboard [money/bank/net]"""
        category = category.lower()
        valid = ["money", "bank", "net"]
        if category not in valid:
            return await ctx.send("Choose one of: `money`, `bank`, `net`.")

        conn = db.get_connection()
        cur = conn.cursor()

        if category == "money":
            cur.execute("SELECT user_id, wallet, bank FROM users ORDER BY wallet DESC LIMIT 10")
            title = "Top Wallet Balances"
        elif category == "bank":
            cur.execute("SELECT user_id, wallet, bank FROM users ORDER BY bank DESC LIMIT 10")
            title = "Top Bank Balances"
        else:
            cur.execute("SELECT user_id, wallet, bank FROM users")
            rows = cur.fetchall()
            rows = sorted(rows, key=lambda r: r["wallet"] + r["bank"], reverse=True)[:10]
            conn.close()

            embed = discord.Embed(title="Top Net Worth", color=discord.Color.gold())
            for idx, row in enumerate(rows, start=1):
                member = ctx.guild.get_member(row["user_id"])
                name = member.display_name if member else f"User {row['user_id']}"
                net = row["wallet"] + row["bank"]
                embed.add_field(
                    name=f"#{idx} {name}",
                    value=f"Net Worth: {net} 💰",
                    inline=False
                )
            return await ctx.send(embed=embed)

        rows = cur.fetchall()
        conn.close()

        embed = discord.Embed(title=title, color=discord.Color.gold())
        for idx, row in enumerate(rows, start=1):
            member = ctx.guild.get_member(row["user_id"])
            name = member.display_name if member else f"User {row['user_id']}"
            wallet = row["wallet"]
            bank = row["bank"]
            net = wallet + bank
            embed.add_field(
                name=f"#{idx} {name}",
                value=f"Wallet: {wallet} 🪙 | Bank: {bank} 🏦 | Net: {net} 💰",
                inline=False
            )

        await ctx.send(embed=embed)

    # -----------------------------
    # Extra Work Commands
    # -----------------------------
    @commands.command()
    async def beg(self, ctx):
        """Beg for some coins."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        amount = random.randint(5, 50)
        db.change_wallet(user_id, amount)

        await ctx.send(f"🧎 You begged and received **{amount} 🪙**.")

    @commands.command()
    async def crime(self, ctx):
        """Commit a crime. High risk, high reward."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        wallet, bank = db.get_balance(user_id)
        if wallet <= 0:
            return await ctx.send("You have nothing to risk.")

        if random.random() < 0.4:
            loss = random.randint(20, min(200, wallet))
            db.change_wallet(user_id, -loss)
            await ctx.send(f"🚓 You got caught and lost **{loss} 🪙** in fines.")
        else:
            gain = random.randint(100, 400)
            db.change_wallet(user_id, gain)
            await ctx.send(f"🕵️ You pulled it off and gained **{gain} 🪙**!")

    @commands.command()
    async def hunt(self, ctx):
        """Go hunting for some rewards."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        amount = random.randint(80, 200)
        db.change_wallet(user_id, amount)

        await ctx.send(f"🏹 You went hunting and earned **{amount} 🪙**.")

    @commands.command()
    async def mine(self, ctx):
        """Mine for resources and money."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        amount = random.randint(120, 300)
        db.change_wallet(user_id, amount)

        await ctx.send(f"⛏️ You mined and earned **{amount} 🪙**.")

    # -----------------------------
    # Investments
    # -----------------------------
    @commands.command()
    async def market(self, ctx):
        """Show available investment assets and their prices."""
        embed = discord.Embed(title="Investment Market", color=discord.Color.green())
        for asset, price in self.INVEST_ASSETS.items():
            embed.add_field(
                name=asset.capitalize(),
                value=f"Price: {price} 🪙 per unit",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command()
    async def investbuy(self, ctx, asset: str, amount: int):
        """Buy investment assets. Usage: !investbuy <asset> <amount>"""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        asset = asset.lower()
        if asset not in self.INVEST_ASSETS:
            return await ctx.send("That asset does not exist. Use `!market` to see options.")

        if amount <= 0:
            return await ctx.send("Buy a positive amount.")

        price = self.INVEST_ASSETS[asset]
        cost = price * amount

        wallet, bank = db.get_balance(user_id)
        if cost > wallet:
            return await ctx.send(f"You need **{cost} 🪙**, but only have **{wallet} 🪙** in your wallet.")

        db.change_wallet(user_id, -cost)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO investments (user_id, asset, amount) VALUES (?, ?, ?) "
            "ON CONFLICT(user_id, asset) DO UPDATE SET amount = amount + ?",
            (user_id, asset, amount, amount)
        )
        conn.commit()
        conn.close()

        await ctx.send(f"📈 You bought **{amount} {asset.capitalize()}** for **{cost} 🪙**.")

    @commands.command()
    async def investsell(self, ctx, asset: str, amount: int):
        """Sell investment assets. Usage: !investsell <asset> <amount>"""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        asset = asset.lower()
        if asset not in self.INVEST_ASSETS:
            return await ctx.send("That asset does not exist. Use `!market` to see options.")

        if amount <= 0:
            return await ctx.send("Sell a positive amount.")

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT amount FROM investments WHERE user_id = ? AND asset = ?",
            (user_id, asset)
        )
        row = cur.fetchone()

        if row is None or row["amount"] < amount:
            conn.close()
            return await ctx.send("You don't own that much of this asset.")

        price = self.INVEST_ASSETS[asset]
        revenue = price * amount

        new_amount = row["amount"] - amount
        if new_amount == 0:
            cur.execute(
                "DELETE FROM investments WHERE user_id = ? AND asset = ?",
                (user_id, asset)
            )
        else:
            cur.execute(
                "UPDATE investments SET amount = ? WHERE user_id = ? AND asset = ?",
                (new_amount, user_id, asset)
            )

        conn.commit()
        conn.close()

        db.change_wallet(user_id, revenue)

        await ctx.send(f"📉 You sold **{amount} {asset.capitalize()}** for **{revenue} 🪙**.")

    @commands.command()
    async def portfolio(self, ctx):
        """View your investment portfolio."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT asset, amount FROM investments WHERE user_id = ?",
            (user_id,)
        )
        rows = cur.fetchall()
        conn.close()

        if not rows:
            return await ctx.send("You don't have any investments yet.")

        embed = discord.Embed(
            title=f"{ctx.author.display_name}'s Portfolio",
            color=discord.Color.green()
        )

        total_value = 0
        for row in rows:
            asset = row["asset"]
            amount = row["amount"]
            price = self.INVEST_ASSETS.get(asset, 0)
            value = price * amount
            total_value += value

            embed.add_field(
                name=asset.capitalize(),
                value=f"Amount: {amount}\nPrice: {price} 🪙\nValue: {value} 🪙",
                inline=False
            )

        embed.add_field(
            name="Total Portfolio Value",
            value=f"{total_value} 🪙",
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
