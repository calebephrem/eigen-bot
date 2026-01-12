import base64
import binascii
import discord
from discord import Interaction, app_commands
from discord.ext import commands


class InputModal(discord.ui.Modal, title="Base64 Encoded Cipher Message"):
    """
    Modal that accepts user input and returns a Base64-encoded version
    of the submitted text.
    """

    input_modal = discord.ui.TextInput(
        label="Your Message",
        style=discord.TextStyle.paragraph,
        placeholder="No horny please :)",
        required=True
    )

    async def on_submit(self, interaction: Interaction) -> None:
        """
        Triggered when the user submits the modal.

        Encodes the input text into Base64 and sends it back
        as a public response message.
        """
        encoded = base64.b64encode(self.input_modal.value.encode("utf-8"))
        await interaction.response.send_message(
            encoded.decode("utf-8"),
            ephemeral=False
        )


class Base64Message(commands.Cog):
    """
    Cog that provides Base64 encode/decode utilities via:
    - A slash command that opens a modal for encoding text
    - A message context menu command that decodes Base64 content
    """

    def __init__(self, bot: commands.Bot) -> None:
        """
        Registers the context menu command when the cog is loaded.
        """
        self.bot = bot
        self.reply_command = app_commands.ContextMenu(
            name="Decode Cipher",
            callback=self.reply_decode_cipher,
        )
        bot.tree.add_command(self.reply_command)

    async def reply_decode_cipher(
        self,
        interaction: discord.Interaction,
        message: discord.Message
    ) -> None:
        """
        Message context menu callback.

        Attempts to decode the selected message as Base64.
        - On success: sends the decoded text ephemerally.
        - On failure: sends a custom error emoji ephemerally.
        """
        try:
            decoded = base64.b64decode(message.content).decode("utf-8")
            await interaction.response.send_message(
                content=decoded,
                ephemeral=True
            )
        except binascii.Error:
            await interaction.response.send_message(
                "<:adudakqua:1408053029659218015>",
                ephemeral=True
            )

    @app_commands.command(
        name="cipher",
        description="Converts the given text to base64 cipher"
    )
    async def handle_base64(self, interaction: discord.Interaction) -> None:
        """
        Slash command that opens a modal allowing the user
        to input text for Base64 encoding.
        """
        await interaction.response.send_modal(InputModal())


async def setup(bot: commands.Bot):
    """
    Standard cog setup entry point for discord.py extensions.
    """
    await bot.add_cog(Base64Message(bot))
