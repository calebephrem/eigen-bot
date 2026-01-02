"""
Misc commands cog.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime, timezone
import calendar

from utils.config import Config
from bot import Fun2OoshBot


class Misc(commands.Cog):
    """Miscellaneous commands."""

    def __init__(self, bot: Fun2OoshBot, config: Config):
        self.bot = bot
        self.config = config

    @commands.hybrid_command(name='about', description='Learn about Eigen Bot')
    async def about(self, ctx: commands.Context):
        """Show information about the bot."""
        embed = discord.Embed(
            title="Eigen Bot",
            description=(
                "Feature-rich Discord bot for community engagement, "
                "support tickets, and utilities. Built with discord.py."
            ),
            color=0x000000
        )
        
        # Add bot stats
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
        total_commands = len(self.bot.tree.get_commands())
        
        embed.add_field(
            name="Statistics",
            value=(
                f"Servers: **{total_guilds}**\n"
                f"Users: **{total_users:,}**\n"
                f"Commands: **{total_commands}**"
            ),
            inline=True
        )
        
        embed.add_field(
            name="Features",
            value=(
                "Support Tickets\n"
                "Starboard\n"
                "Custom Tags\n"
                "Elections\n"
                "Invite Tracker\n"
                "AFK System\n"
                "Fun Commands\n"
                "Utilities"
            ),
            inline=True
        )
        
        embed.add_field(
            name="Links",
            value=(
                "[GitHub](https://github.com/TheCodeVerseHub/Eigen-Bot) · "
                "[Invite](https://discord.com/api/oauth2/authorize) · "
                "[Support](https://discord.gg/4TkQYz7qea)"
            ),
            inline=False
        )
        
        embed.set_footer(
            text=f"discord.py {discord.__version__} · TheCodeVerseHub"
        )
        
        # Set bot thumbnail
        if self.bot.user and self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='song', aliases=['sp', 'spotify'], description='Show what you are currently listening to on Spotify')
    async def song(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        """Display the current song/music that a user is listening to on Spotify or other music apps."""
        target_user = user or ctx.author
        
        # Ensure target_user is a Member (has activities attribute)
        if not isinstance(target_user, discord.Member):
            embed = discord.Embed(
                title="❌ Error",
                description="This command only works in servers, not in DMs.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Check all activities - be more comprehensive
        spotify_activity = None
        music_activity = None
        
        for activity in target_user.activities:
            # Check for Spotify specifically
            if isinstance(activity, discord.Spotify):
                spotify_activity = activity
                break
            # Check for any listening activity (including other music apps)
            elif activity.type == discord.ActivityType.listening:
                music_activity = activity
        
        if spotify_activity:
            # Create rich embed for Spotify
            embed = discord.Embed(
                title="Now Playing · Spotify",
                description=f"{target_user.display_name}",
                color=0x000000
            )
            
            # Song details
            embed.add_field(
                name="Track",
                value=f"**[{spotify_activity.title}]({spotify_activity.track_url})**",
                inline=False
            )
            
            embed.add_field(
                name="Artist",
                value=", ".join(spotify_activity.artists),
                inline=True
            )
            
            embed.add_field(
                name="Album",
                value=spotify_activity.album,
                inline=True
            )
            
            # Duration
            duration = spotify_activity.duration
            current = (discord.utils.utcnow() - spotify_activity.start).total_seconds()
            
            duration_str = f"{int(duration.total_seconds() // 60)}:{int(duration.total_seconds() % 60):02d}"
            current_str = f"{int(current // 60)}:{int(current % 60):02d}"
            
            # Progress bar
            progress = min(current / duration.total_seconds(), 1.0)
            bar_length = 20
            filled = int(bar_length * progress)
            bar = "━" * filled + "○" + "─" * (bar_length - filled - 1)
            
            embed.add_field(
                name="Duration",
                value=f"`{current_str}` {bar} `{duration_str}`",
                inline=False
            )
            
            # Add album art if available
            if spotify_activity.album_cover_url:
                embed.set_thumbnail(url=spotify_activity.album_cover_url)
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
        elif music_activity:
            # Found other music activity (not Spotify)
            if True:
                # Generic music activity
                embed = discord.Embed(
                    title="Now Listening",
                    description=f"{target_user.display_name}",
                    color=0x000000
                )
                
                embed.add_field(
                    name="Activity",
                    value=f"**{music_activity.name}**",
                    inline=False
                )
                
                # Use getattr to safely access optional attributes
                details = getattr(music_activity, 'details', None)
                if details:
                    embed.add_field(name="Details", value=details, inline=False)
                
                state = getattr(music_activity, 'state', None)
                if state:
                    embed.add_field(name="State", value=state, inline=False)
                
                embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        else:
            # No music activity found - show debug info
            if target_user == ctx.author:
                # Show what activities were detected
                activities_list = []
                for activity in target_user.activities:
                    activities_list.append(f"• **{activity.name}** (Type: {activity.type.name})")
                
                if activities_list:
                    debug_info = "\n".join(activities_list)
                    message = (
                        "❌ **No music activity detected!**\n\n"
                        f"**Your current activities:**\n{debug_info}\n\n"
                        "**Possible solutions:**\n"
                        "• Make sure you're listening to music on Spotify, Apple Music, YouTube Music, etc.\n"
                        "• Enable 'Display current activity' in Discord Settings → Activity Privacy\n"
                        "• Restart your Discord client\n"
                        "• Make sure the music app is connected to Discord (check User Settings → Connections)"
                    )
                else:
                    message = (
                        "❌ **You are not currently listening to any music!**\n\n"
                        "**To use this command:**\n"
                        "• Be listening to Spotify or another music app\n"
                        "• Enable 'Display current activity' in Discord Settings → Activity Privacy\n"
                        "• Have your Discord client open and showing your activity\n"
                        "• Connect your music app in Discord Settings → Connections (for Spotify)"
                    )
            else:
                message = (
                    f"❌ **{target_user.display_name} is not currently listening to any music!**\n\n"
                    "They must be listening to Spotify or another music app with activity status enabled."
                )
            
            embed = discord.Embed(
                title="No Music Playing",
                description=message,
                color=0x000000
            )
            embed.set_footer(text="Activity Privacy must be enabled")
        
        await ctx.send(embed=embed)

    @commands.command(name='uptime', hidden=True)
    async def uptime(self, ctx: commands.Context):
        """Show the bot's uptime."""
        if not hasattr(self.bot, 'start_time'):
            await ctx.send("Start time not tracked.")
            return

        now = discord.utils.utcnow()
        delta = now - self.bot.start_time
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        await ctx.send(f"⏱️ **Uptime:** {uptime_str}")

    @commands.command(name='diagnose', hidden=True)
    @commands.has_permissions(administrator=True)
    async def diagnose(self, ctx: commands.Context):
        """Show diagnostic information (Admin only)."""
        # Slash commands count
        slash_commands = len(self.bot.tree.get_commands())
        # Prefix commands count
        prefix_commands = len(self.bot.commands)
        # Guilds
        guilds = len(self.bot.guilds)
        # Users
        users = sum(g.member_count for g in self.bot.guilds if g.member_count)
        # Latency
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(title="Diagnostic Info", color=0x000000)
        embed.add_field(name="Slash Commands", value=str(slash_commands), inline=True)
        embed.add_field(name="Prefix Commands", value=str(prefix_commands), inline=True)
        embed.add_field(name="Guilds", value=str(guilds), inline=True)
        embed.add_field(name="Users", value=str(users), inline=True)
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        
        if hasattr(self.bot, 'start_time'):
             embed.add_field(name="Start Time", value=discord.utils.format_dt(self.bot.start_time, 'R'), inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='bug', description='Report a bug to the bot dev - Only for small bugs')
    @app_commands.describe(bug='Describe the bug you encountered')
    async def bug_report(self, ctx: commands.Context, *, bug: str):
        """Report a bug to the support server."""
        # Support server channel ID
        SUPPORT_CHANNEL_ID = 1452739906525728828
        
        # Get interaction for hybrid command
        interaction = ctx.interaction or ctx
        user = ctx.author
        guild = ctx.guild
        
        try:
            # Get the support channel
            support_channel = self.bot.get_channel(SUPPORT_CHANNEL_ID)
            
            if not support_channel or not isinstance(support_channel, discord.TextChannel):
                response = "❌ Could not access the support channel. Please join our [support server](https://discord.gg/4TkQYz7qea) and report the bug there."
                if ctx.interaction:
                    await ctx.interaction.response.send_message(response, ephemeral=True)
                else:
                    await ctx.send(response)
                return
            
            # Create bug report embed
            embed = discord.Embed(
                title="Bug Report",
                color=0x000000
            )
            
            # Add bug details
            embed.add_field(name="Details", value="*"+bug+"*", inline=False)
            
            # Add reporter and server info inline
            reporter_info = f"{user.mention} · `{user.id}`"
            location_info = f"{guild.name} · `{guild.id}`" if guild else "Direct Message"
            
            embed.add_field(name="Reported by", value=reporter_info, inline=True)
            embed.add_field(name="Server", value=location_info, inline=True)
            
            # Send to support channel
            await support_channel.send(embed=embed)
            
            # Confirm to user
            response = (
                "✅ Your bug report has been submitted to our support team. Thank you for helping us improve!\n\n"
                "**Want to track your report or get faster support?**\n"
                "Join our support server: https://discord.gg/4TkQYz7qea"
            )
            if ctx.interaction:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.send_message(response, ephemeral=True)
                else:
                    await ctx.interaction.followup.send(response, ephemeral=True)
            else:
                await ctx.send(response)
            
        except Exception as e:
            response = (
                f"❌ An error occurred while submitting your bug report: {str(e)}\n\n"
                "Please report this directly in our [support server](https://discord.gg/4TkQYz7qea)."
            )
            if ctx.interaction:
                if not ctx.interaction.response.is_done():
                    await ctx.interaction.response.send_message(response, ephemeral=True)
                else:
                    await ctx.interaction.followup.send(response, ephemeral=True)
            else:
                await ctx.send(response)
    
    @commands.hybrid_command(name='support', description='Get the support server invite link')
    async def support(self, ctx: commands.Context):
        """Send the support server invite link."""
        embed = discord.Embed(
            title="Support Server",
            description=(
                "[discord.gg/4TkQYz7qea](https://discord.gg/4TkQYz7qea)\n\n"
                "Get help with bug reports, feature requests, questions, and updates."
            ),
            color=0x000000
        )
        
        embed.set_footer(text="Support")
        
        if ctx.interaction:
            await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await ctx.send(embed=embed)
    
    @app_commands.command(name='newfeature', description='Suggest a new feature for the bot')
    @app_commands.describe(feature='Describe the feature you would like to see')
    async def new_feature(self, interaction: discord.Interaction, feature: str):
        """Submit a feature request to the support server."""
        # Feature requests channel ID
        FEATURE_CHANNEL_ID = 1452740031419777096
        
        try:
            # Get the feature requests channel
            feature_channel = self.bot.get_channel(FEATURE_CHANNEL_ID)
            
            if not feature_channel or not isinstance(feature_channel, discord.TextChannel):
                await interaction.response.send_message(
                    "❌ Could not access the feature requests channel. Please join our [support server](https://discord.gg/4TkQYz7qea) and submit your request there.",
                    ephemeral=True
                )
                return
            
            # Create feature request embed
            embed = discord.Embed(
                title="Feature Request",
                color=0x000000
            )
            
            # Add feature details
            embed.add_field(name="Details", value="*"+feature+"*", inline=False)
            
            # Add requester and server info inline
            requester_info = f"{interaction.user.mention} · `{interaction.user.id}`"
            location_info = f"{interaction.guild.name} · `{interaction.guild.id}`" if interaction.guild else "Direct Message"
            
            embed.add_field(name="Requested By", value=requester_info, inline=True)
            embed.add_field(name="Location", value=location_info, inline=True)
            
            # Send to feature requests channel
            await feature_channel.send(embed=embed)
            
            # Confirm to user
            await interaction.response.send_message(
                "✅ Your feature request has been submitted! Our team will review it soon.\n\n"
                "**Want to discuss your idea or see other requests?**\n"
                "Join our support server: https://discord.gg/4TkQYz7qea",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred while submitting your feature request: {str(e)}\n\n"
                "Please submit it directly in our [support server](https://discord.gg/4TkQYz7qea).",
                ephemeral=True
            )
    
    @app_commands.command(name='feedback', description='Share your feedback about the bot')
    @app_commands.describe(
        rating='Rate your experience (1-5 stars)',
        feedback='Share your thoughts, suggestions, or testimonial'
    )
    @app_commands.choices(rating=[
        app_commands.Choice(name='⭐ 1 Star - Poor', value=1),
        app_commands.Choice(name='⭐⭐ 2 Stars - Fair', value=2),
        app_commands.Choice(name='⭐⭐⭐ 3 Stars - Good', value=3),
        app_commands.Choice(name='⭐⭐⭐⭐ 4 Stars - Very Good', value=4),
        app_commands.Choice(name='⭐⭐⭐⭐⭐ 5 Stars - Excellent', value=5)
    ])
    async def feedback_command(self, interaction: discord.Interaction, rating: int, feedback: str):
        """Submit feedback/testimonial to the support server."""
        # Feedback/testimonials channel ID
        FEEDBACK_CHANNEL_ID = 1453356371952275527
        
        try:
            # Get the feedback channel
            feedback_channel = self.bot.get_channel(FEEDBACK_CHANNEL_ID)
            
            if not feedback_channel or not isinstance(feedback_channel, discord.TextChannel):
                await interaction.response.send_message(
                    "❌ Could not access the feedback channel. Please join our [support server](https://discord.gg/4TkQYz7qea) and share your feedback there.",
                    ephemeral=True
                )
                return
            
            # Create star rating display
            stars = "⭐" * rating
            rating_text = ["Poor", "Fair", "Good", "Very Good", "Excellent"][rating - 1]
            
            # Create feedback embed with professional black design
            embed = discord.Embed(
                title=f"{stars} {rating}/5 · {rating_text}",
                color=0x000000
            )
            
            # Add feedback content
            embed.add_field(name="Feedback", value="*"+feedback+"*", inline=False)
            
            # Add reviewer and server info inline
            reviewer_info = f"{interaction.user.mention} · `{interaction.user.id}`"
            location_info = f"{interaction.guild.name} · `{interaction.guild.id}`" if interaction.guild else "Direct Message"
            
            embed.add_field(name="User", value=reviewer_info, inline=True)
            embed.add_field(name="Server", value=location_info, inline=True)
            
            # Send to feedback channel
            await feedback_channel.send(embed=embed)
            
            # Confirm to user with different messages based on rating
            if rating >= 4:
                message = (
                    "✅ Thank you for your positive feedback! We're thrilled you're enjoying the bot! 🎉\n\n"
                    "**Help us grow:**\n"
                    "Share your experience with others in our [support server](https://discord.gg/4TkQYz7qea)!"
                )
            else:
                message = (
                    "✅ Thank you for your feedback! We appreciate your honesty and will work on improvements.\n\n"
                    "**Want to discuss further?**\n"
                    "Join our support server: https://discord.gg/4TkQYz7qea"
                )
            
            await interaction.response.send_message(message, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred while submitting your feedback: {str(e)}\n\n"
                "Please share it directly in our [support server](https://discord.gg/4TkQYz7qea).",
                ephemeral=True
            )
    
    @app_commands.command(name='timestamp', description='Generate Discord timestamps for any date/time')
    @app_commands.describe(
        year='Year (e.g., 2025)',
        month='Month (1-12)',
        day='Day of month (1-31)',
        hour='Hour in 24-hour format (0-23, optional)',
        minute='Minute (0-59, optional)',
        utc_offset='UTC offset in hours (e.g., -5 for EST, 5.5 for IST, optional)'
    )
    async def timestamp_command(
        self, 
        interaction: discord.Interaction,
        year: int,
        month: app_commands.Range[int, 1, 12],
        day: app_commands.Range[int, 1, 31],
        hour: app_commands.Range[int, 0, 23] = None,
        minute: app_commands.Range[int, 0, 59] = None,
        utc_offset: float = 0.0
    ):
        """Generate Discord timestamps with all available formats."""
        # Set defaults if None
        if hour is None:
            hour = 0
        if minute is None:
            minute = 0
            
        try:
            # Validate UTC offset range
            if utc_offset < -12 or utc_offset > 14:
                await interaction.response.send_message(
                    "❌ UTC offset must be between -12 and +14 hours!",
                    ephemeral=True
                )
                return
            
            # Validate the date
            if day > calendar.monthrange(year, month)[1]:
                await interaction.response.send_message(
                    f"❌ Invalid date: {month}/{day}/{year} does not exist!",
                    ephemeral=True
                )
                return
            
            # Create datetime object in UTC
            # User provides time in their timezone, convert to UTC
            offset_hours = int(utc_offset)
            offset_minutes = int((utc_offset - offset_hours) * 60)
            
            # Create the datetime in user's timezone
            user_dt = datetime(year, month, day, hour, minute)
            
            # Convert to UTC by subtracting the offset
            utc_dt = user_dt.replace(tzinfo=None)
            # Subtract offset to get UTC time
            from datetime import timedelta
            utc_dt = utc_dt - timedelta(hours=offset_hours, minutes=offset_minutes)
            
            # Get Unix timestamp
            unix_timestamp = int(utc_dt.replace(tzinfo=timezone.utc).timestamp())
            
            # Create embed with all timestamp formats
            embed = discord.Embed(
                title="Discord Timestamps",
                description=f"{month}/{day}/{year} {hour:02d}:{minute:02d} (UTC{utc_offset:+.1f})",
                color=0x000000
            )
            
            # Add all timestamp formats
            formats = [
                ("Short Time", "t", f"<t:{unix_timestamp}:t>"),
                ("Long Time", "T", f"<t:{unix_timestamp}:T>"),
                ("Short Date", "d", f"<t:{unix_timestamp}:d>"),
                ("Long Date", "D", f"<t:{unix_timestamp}:D>"),
                ("Short Date/Time", "f", f"<t:{unix_timestamp}:f>"),
                ("Long Date/Time", "F", f"<t:{unix_timestamp}:F>"),
                ("Relative Time", "R", f"<t:{unix_timestamp}:R>"),
            ]
            
            format_text = ""
            for name, code, timestamp_code in formats:
                # Show both the code and how it renders
                format_text += f"**{name}** (`{code}`)\n`{timestamp_code}` → {timestamp_code}\n\n"
            
            embed.add_field(
                name="Available Formats",
                value=format_text.strip(),
                inline=False
            )
            
            # Add copy-paste section
            embed.add_field(
                name="Quick Copy",
                value=(
                    f"**Unix Timestamp:** `{unix_timestamp}`\n"
                    f"**Default:** `<t:{unix_timestamp}>`\n"
                    f"**Relative:** `<t:{unix_timestamp}:R>`"
                ),
                inline=False
            )
            
            embed.set_footer(text="Click 'Copy' on any code block to use it")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError as e:
            await interaction.response.send_message(
                f"❌ Invalid date/time: {str(e)}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )

    @app_commands.command(name='say', description='Make the bot say something (Admin only)')
    @app_commands.describe(text='The text you want the bot to say')
    @app_commands.default_permissions(administrator=True)
    async def say(self, interaction: discord.Interaction, text: str):
        """Make the bot send a message (admin only to prevent abuse)."""
        # Double-check permissions (extra safety)
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ This command is restricted to administrators only.",
                ephemeral=True
            )
            return
        
        # Send the text in the channel
        await interaction.channel.send(text)
        
        # Confirm to admin (ephemeral so only they see it)
        await interaction.response.send_message(
            "✅ Message sent!",
            ephemeral=True
        )


async def setup(bot):
    """Setup the misc cog."""
    config = bot.config
    await bot.add_cog(Misc(bot, config))
