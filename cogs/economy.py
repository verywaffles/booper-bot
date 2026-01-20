import time
import random
import discord
from discord.ext import commands
from .utils import database as db

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


class Economy(commands.Cog):
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
        return row[field]

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
    # Balance
    # -----------------------------
    @commands.command(name="balance", aliases=["bal", "money"])
    async def balance(self, ctx, member: discord.Member = None):
        """Check your or someone else's balance."""
        member = member or ctx.author
        wallet, bank = db.get_balance(member.id)

        embed = discord.Embed(
            title=f"{member.display_name}'s Balance",
            color=discord.Color.gold()
        )
        embed.add_field(name="Wallet", value=f"{wallet} 🪙")
        embed.add_field(name="Bank", value=f"{bank} 🏦")
        embed.add_field(name="Net Worth", value=f"{wallet + bank} 💰", inline=False)

        await ctx.send(embed=embed)

    # -----------------------------
    # Deposit
    # -----------------------------
    @commands.command(name="deposit", aliases=["dep"])
    async def deposit(self, ctx, amount: int):
        """Deposit money from wallet to bank."""
        wallet, bank = db.get_balance(ctx.author.id)

        if amount <= 0:
            return await ctx.send("Enter a positive amount.")
        if amount > wallet:
            return await ctx.send("You don't have that much in your wallet.")

        db.change_wallet(ctx.author.id, -amount)
        db.change_bank(ctx.author.id, amount)

        await ctx.send(f"Deposited {amount} 🪙 into your bank.")

    # -----------------------------
    # Withdraw
    # -----------------------------
    @commands.command(name="withdraw", aliases=["with"])
    async def withdraw(self, ctx, amount: int):
        """Withdraw money from bank to wallet."""
        wallet, bank = db.get_balance(ctx.author.id)

        if amount <= 0:
            return await ctx.send("Enter a positive amount.")
        if amount > bank:
            return await ctx.send("You don't have that much in your bank.")

        db.change_bank(ctx.author.id, -amount)
        db.change_wallet(ctx.author.id, amount)

        await ctx.send(f"Withdrew {amount} 🪙 into your wallet.")

    # -----------------------------
    # Daily Reward
    # -----------------------------
    @commands.command()
    async def daily(self, ctx):
        """Claim your daily reward."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        now = int(time.time())
        last = self._get_timestamp(user_id, "last_daily")

        if last is not None and now - last < DAILY_COOLDOWN:
            remaining = DAILY_COOLDOWN - (now - last)
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            return await ctx.send(
                f"You already claimed your daily. Try again in {hours}h {minutes}m."
            )

        db.change_wallet(user_id, DAILY_AMOUNT)
        self._set_timestamp(user_id, "last_daily", now)

        await ctx.send(f"You claimed your daily {DAILY_AMOUNT} 🪙!")

    # -----------------------------
    # Weekly Reward
    # -----------------------------
    @commands.command()
    async def weekly(self, ctx):
        """Claim your weekly reward."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        now = int(time.time())
        last = self._get_timestamp(user_id, "last_weekly")

        if last is not None and now - last < WEEKLY_COOLDOWN:
            remaining = WEEKLY_COOLDOWN - (now - last)
            days = remaining // 86400
            hours = (remaining % 86400) // 3600
            return await ctx.send(
                f"You already claimed your weekly. Try again in {days}d {hours}h."
            )

        db.change_wallet(user_id, WEEKLY_AMOUNT)
        self._set_timestamp(user_id, "last_weekly", now)

        await ctx.send(f"You claimed your weekly {WEEKLY_AMOUNT} 🪙!")

    # -----------------------------
    # Work Command
    # -----------------------------
    @commands.command()
    async def work(self, ctx):
        """Work and earn money (1 hour cooldown)."""
        user_id = ctx.author.id
        db.ensure_user(user_id)

        now = int(time.time())

        # Check cooldown
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT last_used FROM cooldowns WHERE user_id = ? AND command = ?",
            (user_id, "work"),
        )
        row = cur.fetchone()

        if row is not None:
            last_used = row["last_used"]
            if now - last_used < WORK_COOLDOWN:
                remaining = WORK_COOLDOWN - (now - last_used)
                minutes = remaining // 60
                seconds = remaining % 60
                conn.close()
                return await ctx.send(
                    f"You are tired. Try working again in {minutes}m {seconds}s."
                )

        # Pay user
        amount = random.randint(WORK_MIN, WORK_MAX)
        db.change_wallet(user_id, amount)

        # Update cooldown
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

    await ctx.send(embed=embed)
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

    job = row["job"]
    level = row["job_level"]

    if job is None:
        return await ctx.send("❌ You don't have a job. Use `!apply <job>` first.")

    job_data = self.JOBS[job]

    if level >= job_data["max_level"]:
        return await ctx.send("⭐ You are already at the **maximum level** for this job.")

    cost = job_data["promotion_cost"] * level
    wallet, bank = db.get_balance(user_id)

    if wallet < cost:
        return await ctx.send(f"❌ You need **{cost} 🪙** to get promoted.")

    # Deduct cost
    db.change_wallet(user_id, -cost)

    # Promote
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

    job = row["job"]
    level = row["job_level"]

    if job is None:
        return await ctx.send("❌ You don't have a job. Use `!apply <job>` first.")

    job_data = self.JOBS[job]

    # Salary formula
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


async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))
