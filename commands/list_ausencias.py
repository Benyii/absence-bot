import discord
from discord import app_commands
import aiosqlite

async def list_ausencias(interaction: discord.Interaction):
    try:
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id, tipo FROM absences') as cursor:
                rows = await cursor.fetchall()

        if not rows:
            await interaction.response.send_message('No hay ausencias registradas.', ephemeral=True)
            return

        embed = discord.Embed(title="Lista de Ausencias")
        for row in rows:
            absence_id, user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id, tipo = row
            user = interaction.client.get_user(user_id)
            approver_user = interaction.client.get_user(approver_user_id)
            estado = "Activo" if status == "approved" else "Finalizada"
            embed_color = discord.Color.green() if status == "approved" else discord.Color.red()
            embed = discord.Embed(title=f"Ausencia - ID: {absence_id}", color=embed_color)
            embed.add_field(name="Nombre", value=user.mention, inline=False)
            embed.add_field(name="Fecha inicio", value=start_date, inline=False)
            embed.add_field(name="Fecha termino", value=end_date, inline=False)
            embed.add_field(name="Motivo", value=reason, inline=False)
            embed.add_field(name="Tipo de Ausencia", value=tipo, inline=False)
            embed.add_field(name="Estado", value=estado, inline=False)
            embed.add_field(name="Ausencia aprobada por", value=approver_user.mention, inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'Error in /list_ausencias command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='list_ausencias', description="Muestra todas las ausencias y su estado actual", callback=list_ausencias))
