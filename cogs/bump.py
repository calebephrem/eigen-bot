import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict
from pathlib import Path

class BumpSystem(commands.Cog):
    """
    Bump Reminder System with Leaderboard and Reaction Time tracking.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db_path = Path("data/bump.db")
        self.disboard_id = 302050872383242240  # Disboard Bot ID
        # reminder_task will be started in cog_load after DB initialization

    async def cog_load(self):
        await self.init_db()
        # ensure reminder_task starts after DB is ready
        try:
            if not self.reminder_task.is_running():
                self.reminder_task.start()
        except RuntimeError:
            # if already started or bot shutting down, ignore
            pass

    def cog_unload(self):
        self.reminder_task.cancel()

    async def init_db(self):
        self.db_path.parent.mkdir(exist_ok=True)
        async with aiosqlite.connect(self.db_path) as db:
            # Configuration table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bump_config (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    message TEXT,
                    role_id INTEGER
                )
            """)
            # Stats table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bump_stats (
                    user_id INTEGER,
                    guild_id INTEGER,
                    bump_count INTEGER DEFAULT 0,
                    total_reaction_time INTEGER DEFAULT 0,
                    PRIMARY KEY (user_id, guild_id)
                )
            """)
            # State table (to persist next bump time)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bump_state (
                    guild_id INTEGER PRIMARY KEY,
                    next_bump_timestamp REAL,
                    reminder_sent_timestamp REAL,
                    reminder_sent BOOLEAN DEFAULT 0
                )
            """)
            await db.commit()

    @tasks.loop(seconds=30)
    async def reminder_task(self):
        """Checks if a bump reminder needs to be sent."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT guild_id, next_bump_timestamp, reminder_sent FROM bump_state")
            states = await cursor.fetchall()
            
            now = datetime.now(timezone.utc).timestamp()
            
            for guild_id, next_ts, reminder_sent in states:
                if next_ts and now >= next_ts and not reminder_sent:
                    # Time to remind!
                    await self.send_reminder(guild_id)

    @reminder_task.before_loop
    async def before_reminder_task(self):
        await self.bot.wait_until_ready()

    async def send_reminder(self, guild_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            # Get config
            cursor = await db.execute("SELECT channel_id, message, role_id FROM bump_config WHERE guild_id = ?", (guild_id,))
            config = await cursor.fetchone()
            
            if not config:
                return

            channel_id, message_text, role_id = config
            channel = self.bot.get_channel(channel_id)
            
            if channel and isinstance(channel, discord.TextChannel):
                # Prepare message
                msg = message_text or "It's time to bump the server!"
                
                # Construct content with role ping
                content = f"<@&{role_id}> {msg}" if role_id else msg
                
                try:
                    embed = discord.Embed(
                        title="🔔 Bump Reminder",
                        description="It's time to bump the server! Use `/bump`",
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text="Bump now to track your reaction time!")
                    await channel.send(content=content, embed=embed)
                    
                    # Update state (insert or update)
                    now = datetime.now(timezone.utc).timestamp()
                    await db.execute("""
                        INSERT INTO bump_state (guild_id, next_bump_timestamp, reminder_sent_timestamp, reminder_sent)
                        VALUES (?, NULL, ?, 1)
                        ON CONFLICT(guild_id) DO UPDATE SET reminder_sent = 1, reminder_sent_timestamp = excluded.reminder_sent_timestamp
                    """, (guild_id, now))
                    await db.commit()
                except Exception as e:
                    print(f"Failed to send bump reminder in guild {guild_id}: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Check if message is from Disboard or a bot responding to /bump
        # Disboard ID: 302050872383242240
        # We also check for interaction metadata if available
        
        is_bump_success = False
        bumper_user = None

        # Method 1: Check for interaction (Slash Command) response
        # Prefer interaction_metadata (v2.4+) to avoid deprecation warning
        interaction = None
        if hasattr(message, 'interaction_metadata'):
            interaction = message.interaction_metadata
        else:
            interaction = message.interaction
        
        if interaction and getattr(interaction, 'name', None) == "bump":
            if message.embeds:
                desc = (message.embeds[0].description or "").lower()
                if "bumped" in desc:
                    is_bump_success = True
                    bumper_user = getattr(interaction, 'user', None)

        # Method 2: Fallback for text command or if interaction data is missing but it's Disboard
        elif message.author and getattr(message.author, 'id', None) == self.disboard_id:
            if message.embeds:
                desc = (message.embeds[0].description or "").lower()
                if "bumped" in desc:
                    is_bump_success = True
                    # We don't always know who bumped in this case (lack of interaction info)
                    bumper_user = None

        if is_bump_success and message.guild:
            await self.handle_bump_success(message.guild.id, bumper_user)

    async def handle_bump_success(self, guild_id: int, user: Optional[discord.User]):
        now = datetime.now(timezone.utc).timestamp()
        next_bump = now + (2 * 60 * 60) # 2 hours later

        async with aiosqlite.connect(self.db_path) as db:
            # Get previous state to calculate reaction time
            cursor = await db.execute("SELECT reminder_sent_timestamp, reminder_sent FROM bump_state WHERE guild_id = ?", (guild_id,))
            state = await cursor.fetchone()
            
            reaction_time = 0
            if state:
                reminder_ts, reminder_sent = state
                if reminder_sent and reminder_ts:
                    reaction_time = int((now - reminder_ts) * 1000) # ms
                    # If reaction time is negative (bumped before reminder?), ignore or set to 0
                    if reaction_time < 0: reaction_time = 0

            # Update State
            await db.execute("""
                INSERT OR REPLACE INTO bump_state (guild_id, next_bump_timestamp, reminder_sent, reminder_sent_timestamp)
                VALUES (?, ?, 0, NULL)
            """, (guild_id, next_bump))

            # Update Stats if user is known
            if user:
                # Check if user exists
                cursor = await db.execute("SELECT bump_count, total_reaction_time FROM bump_stats WHERE user_id = ? AND guild_id = ?", (user.id, guild_id))
                stats = await cursor.fetchone()
                
                if stats:
                    new_count = stats[0] + 1
                    new_total_time = stats[1] + reaction_time
                    await db.execute("""
                        UPDATE bump_stats 
                        SET bump_count = ?, total_reaction_time = ? 
                        WHERE user_id = ? AND guild_id = ?
                    """, (new_count, new_total_time, user.id, guild_id))
                else:
                    await db.execute("""
                        INSERT INTO bump_stats (user_id, guild_id, bump_count, total_reaction_time)
                        VALUES (?, ?, 1, ?)
                    """, (user.id, guild_id, reaction_time))
            
            await db.commit()
            
            # Send confirmation
            channel_id = None
            cursor = await db.execute("SELECT channel_id FROM bump_config WHERE guild_id = ?", (guild_id,))
            row = await cursor.fetchone()
            if row:
                channel_id = row[0]
                channel = self.bot.get_channel(channel_id)
                if channel and isinstance(channel, discord.TextChannel):
                    embed = discord.Embed(title="✅ Timer Reset", description=f"Next bump in 2 hours (<t:{int(next_bump)}:R>).", color=discord.Color.green())
                    if user and reaction_time > 0:
                        seconds = reaction_time / 1000
                        embed.add_field(name="Reaction Time", value=f"{seconds:.2f}s")
                    await channel.send(embed=embed)

    @commands.hybrid_command(name="bumpconfig", help="Configure the bump reminder system.")
    @app_commands.describe(channel="Channel to send reminders in", message="Message to send", role="Role to ping (optional)")
    @commands.has_permissions(administrator=True)
    async def bump_config(self, ctx: commands.Context, channel: discord.TextChannel, message: str, role: Optional[discord.Role] = None):
        """Set the bump reminder channel and message."""
        if not ctx.guild:
            return
        role_id = role.id if role else None
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO bump_config (guild_id, channel_id, message, role_id)
                VALUES (?, ?, ?, ?)
            """, (ctx.guild.id, channel.id, message, role_id))
            # Ensure there is a bump_state entry for this guild
            await db.execute("""
                INSERT INTO bump_state (guild_id, next_bump_timestamp, reminder_sent, reminder_sent_timestamp)
                VALUES (?, NULL, 0, NULL)
                ON CONFLICT(guild_id) DO NOTHING
            """, (ctx.guild.id,))
            await db.commit()
            
        embed = discord.Embed(title="Bump Configuration Saved", color=discord.Color.green())
        embed.add_field(name="Channel", value=channel.mention)
        embed.add_field(name="Message", value=message)
        if role:
            embed.add_field(name="Role Ping", value=role.mention)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bumpleaderboard", help="Show the bump leaderboard.")
    @commands.guild_only()
    async def bump_leaderboard(self, ctx: commands.Context):
        """Show top bumpers in the server."""
        if not ctx.guild:
            return
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT user_id, bump_count, total_reaction_time 
                FROM bump_stats 
                WHERE guild_id = ? 
                ORDER BY bump_count DESC 
                LIMIT 10
            """, (ctx.guild.id,))
            rows = await cursor.fetchall()
            
        if not rows:
            await ctx.send("No bump stats recorded yet.")
            return

        embed = discord.Embed(title="🏆 Bump Leaderboard", color=discord.Color.gold())
        
        for i, (user_id, count, total_time) in enumerate(rows, 1):
            user = ctx.guild.get_member(user_id)
            name = user.display_name if user else f"User {user_id}"
            
            avg_time_str = "N/A"
            if count > 0 and total_time > 0:
                avg_ms = total_time / count
                avg_time_str = f"{avg_ms/1000:.1f}s"
                
            embed.add_field(
                name=f"#{i} {name}",
                value=f"**Bumps:** {count}\n**Avg Reaction:** {avg_time_str}",
                inline=True
            )
            
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="bumptest", help="Test the bump reminder immediately.")
    @commands.has_permissions(administrator=True)
    async def bump_test(self, ctx: commands.Context):
        """Trigger a fake reminder for testing."""
        if not ctx.guild:
            return
        await self.send_reminder(ctx.guild.id)
        await ctx.send("Test reminder sent (if configured).")

async def setup(bot: commands.Bot):
    await bot.add_cog(BumpSystem(bot))
