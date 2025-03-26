import requests
import time
import random
import nextcord

async def leave_servers(interaction: nextcord.Interaction, token, bot_guild_id):
    await interaction.followup.send(
        " Limpeza de servidores iniciada com sucesso!", ephemeral=True
    )

    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0"
    }

    api_url = "https://discord.com/api/v9/users/@me/guilds"

    while True:
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            await interaction.followup.send(
                " Erro ao obter servidores. Verifique o token.", ephemeral=True
            )
            return

        guilds = response.json()

        if not guilds:
            await interaction.followup.send(
                " Não há servidores para limpar.", ephemeral=True
            )
            return

        # Lista para manter servidores onde o bot está e onde o usuário é o dono
        remaining_guilds = []

        for guild in guilds:
            guild_id = guild["id"]
            owner_id = guild.get("owner_id")

            # Se o bot estiver no servidor, não deve sair
            if str(guild_id) == str(bot_guild_id):
                remaining_guilds.append(guild)  # Mantém o servidor onde o bot está
                continue

            # Ignora servidores onde o usuário é o dono
            if str(owner_id) == str(interaction.user.id):
                remaining_guilds.append(guild)  # Mantém servidores onde o usuário é o dono
                continue

            leave_url = f"https://discord.com/api/v9/users/@me/guilds/{guild_id}"

            # Tenta sair do servidor
            while True:
                leave_response = requests.delete(leave_url, headers=headers)

                if leave_response.status_code == 204:
                    break  # Saiu com sucesso, continua com o próximo servidor

                elif leave_response.status_code == 429:
                    retry_after = leave_response.json().get("retry_after", 1)
                    time.sleep(retry_after)  # Espera o tempo indicado

                elif leave_response.status_code == 403:
                    break  # Sem permissão, pula para o próximo servidor

                elif leave_response.status_code == 401:
                    await interaction.followup.send(
                        " Token inválido. Verifique e tente novamente.", ephemeral=True
                    )
                    return
                else:
                    break  # Outros erros, pula para o próximo

            time.sleep(2 + random.random() * 2)  # Aguarda entre 2 e 4 segundos

        # Se o bot saiu de todos os servidores que ele não é o dono
        if len(remaining_guilds) == len(guilds):
            await interaction.followup.send(
                " Saiu de todos os servidores com sucesso!", ephemeral=True
            )
            return

        # Se o bot já saiu de todos os servidores que não são do usuário ou do bot
        if len(remaining_guilds) == 1:  # Apenas o servidor onde o bot está ou o usuário é dono
            await interaction.followup.send(
                " Limpeza de servidores completa !", ephemeral=True
            )
            return

        time.sleep(3)  # Pequena pausa antes de tentar novamente
