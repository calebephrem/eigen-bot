"""
Daily Quests System - Inspired by OWO bot
Complete daily challenges to earn streak freezes and bonus hints!
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.codebuddy_database import (
    get_daily_quest_progress, 
    get_quest_rewards,
    use_streak_freeze,
    use_bonus_hint
)


class DailyQuestsCog(commands.Cog):
    """Daily quests and rewards system for CodeBuddy."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name="dailyquest", aliases=["dq", "quests", "quest", "daily", "checklist"])
    async def daily_quest(self, ctx: commands.Context):
        """
        View your daily quest progress and rewards.
        Complete 5 quizzes and vote for the bot to earn rewards!
        """
        user_id = ctx.author.id
        
        try:
            # Get quest progress
            quest_date, quizzes, voted, completed, freezes, hints = await get_daily_quest_progress(user_id)
            
            # Create embed
            embed = discord.Embed(
                title="Daily Quest Checklist",
                description="Complete all tasks to earn rewards! Resets every 24 hours.",
                color=0x000000
            )
            
            # Quest tasks
            quiz_status = "Done" if quizzes >= 5 else f"{quizzes}/5"
            vote_status = "Done" if voted == 1 else "Pending"
            
            tasks = f"""
            **1. Solve 5 Basic Quizzes** {quiz_status}
            Answer <#1398986762352857129> quiz questions correctly
            
            **2. Vote for the Bot** {vote_status}
            Vote on top.gg (coming soon!)
            """
            
            embed.add_field(name="Quest Tasks", value=tasks, inline=False)
            
            # Rewards section
            if completed == 1:
                reward_text = "**Quest Completed!** You earned:\n• 1 Streak Freeze\n• 1 Bonus Hint"
            else:
                reward_text = "Complete all tasks to earn:\n• 1 Streak Freeze (protects your streak)\n• 1 Bonus Hint (use `?bonushint` in quiz)"
            
            embed.add_field(name="Rewards", value=reward_text, inline=False)
            
            # Current inventory
            inventory = f"Streak Freezes: **{freezes}**\nBonus Hints: **{hints}**"
            embed.add_field(name="Your Inventory", value=inventory, inline=False)
            
            # Footer
            embed.set_footer(text=f"Quest Date: {quest_date.strftime('%Y-%m-%d')} • Keep grinding!")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"[Error in daily_quest command]: {e}")
            await ctx.send("An error occurred while fetching your quest progress.", ephemeral=True)
    
    @commands.command(name="bonushint", aliases=["hint"])
    async def bonus_hint(self, ctx: commands.Context):
        """
        Use a bonus hint on the current quiz question.
        Hints are earned by completing daily quests!
        """
        user_id = ctx.author.id
        
        try:
            # Check if user has hints
            freezes, hints = await get_quest_rewards(user_id)
            
            if hints <= 0:
                embed = discord.Embed(
                    title="No Bonus Hints Available",
                    description="You don't have any bonus hints! Complete your daily quest to earn one.",
                    color=0x000000
                )
                embed.add_field(
                    name="How to Get Hints",
                    value="Use `?dailyquest` to check your progress and complete tasks!",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            # Check if there's an active question (from CodeBuddyQuizCog)
            quiz_cog = self.bot.get_cog("CodeBuddyQuizCog")
            
            if not quiz_cog or not quiz_cog.question_active:
                await ctx.send("There's no active quiz question right now. Wait for the next question!", ephemeral=True)
                return
            
            # Use the hint
            used = await use_bonus_hint(user_id)
            
            if not used:
                await ctx.send("Failed to use bonus hint. Please try again.", ephemeral=True)
                return
            
            # Provide the hint (ephemeral)
            correct_answer = quiz_cog.current_answer
            
            # Create hint message
            hint_text = f"**Bonus Hint Used!**\n\n"
            
            if correct_answer == "a":
                hint_text += "The correct answer is **NOT** 'b' or 'c'!"
            elif correct_answer == "b":
                hint_text += "The correct answer is **NOT** 'a' or 'c'!"
            else:  # c
                hint_text += "The correct answer is **NOT** 'a' or 'b'!"
            
            hint_text += f"\n\nYou have **{hints - 1}** bonus hint(s) remaining."
            
            embed = discord.Embed(
                title="Bonus Hint",
                description=hint_text,
                color=0x000000
            )
            embed.set_footer(text="This message is only visible to you!")
            
            # Send ephemeral message (in DM or as a temporary message)
            try:
                await ctx.author.send(embed=embed)
                await ctx.message.add_reaction("✅")
            except discord.Forbidden:
                # If DMs are disabled, send a temporary message
                msg = await ctx.send(embed=embed)
                # Delete after 10 seconds
                await msg.delete(delay=10)
            
        except Exception as e:
            print(f"[Error in bonus_hint command]: {e}")
            await ctx.send("An error occurred while using your bonus hint.", ephemeral=True)
    
    @commands.command(name="inventory", aliases=["inv", "rewards"])
    async def inventory(self, ctx: commands.Context):
        """View your quest rewards inventory."""
        user_id = ctx.author.id
        
        try:
            freezes, hints = await get_quest_rewards(user_id)
            
            embed = discord.Embed(
                title="Your Inventory",
                description="Items earned from completing daily quests",
                color=0x000000
            )
            
            # Streak Freezes
            freeze_desc = "Protect your quiz streak when you answer incorrectly.\nAutomatically used when needed."
            embed.add_field(
                name=f"Streak Freezes: {freezes}",
                value=freeze_desc,
                inline=False
            )
            
            # Bonus Hints
            hint_desc = "Get a hint on the current quiz question.\nUse with `?bonushint` or `?hint`"
            embed.add_field(
                name=f"Bonus Hints: {hints}",
                value=hint_desc,
                inline=False
            )
            
            # How to earn more
            embed.add_field(
                name="How to Earn More",
                value="Complete your daily quest! Use `?dailyquest` to check progress.",
                inline=False
            )
            
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.set_footer(text="Keep completing quests to build your inventory!")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"[Error in inventory command]: {e}")
            await ctx.send("An error occurred while fetching your inventory.", ephemeral=True)
    
    @app_commands.command(name="dailyquest", description="View your daily quest progress and rewards")
    async def daily_quest_slash(self, interaction: discord.Interaction):
        """Slash command version of dailyquest."""
        user_id = interaction.user.id
        
        try:
            # Get quest progress
            quest_date, quizzes, voted, completed, freezes, hints = await get_daily_quest_progress(user_id)
            
            # Create embed
            embed = discord.Embed(
                title="Daily Quest Checklist",
                description="Complete all tasks to earn rewards! Resets every 24 hours.",
                color=0x000000
            )
            
            # Quest tasks
            quiz_status = "Done" if quizzes >= 5 else f"{quizzes}/5"
            vote_status = "Done" if voted == 1 else "Pending"
            
            tasks = f"""
            **1. Solve 5 Basic Quizzes** {quiz_status}
            *Answer CodeBuddy quiz questions correctly*
            
            **2. Vote for the Bot** {vote_status}
            *Vote on top.gg (coming soon!)*
            """
            
            embed.add_field(name="Quest Tasks", value=tasks, inline=False)
            
            # Rewards section
            if completed == 1:
                reward_text = "**Quest Completed!** You earned:\n• 1 Streak Freeze\n• 1 Bonus Hint"
            else:
                reward_text = "Complete all tasks to earn:\n• 1 Streak Freeze (protects your streak)\n• 1 Bonus Hint (use `?bonushint` in quiz)"
            
            embed.add_field(name="Rewards", value=reward_text, inline=False)
            
            # Current inventory
            inventory = f"Streak Freezes: **{freezes}**\nBonus Hints: **{hints}**"
            embed.add_field(name="Your Inventory", value=inventory, inline=False)
            
            # Footer
            embed.set_footer(text=f"Quest Date: {quest_date.strftime('%Y-%m-%d')} • Keep grinding!")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"[Error in daily_quest_slash command]: {e}")
            await interaction.response.send_message("An error occurred while fetching your quest progress.", ephemeral=True)


async def setup(bot: commands.Bot):
    """Setup function to load the cog."""
    await bot.add_cog(DailyQuestsCog(bot))
