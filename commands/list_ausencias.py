import discord
from absence_bot import AbsenceBot
import aiosqlite

@bot.tree.command(name='list_ausencias', description="Muestra todas las ausencias y su estado actual")
async def list_ausencias(interaction: discord.Interaction):
    try:
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT * FROM absences') as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message('No hay ausencias registradas.', ephemeral=True)
            return

        embed = discord.Embed(title="Lista de Ausencias")
        for row in rows:
            absence_id, user_id, start_date, end_date, status, reason = row
            user = bot.get_user(user_id)
            embed.add_field(name=f"{user.display_name} (ID: {absence_id})", value=f"Desde: {start_date}\nHasta: {end_date}\nEstado: {status}\nMotivo: {reason}", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'Error in /list_ausencias command: {e}')
