import discord
from discord import app_commands
import aiosqlite

async def terminarausenciaid(interaction: discord.Interaction, absence_id: int):
    try:
        if not any(role.id == int(os.getenv('APPROVER_ROLE_ID')) for role in interaction.user.roles):
            await interaction.response.send_message('No tienes permiso para realizar esta acción.', ephemeral=True)
            return

        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT * FROM absences WHERE id = ? AND status = ?', (absence_id, 'approved')) as cursor:
                row = await cursor.fetchone()

            if not row:
                await interaction.response.send_message('No se encontró una ausencia aprobada con ese ID.', ephemeral=True)
                return

            user_id, start_date, end_date, motivo = row[1], row[2], row[3], row[5]
            await db.execute('UPDATE absences SET status = ? WHERE id = ?', ('finished', absence_id))
            await db.commit()

            user = interaction.client.get_user(user_id)
            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            async for message in public_channel.history(limit=200):
                if f'Ausencia ID: {absence_id}' in message.content:
                    await message.clear_reactions()
                    await message.add_reaction('✅')
                    await message.edit(content=message.content.replace(":green_circle:", ":red_circle:"))
                    break

        await interaction.response.send_message(f'La ausencia con ID {absence_id} ha sido marcada como terminada.', ephemeral=True)
    except Exception as e:
        print(f'Error in /terminarausenciaid command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='terminarausenciaid', description="Termina manualmente una ausencia específica por ID", callback=terminarausenciaid))
