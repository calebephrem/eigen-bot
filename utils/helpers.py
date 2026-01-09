"""
Helper utilities for the bot.
"""

import random
from typing import Any, List, Optional

import discord
from discord import Embed

from utils.config import Config


class EmbedBuilder:
    """Helper class for building Discord embeds."""

    @staticmethod
    def success_embed(title: str, description: str = "") -> Embed:
        """Create a success embed."""
        embed = Embed(title=title, description=description, color=discord.Color.green())
        return embed

    @staticmethod
    def error_embed(title: str, description: str = "") -> Embed:
        """Create an error embed."""
        embed = Embed(title=title, description=description, color=discord.Color.red())
        return embed

    @staticmethod
    def info_embed(title: str, description: str = "") -> Embed:
        """Create an info embed."""
        embed = Embed(title=title, description=description, color=discord.Color.blue())
        return embed


# --- Additional helpers used by cogs/community.py ---
def get_random_quote(quotes: list) -> str:
    if not quotes:
        return ""
    return random.choice(quotes)


def get_random_question(questions: list):
    if not questions:
        return None
    return random.choice(questions)


async def fetch_programming_meme() -> str:
    # Minimal placeholder: return a stock image URL or a short message
    # In production, this would call an external API
    return "https://i.imgur.com/3G9jQ.jpg"


def sanitize_input(text: str, max_len: int = 1000) -> str:
    if not text:
        return ""
    cleaned = text.strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len]
    return cleaned

# --- Compatibility helper aliases for other cogs (starboard) ---
def create_success_embed(title: str, description: str = "") -> Embed:
    return EmbedBuilder.success_embed(title, description)

def create_error_embed(title: str, description: str = "") -> Embed:
    return EmbedBuilder.error_embed(title, description)

def create_warning_embed(title: str, description: str = "") -> Embed:
    # Using yellow/orange for warning style
    return Embed(title=title, description=description, color=discord.Color.orange())

def create_info_embed(title: str, description: str = "") -> Embed:
    return EmbedBuilder.info_embed(title, description)
