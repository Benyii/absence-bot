import discord
import aiosqlite
from datetime import datetime, timedelta
from views.absence_button_view import AbsenceButtonView
import os

class AbsenceModal(discord.ui.Modal, title='Registrar Ausencia'):
    def __init__(self, interaction: discord.Interaction):
        super().__init__(title="Registrar Ausencia")
        self.interaction = interaction
        self.dias = discord.ui.TextInput(label='Días de ausencia', style=discord.TextStyle.short, placeholder='Número de días de ausencia', required=True, custom_id='dias_ausencia')
        self.motivo = discord.ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph, placeholder='Describe el motivo de tu ausencia', required=True, custom_id='motivo_ausencia')
        self.tipo = discord.ui.TextInput(label='Tipo de ausencia (AAR o ATC)', style=discord.TextStyle.short, placeholder='Indica AAR o ATC', required=True, custom_id='tipo_ausencia')

        self.add_item(self.dias)
        self.add_item(self.motivo)
        self.add_item(self.tipo)

    async def on_submit(self, interaction: discord.Interaction):
        dias = int(self.dias.value)
        motivo = self.motivo.value
        tipo = self.tipo.value.upper()

        if dias <= 0:
            await interaction.response.send_message('El número de días debe ser un número positivo.', ephemeral=True)
            return

        if dias > 7:
            await interaction.response.send_message('Aquí solo se pueden postear ausencias con un máximo de 7 días. En caso de realizarse una ausencia por más tiempo o indefinido, realizar la solicitud por el canal #generar-ticket', ephemeral=True)
            return

        if tipo not in ['AAR', 'ATC']:
            await interaction.response.send_message('El tipo de ausencia debe ser AAR o ATC.', ephemeral=True)
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
            public_message = await public_channel.send(f'Una **ausencia de:** {user.mention} se encuentra en revisión por el Command Staff.')

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

            # Enviar mensaje al LOG_CHANNEL con menciones a los roles
            log_channel = self.interaction.client.get_channel(int(os.getenv('LOG_CHANNEL_ID')))
            if log_channel:
                role_mention_1 = '<@&1131273125376557093>'
                role_mention_2 = '<@&1131273125322043510>'
                await log_channel.send(
                    content=f'{role_mention_1} {role_mention_2}\nNueva ausencia registrada por {user.mention}.',
                    embed=embed
                )

        await interaction.response.send_message(f'Se ha registrado tu ausencia para revisión. Recibirás un mensaje en caso de que tu ausencia sea aprobada.', ephemeral=True)
