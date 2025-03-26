import requests
import time
import random
import nextcord

async def clear_dm(interaction: nextcord.Interaction):
    token = interaction.client.user_token

    if not token:
        await interaction.response.send_message(
            "Por favor, configure seu token primeiro!", ephemeral=True
        )
        return

    await interaction.response.send_modal(ClearDMModal())

class ClearDMModal(nextcord.ui.Modal):
    channel_id_input = nextcord.ui.TextInput(
        label="ID do Canal",
        placeholder="Insira o ID do canal da DM",
        required=True,
        max_length=50
    )

    def __init__(self):
        super().__init__(title="Limpar DM")
        self.add_item(self.channel_id_input)

    async def callback(self, interaction: nextcord.Interaction):
        channel_id = self.channel_id_input.value
        token = interaction.client.user_token

        await interaction.response.send_message("Iniciando a limpeza das mensagens...", ephemeral=True)

        messages = fetch_messages(token, channel_id)
        
        if not messages:
            await interaction.followup.send("Erro ao buscar mensagens ou nenhuma mensagem encontrada.", ephemeral=True)
            return

        delete_messages(token, channel_id, messages)
        await interaction.followup.send(f"Mensagens deletadas: {len(messages)}", ephemeral=True)

def fetch_messages(token, channel_id):
    headers = {"Authorization": token, "User-Agent": "Mozilla/5.0"}
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    messages = []

    while True:
        params = {"limit": 100}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            return []
        
        data = response.json()
        if not data:
            break

        messages.extend([msg["id"] for msg in data])

        if len(data) < 100:
            break

    return messages

def delete_messages(token, channel_id, messages):
    headers = {"Authorization": token, "User-Agent": "Mozilla/5.0"}
    url_template = f"https://discord.com/api/v9/channels/{channel_id}/messages/{{}}"
    
    for msg_id in messages:
        while True:
            response = requests.delete(url_template.format(msg_id), headers=headers)

            if response.status_code == 204:
                break
            elif response.status_code == 429:
                time.sleep(response.json().get("retry_after", 1))
            else:
                break

            time.sleep(random.uniform(2.5, 3.5))
