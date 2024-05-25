import discord
import aiosqlite
from datetime import datetime, timedelta
from views.absence_button_view import AbsenceButtonView
import os

class AbsenceModal(discord.ui.Modal, title='Registrar Ausencia'):
    dias = discord.ui.TextInput(label='Días de ausencia', style=discord.TextStyle.short, placeholder='Número de días de ausencia', required=True, custom_id='dias')
    motivo = discord.ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph, placeholder='Describe el motivo de tu ausencia', required=True, custom_id='motivo')
    tipo = discord.ui.Select(
        placeholder='Selecciona el tipo de ausencia',
        options=[
            discord.SelectOption(label='AAR', description='Ausencia de Actividad Reducida'),
            discord.SelectOption(label='ATC', description='Ausencia de Tiempo Completo')
        ],
        custom_id='tipo'
    )

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction
        self.add_item(self.tipo)

    async def on_submit(self, interaction: discord.Interaction):
        dias = int(self.dias.value)
        motivo = self.motivo.value
        tipo = self.tipo.values[0]

        if dias <= 0:
            await interaction.response.send_message('El número de días debe ser un número positivo.', ephemeral=True)
            return

        if dias > 7:
            await interaction.response.send_message('Aquí solo se pueden postear ausencias con un máximo de 7 días. En caso de realizarse una ausencia por más tiempo o indefinido, realizar la solicitud por el canal #generar-ticket', ephemeral=True)
            return

        user = self.interaction.user
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
            public_channel = self.interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
            public_message = await public_channel.send(f'[EN REVISIÓN] **Ausencia de:** {user.mention} - **Días:** {dias} - **Motivo:** {motivo} (ID: {user.id})')

            await db.execute('''
                INSERT INTO absences (user_id, start_date, end_date, status, reason, public_message_id, tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user.id, formatted_start_date, formatted_end_date, 'pending', motivo, public_message.id, tipo))
            await db.commit()

            cursor = await db.execute('SELECT last_insert_rowid()')
            absence_id = (await cursor.fetchone())[0]
            await cursor.close()

            validation_channel = self.interaction.client.get_channel(int(os.getenv('VALIDATION_CHANNEL_ID')))
            view = AbsenceButtonView(absence_id)
            embed = discord.Embed(description=f'**Días:** {dias} - **Motivo:** {motivo}')
            embed.set_footer(text=str(absence_id))
            await validation_channel.send(
                f'[EN REVISIÓN] **Ausencia de:** {user.mention} (ID: {absence_id})',
                embed=embed,
                view=view
            )

        await interaction.response.send_message(f'Se ha registrado tu ausencia para revisión.', ephemeral=True)