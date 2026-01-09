import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
from utils.codebuddy_database import DB_PATH
import ast
import operator
import random
import asyncio

class Counting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Cache for counting channels: guild_id -> channel_id
        self.counting_channels = {}

    async def cog_load(self):
        """Load counting channels into memory on startup"""
        try:
            async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
                try:
                    async with db.execute("SELECT guild_id, channel_id FROM counting_config") as cursor:
                        rows = await cursor.fetchall()
                        for guild_id, channel_id in rows:
                            self.counting_channels[guild_id] = channel_id
                    print(f"Loaded {len(self.counting_channels)} counting channels")
                except aiosqlite.OperationalError:
                    print("counting_config table not found during cog load (likely first run)")
        except Exception as e:
            print(f"Error loading counting channels: {e}")

    @app_commands.command(name="setcountingchannel", description="Set the channel for the counting game")
    @app_commands.checks.has_permissions(administrator=True)
    async def setcountingchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
            await db.execute("""
                INSERT INTO counting_config (guild_id, channel_id)
                VALUES (?, ?)
                ON CONFLICT(guild_id) DO UPDATE SET channel_id = excluded.channel_id
            """, (interaction.guild_id, channel.id))
            await db.commit()
        
        # Update cache
        self.counting_channels[interaction.guild_id] = channel.id
        
        await interaction.response.send_message(f"Counting channel set to {channel.mention}", ephemeral=True)

    def safe_eval(self, expr):
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.BitXor: operator.pow, # Allow ^ for power
            ast.USub: operator.neg
        }

        def eval_node(node):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    return node.value
                raise TypeError("Not a number")
            elif isinstance(node, ast.BinOp):
                op = type(node.op)
                if op in operators:
                    left = eval_node(node.left)
                    right = eval_node(node.right)
                    if op in (ast.Pow, ast.BitXor):
                        if right > 100: # Limit exponent
                            raise ValueError("Exponent too large")
                    return operators[op](left, right)
            elif isinstance(node, ast.UnaryOp):
                op = type(node.op)
                if op in operators:
                    return operators[op](eval_node(node.operand))
            raise TypeError("Unsupported type")

        try:
            tree = ast.parse(expr, mode='eval')
            return eval_node(tree.body)
        except Exception:
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        # 1. OPTIMIZATION: Check cache first before touching DB
        if message.guild.id not in self.counting_channels:
            return
        
        if message.channel.id != self.counting_channels[message.guild.id]:
            return

        # 2. Process the message logic
        # Wrap DB operations in retry loop for robustness
        retries = 3
        while retries > 0:
            try:
                async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
                    async with db.execute("SELECT current_count, last_user_id, high_score FROM counting_config WHERE guild_id = ?", (message.guild.id,)) as cursor:
                        config = await cursor.fetchone()
                    
                    if not config:
                        # Should not happen if in cache, but possible if DB was manually cleared
                        return

                    current_count, last_user_id, high_score = config

                    # Try to parse the number
                    content = message.content.strip()
                    if not content:
                        return

                    # Evaluate math expression
                    number = self.safe_eval(content)
                    if number is None:
                        return # Not a valid number/expression

                    # Check if it's an integer
                    if isinstance(number, float):
                        if number.is_integer():
                            number = int(number)
                        else:
                            # Not an int, ignore
                            return

                    # Check rules
                    next_count = current_count + 1
                    
                    if number != next_count:
                        await self.fail_count(message, current_count, "Wrong number!")
                        return

                    if message.author.id == last_user_id:
                        await self.fail_count(message, current_count, "You can't count twice in a row!")
                        return

                    # Valid count - Update DB
                    await message.add_reaction("✅")
                    new_high_score = max(high_score, next_count)
                    
                    # Update configuration tables
                    await db.execute("""
                        UPDATE counting_config 
                        SET current_count = ?, last_user_id = ?, high_score = ?
                        WHERE guild_id = ?
                    """, (next_count, message.author.id, new_high_score, message.guild.id))
                    
                    # Update user stats
                    await db.execute("""
                        INSERT INTO counting_stats (user_id, guild_id, total_counts, ruined_counts)
                        VALUES (?, ?, 1, 0)
                        ON CONFLICT(user_id, guild_id) DO UPDATE SET total_counts = total_counts + 1
                    """, (message.author.id, message.guild.id))
                    
                    await db.commit()
                    return # Success
            
            except aiosqlite.OperationalError as e:
                # If specifically locked, retry
                if "locked" in str(e):
                    retries -= 1
                    if retries == 0:
                        print(f"Database locked repeatedly in counting for msg {message.id}")
                        # Don't crash bot, just ignore or log
                        return
                    await asyncio.sleep(0.1 * (4 - retries)) # backoff
                else:
                    raise # Re-raise other operational errors

    async def fail_count(self, message, current_count, reason):
        # 1. Send initial message
        await message.add_reaction("❌")
        status_msg = await message.channel.send(
            f"{reason} {message.author.mention} messed up at {current_count}!\n"
            "🎲 **Rolling the Dice of Fate...**\n"
            "React with 🎲 to help roll! (Need 2 reactions in 60s)"
        )
        await status_msg.add_reaction("🎲")

        # 2. Wait for reactions
        reactions_collected = False
        try:
            end_time = asyncio.get_event_loop().time() + 60
            while True:
                # Check current count
                status_msg = await message.channel.fetch_message(status_msg.id)
                reaction = discord.utils.get(status_msg.reactions, emoji="🎲")
                
                # If bot reacted, count is at least 1. We need 2 total.
                if reaction and reaction.count >= 2:
                    reactions_collected = True
                    break
                
                timeout = end_time - asyncio.get_event_loop().time()
                if timeout <= 0:
                    break
                
                try:
                    # Wait for any reaction on this message
                    await self.bot.wait_for(
                        'reaction_add', 
                        check=lambda r, u: r.message.id == status_msg.id and str(r.emoji) == "🎲", 
                        timeout=timeout
                    )
                except asyncio.TimeoutError:
                    break
        except Exception:
            pass # Proceed if something fails

        # 3. Determine Outcome
        outcome_msg = ""
        new_count = 0
        new_last_user_id = None
        
        dice_db_ops = [] # List of DB operations to perform (query, args)

        if not reactions_collected:
            # TIMEOUT / NOT ENOUGH REACTIONS -> RESET
            new_count = 0
            new_last_user_id = None
            outcome_msg = "⏳ **Time's up!** Not enough people helped roll the dice.\n💥 **Reset!** The count goes back to 0."
            
            dice_db_ops.append(("""
                UPDATE counting_config 
                SET current_count = 0, last_user_id = NULL
                WHERE guild_id = ?
            """, (message.guild.id,)))

            dice_db_ops.append(("""
                INSERT INTO counting_stats (user_id, guild_id, total_counts, ruined_counts)
                VALUES (?, ?, 0, 1)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET ruined_counts = ruined_counts + 1
            """, (message.author.id, message.guild.id)))

        else:
            # REACTIONS COLLECTED -> ROLL DICE
            dice_roll = random.randint(1, 6)
            outcome_msg = f"🎲 **Dice Roll: {dice_roll}**\n"
            
            if dice_roll in [2, 4, 6]:
                # SAVE
                new_count = current_count
                outcome_msg += "✨ **Saved!** The count continues!"
                # No update to config needed except maybe verifying it? 
                # Actually if saved, we do NOTHING to counting_config.
            elif dice_roll == 3:
                # RESET
                new_count = 0
                new_last_user_id = None
                outcome_msg += "💥 **Reset!** The count goes back to 0."
            elif dice_roll == 1:
                # -10 Penalty
                new_count = max(0, current_count - 10)
                new_last_user_id = None
                outcome_msg += "🔻 **-10 Penalty!** The count drops by 10."
            elif dice_roll == 5:
                # -5 Penalty
                new_count = max(0, current_count - 5)
                new_last_user_id = None
                outcome_msg += "🔻 **-5 Penalty!** The count drops by 5."

            if dice_roll not in [2, 4, 6]:
                dice_db_ops.append(("""
                    UPDATE counting_config 
                    SET current_count = ?, last_user_id = ?
                    WHERE guild_id = ?
                """, (new_count, new_last_user_id, message.guild.id)))
            
            dice_db_ops.append(("""
                INSERT INTO counting_stats (user_id, guild_id, total_counts, ruined_counts)
                VALUES (?, ?, 0, 1)
                ON CONFLICT(user_id, guild_id) DO UPDATE SET ruined_counts = ruined_counts + 1
            """, (message.author.id, message.guild.id)))

        # EXECUTE DB OPS with Retry
        if dice_db_ops:
            retries = 3
            while retries > 0:
                try:
                    async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
                        for sql, args in dice_db_ops:
                            await db.execute(sql, args)
                        await db.commit()
                    break # Success
                except aiosqlite.OperationalError as e:
                    if "locked" in str(e):
                        retries -= 1
                        await asyncio.sleep(0.5)
                    else:
                        print(f"Error saving count fail state: {e}")
                        break

        # 4. Edit message
        await status_msg.edit(content=f"{reason} {message.author.mention} messed up at {current_count}!\n{outcome_msg}\nNext number is **{new_count + 1}**.")

    @commands.command(name="mcl", aliases=["tc"])
    async def most_count_leaderboard(self, ctx):
        async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
            async with db.execute("""
                SELECT user_id, total_counts 
                FROM counting_stats 
                WHERE guild_id = ? 
                ORDER BY total_counts DESC 
                LIMIT 10
            """, (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()
        
        if not rows:
            await ctx.send("No counting stats yet.")
            return

        embed = discord.Embed(title="Most Count Leaderboard", color=discord.Color.blue())
        description = ""
        for i, (user_id, count) in enumerate(rows, 1):
            description += f"{i}. <@{user_id}>: {count}\n"
        embed.description = description
        await ctx.send(embed=embed)

    @commands.command(name="mrl")
    async def most_ruined_leaderboard(self, ctx):
        async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
            async with db.execute("""
                SELECT user_id, ruined_counts 
                FROM counting_stats 
                WHERE guild_id = ? 
                ORDER BY ruined_counts DESC 
                LIMIT 10
            """, (ctx.guild.id,)) as cursor:
                rows = await cursor.fetchall()
        
        if not rows:
            await ctx.send("No ruined stats yet.")
            return

        embed = discord.Embed(title="Most Ruined Leaderboard", color=discord.Color.red())
        description = ""
        for i, (user_id, count) in enumerate(rows, 1):
            description += f"{i}. <@{user_id}>: {count}\n"
        embed.description = description
        await ctx.send(embed=embed)

    @commands.command(name="scs")
    async def server_count_stats(self, ctx):
        async with aiosqlite.connect(DB_PATH, timeout=30.0) as db:
            async with db.execute("SELECT current_count, high_score FROM counting_config WHERE guild_id = ?", (ctx.guild.id,)) as cursor:
                row = await cursor.fetchone()
        
        if not row:
            await ctx.send("Counting channel not set up or no data.")
            return
            
        current, high = row
        embed = discord.Embed(title="Server Count Stats", color=discord.Color.green())
        embed.add_field(name="Current Count", value=str(current))
        embed.add_field(name="High Score", value=str(high))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Counting(bot))
