import discord
from discord import app_commands
import aiosqlite
import os

async def list_ausencias(interaction: discord.Interaction):
    try:
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id FROM absences') as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message('No hay ausencias registradas.', ephemeral=True)
            return

        embed = discord.Embed(title="Lista de Ausencias")
        for row in rows:
            absence_id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id = row
            user = interaction.client.get_user(user_id)
            embed.add_field(name=f"{user.display_name} (ID: {absence_id})", value=f"Desde: {start_date}\nHasta: {end_date}\nEstado: {status}\nMotivo: {reason}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'Error in /list_ausencias command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='list_ausencias', description="Muestra todas las ausencias y su estado actual", callback=list_ausencias))
