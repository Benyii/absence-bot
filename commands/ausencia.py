import discord
from discord import app_commands
from views.absence_modal import AbsenceModal
import os

async def ausencia(interaction: discord.Interaction):
    await interaction.response.send_modal(AbsenceModal(interaction))

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='ausencia', description="Registra una ausencia indicando el número de días y el motivo", callback=ausencia))
