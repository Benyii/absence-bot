import discord
import aiosqlite
import os

class AbsenceButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Aprobar", style=discord.ButtonStyle.green, custom_id="approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            print("Approve button clicked.")
            if not any(role.id == int(os.getenv('APPROVER_ROLE_ID')) for role in interaction.user.roles):
                await interaction.response.send_message('No tienes permiso para realizar esta acción.', ephemeral=True)
                return

            user_id = int(interaction.message.embeds[0].footer.text)
            print(f"Processing approval for user ID: {user_id}")

            async with aiosqlite.connect('absences.db') as db:
                async with db.execute('SELECT * FROM absences WHERE user_id = ? AND status = ?', (user_id, 'pending')) as cursor:
                    row = await cursor.fetchone()

                if row:
                    print(f"Found row: {row}")
                    absence_id, user_id, start_date, end_date, status, reason, public_message_id, _ = row
                    await db.execute('UPDATE absences SET status = ? WHERE user_id = ?', ('approved', user_id))
                    await db.commit()
                    user = interaction.client.get_user(user_id)
                    await user.send(f'Su ausencia ha sido aprobada.')
                    await interaction.response.send_message(f'Ausencia aprobada para {user.mention}', ephemeral=True)

                    updated_content = interaction.message.content.replace("[EN REVISIÓN]", "[APROBADO]")
                    await interaction.message.edit(content=updated_content, view=None)

                    public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
                    try:
                        public_message = await public_channel.fetch_message(public_message_id)
                        await public_message.delete()
                    except discord.NotFound:
                        print(f"Public message with ID {public_message_id} not found.")
                    
                    approved_message = await public_channel.send(
                        f':green_circle: **Ausencia de:** {user.mention} (ID: {absence_id}) - **Desde:** {start_date} - **Hasta:** {end_date} - **Motivo:** {reason}'
                    )
                    await approved_message.add_reaction('⏳')

                    await db.execute('UPDATE absences SET approved_message_id = ? WHERE id = ?', (approved_message.id, absence_id))
                    await db.commit()
                else:
                    print(f"No row found for user ID: {user_id}")
                    await interaction.response.send_message('Ausencia no encontrada o ya procesada.', ephemeral=True)
        except Exception as e:
            print(f'Error in approve button: {e}')
            await interaction.response.send_message(f'Error al aprobar: {e}', ephemeral=True)

    @discord.ui.button(label="Denegar", style=discord.ButtonStyle.red, custom_id="deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            print("Deny button clicked.")
            if not any(role.id == int(os.getenv('APPROVER_ROLE_ID')) for role in interaction.user.roles):
                await interaction.response.send_message('No tienes permiso para realizar esta acción.', ephemeral=True)
                return

            user_id = int(interaction.message.embeds[0].footer.text)
            print(f"Processing denial for user ID: {user_id}")

            async with aiosqlite.connect('absences.db') as db:
                async with db.execute('SELECT * FROM absences WHERE user_id = ? AND status = ?', (user_id, 'pending')) as cursor:
                    row = await cursor.fetchone()

                if row:
                    print(f"Found row: {row}")
                    absence_id, user_id, start_date, end_date, status, reason, public_message_id, _ = row
                    class DenyReasonModal(discord.ui.Modal, title='Motivo de la Denegación'):
                        reason = discord.ui.TextInput(label='Motivo', style=discord.TextStyle.paragraph)

                        async def on_submit(self, interaction: discord.Interaction):
                            async with aiosqlite.connect('absences.db') as db:
                                await db.execute('UPDATE absences SET status = ?, reason = ? WHERE user_id = ?', ('denied', self.reason.value, user_id))
                                await db.commit()
                            user = interaction.client.get_user(user_id)
                            await user.send(f'Tu ausencia ha sido denegada por el motivo: {self.reason.value}')
                            await interaction.response.send_message(f'Ausencia denegada para {user.mention} con el motivo: {self.reason.value}', ephemeral=True)
                            updated_content = interaction.message.content.replace("[EN REVISIÓN]", "[DENEGADO]")
                            await interaction.message.edit(content=updated_content, view=None)

                            log_channel = interaction.client.get_channel(int(os.getenv('LOG_CHANNEL_ID')))
                            log_message = await log_channel.fetch_message(interaction.message.id)
                            embed = log_message.embeds[0]
                            embed.add_field(name="Motivo de la Denegación", value=self.reason.value)
                            await log_message.edit(embed=embed)

                            public_channel = interaction.client.get_channel(int(os.getenv('PUBLIC_CHANNEL_ID')))
                            try:
                                public_message = await public_channel.fetch_message(public_message_id)
                                await public_message.delete()
                            except discord.NotFound:
                                print(f"Public message with ID {public_message_id} not found.")

                    modal = DenyReasonModal()
                    await interaction.response.send_modal(modal)
                else:
                    print(f"No row found for user ID: {user_id}")
                    await interaction.response.send_message('Ausencia no encontrada o ya procesada.', ephemeral=True)
        except Exception as e:
            print(f'Error in deny button: {e}')
            await interaction.response.send_message(f'Error al denegar: {e}', ephemeral=True)
