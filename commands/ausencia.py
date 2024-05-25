import discord
from discord import app_commands
import aiosqlite
from datetime import datetime, timedelta
from views.absence_button_view import AbsenceButtonView
import os

async def ausencia(interaction: discord.Interaction, dias: int, motivo: str):
    try:
        if dias <= 0:
            await interaction.response.send_message('El número de días debe ser un número positivo.', ephemeral=True)
            return

        if dias > 7:
            await interaction.response.send_message('Aquí solo se pueden postear ausencias con un máximo de 7 días. En caso de realizarse una ausencia por más tiempo o indefinido, realizar la solicitud por el canal #generar-ticket', ephemeral=True)
            return

        if interaction.channel.id != int(os.getenv('PUBLIC_CHANNEL_ID')):
            await interaction.response.send_message('Este comando solo puede ser utilizado en el canal de #ausencias.', ephemeral=True)
            return

        user = interaction.user
        async with aiosqlite.connect('absences.db') as db:
            async with db.execute('SELECT * FROM absences WHERE user_id = ? AND status IN (?, ?)', (user.id, 'pending', 'approved')) as cursor:
                row = await cursor.fetchone()

            if row:
                await interaction.response.send_message('Ya tienes una ausencia en curso o pendiente. Solo puedes registrar una nueva ausencia cuando la actual haya finalizado.', ephemeral=True)
                return

            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=dias)
            formatted_start_date = start_date.strftime('%d-%m-%Y')
            formatted_end_date = end_date.strftime('%d-%m-%Y')

            # Enviar el mensaje público y obtener el ID
            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            public_message = await public_channel.send(f'[EN REVISIÓN] **Ausencia de:** {user.mention} - **Días:** {dias} - **Motivo:** {motivo} (ID: {user.id})')

            validation_channel = interaction.client.get_channel(int(os.getenv('VALIDATION_CHANNEL_ID')))
            view = AbsenceButtonView()
            embed = discord.Embed(description=f'**Días:** {dias} - **Motivo:** {motivo}')
            embed.set_footer(text=str(user.id))
            validation_message = await validation_channel.send(
                f'[EN REVISIÓN] **Ausencia de:** {user.mention} (ID: {user.id})',
                embed=embed,
                view=view
            )

            await db.execute('''
                INSERT INTO absences (user_id, start_date, end_date, status, reason, message_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user.id, formatted_start_date, formatted_end_date, 'pending', motivo, public_message.id))
            await db.commit()

        await interaction.response.send_message(f'Se ha registrado tu ausencia para revisión.', ephemeral=True)
    except Exception as e:
        print(f'Error in /ausencia command: {e}')

def setup(bot):
    bot.tree.add_command(app_commands.Command(name='ausencia', description="Registra una ausencia indicando el número de días y el motivo", callback=ausencia))
