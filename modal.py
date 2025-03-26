import nextcord

class ConfigAccountModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Configurar Conta")
        self.token_input = nextcord.ui.TextInput(
            label="Token",
            required=True,
            placeholder="Insira seu token"
        )
        self.add_item(self.token_input)

    async def callback(self, interaction: nextcord.Interaction):
        token = self.token_input.value
        interaction.client.user_token = token  # Armazena o token no objeto client

        await interaction.response.send_message(
            "Token configurado com sucesso!", ephemeral=True
        )
