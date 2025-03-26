import json
import asyncio
from websockets import connect, ConnectionClosedError
import nextcord

async def farm_call(interaction: nextcord.Interaction):
    token = interaction.client.user_token

    if not token:
        await interaction.response.send_message(
            "Por favor, configure seu token primeiro!",
            ephemeral=True
        )
        return

    await interaction.response.send_modal(FarmCallModal())

class FarmCallModal(nextcord.ui.Modal):
    call_id_input = nextcord.ui.TextInput(
        label="ID da Call",
        placeholder="Insira o ID da call",
        required=True,
        max_length=50
    )

    server_id_input = nextcord.ui.TextInput(
        label="ID do Servidor",
        placeholder="Insira o ID do servidor",
        required=True,
        max_length=50
    )

    def __init__(self):
        super().__init__(title="Farm Call")
        self.add_item(self.call_id_input)
        self.add_item(self.server_id_input)

    async def callback(self, interaction: nextcord.Interaction):
        call_id = self.call_id_input.value
        server_id = self.server_id_input.value
        token = interaction.client.user_token

        if not token:
            await interaction.response.send_message(
                "Por favor, configure seu token primeiro!",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Tentando entrar na call... ",
            ephemeral=True
        )

        success, error_message = await voice_joiner(token, server_id, call_id)

        if success:
            await interaction.followup.send("Você entrou na call com sucesso!", ephemeral=True)
        else:
            await interaction.followup.send(f"Erro ao tentar entrar na call: {error_message}", ephemeral=True)

async def voice_joiner(token: str, guild_id: str, channel_id: str):
    ws_url = "wss://gateway.discord.gg/?v=8&encoding=json"

    while True:
        try:
            async with connect(ws_url) as ws:
                identify_payload = {
                    "op": 2,
                    "d": {
                        "token": token,
                        "properties": {
                            "$os": "windows",
                            "$browser": "Discord",
                            "$device": "desktop"
                        }
                    }
                }

                await ws.send(json.dumps(identify_payload))
                await ws.recv()  # Response for identify

                voice_state_payload = {
                    "op": 4,
                    "d": {
                        "guild_id": guild_id,
                        "channel_id": channel_id,
                        "self_mute": False,
                        "self_deaf": False
                    }
                }

                await ws.send(json.dumps(voice_state_payload))

                async def keep_alive():
                    while True:
                        await ws.send(json.dumps({"op": 1, "d": None}))
                        await asyncio.sleep(30)

                asyncio.create_task(keep_alive())

                while True:
                    msg = await ws.recv()
                    if '"op": 3' in msg:
                        return True, None

        except ConnectionClosedError as e:
            print(f"Conexão fechada: {e}. Tentando reconectar em 5 segundos...")
        except Exception as e:
            print(f"Erro inesperado: {e}. Tentando reconectar em 5 segundos...")

        await asyncio.sleep(5)
