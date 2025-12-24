"""
Configuration management using Pydantic settings.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Bot configuration settings."""

    discord_token: str = Field(default='demo_token')
    guild_id: Optional[int] = Field(default=None)
    log_level: str = Field(default='INFO')
    owner_id: Optional[int] = Field(default=None)
    topgg_token: Optional[str] = Field(default=None)
    topgg_webhook_secret: Optional[str] = Field(default=None)
    redis_url: Optional[str] = Field(default=None)

    # CodeBuddy settings
    question_channel_id: Optional[int] = Field(default=None)

    class Config:
        env_file = '.env'
        case_sensitive = False
