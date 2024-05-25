import discord
from discord import app_commands
import aiosqlite
import os

async def terminarausenciaid(interaction: discord.Interaction, absence_id: int):
    try:
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id FROM absences WHERE id = ? AND status = ?', (absence_id, 'approved')) as cursor:
                row = await cursor.fetchone()

            if not row:
                await interaction.response.send_message('No se encontró una ausencia aprobada con ese ID.', ephemeral=True)
                return

            user_id, start_date, end_date, status, reason, public_message_id, approved_message_id, approver_user_id = row
            await db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id))
            await db.commit()

            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            try:
                approved_message = await public_channel.fetch_message(approved_message_id)
                embed = approved_message.embeds[0]
                embed.color = discord.Color.red()
                embed.set_field_at(3, name="Estado", value="Finalizada", inline=False)
                await approved_message.edit(embed=embed)
                await approved_message.clear_reactions()
                await approved_message.add_reaction('✅')
            except discord.NotFound:
                print(f"Approved message with ID {approved_message_id} not found.")

        await interaction.response.send_message(f'La ausencia con ID {absence_id} ha sido marcada como terminada.', ephemeral=True)
    except Exception as e:
        print(f'Error in /terminarausenciaid command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='terminarausenciaid', description="Termina una ausencia por ID", callback=terminarausenciaid))
