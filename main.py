import json
import nextcord
from nextcord.ext import commands
from cl import clear_dm  # Certifique-se de que este módulo existe
import farm  # Certifique-se de que este módulo existe
from modal import ConfigAccountModal  # Modal para configurar conta
from leave import leave_servers  # Importa a função leave_servers

intents = nextcord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.user_token = None  # Inicializa a variável para armazenar o token

# Função para carregar estado da view a partir de um arquivo JSON
def load_state():
    try:
        with open('panel_state.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Função para salvar o estado da view em um arquivo JSON
def save_state(state):
    with open('panel_state.json', 'w') as f:
        json.dump(state, f)

# Classe para o painel de interação com botões
class ConfirmButton(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(nextcord.ui.Button(label="Confirmar", style=nextcord.ButtonStyle.green, custom_id="confirm_button"))
        self.add_item(nextcord.ui.Button(label="Ignorar", style=nextcord.ButtonStyle.red, custom_id="ignore_button"))
    
    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.user != bot.user:
            return True
        return False

    async def on_button_click(self, interaction: nextcord.Interaction):
        if interaction.custom_id == "confirm_button":
            await interaction.response.send_message("Você confirmou a ação!", ephemeral=True)
        elif interaction.custom_id == "ignore_button":
            await interaction.response.send_message("Você ignorou a ação.", ephemeral=True)
        
        # Após a interação, podemos remover os botões para garantir que não sejam clicados novamente
        await interaction.message.edit(view=None)

# Classe MainView e MainSelect conforme o código original
class MainView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Mantém a View ativa indefinidamente
        self.add_item(MainSelect())  # Adiciona o Select no início

    async def update_view(self, interaction: nextcord.Interaction):
        """Método para atualizar a View quando necessário."""
        await interaction.message.edit(view=self)

class MainSelect(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(
                label="Configurar Conta",
                description="Configurar seu token",
                value="configure_account"
            ),
            nextcord.SelectOption(
                label="Clear DM",
                description="Limpa as dm com alguém específico",
                value="clear_dm"
            ),
            nextcord.SelectOption(
                label="Farm Call",
                description="Entra em uma call para farmar horas na sua conta",
                value="farm_call"
            ),
            nextcord.SelectOption(
                label="Clear Serves",
                description="Sai de todos servidores",
                value="leave_servers"
            )
        ]
        super().__init__(
            placeholder="Escolha uma opção...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: nextcord.Interaction):
        selected = self.values[0]

        if selected == "configure_account":
            await interaction.response.send_modal(ConfigAccountModal())
        
        elif selected == "clear_dm":
            await clear_dm(interaction)
        
        elif selected == "farm_call":
            await farm.farm_call(interaction)
        
        elif selected == "leave_servers":
            token = interaction.client.user_token  # Obtém o token configurado
            if token:
                bot_guild_id = interaction.guild.id  # Obtenha o ID do servidor onde o comando foi executado
                await interaction.response.defer()  # Adia a resposta
                await leave_servers(interaction, token, bot_guild_id)  # Passa o bot_guild_id para a função leave_servers
            else:
                await interaction.response.send_message(
                    "Por favor, configure seu token primeiro!", ephemeral=True
                )

        # Atualiza a mensagem com a view diretamente, sem tentar acessar o atributo 'view'
        new_view = MainView()  # Crie a view novamente após a interação
        await interaction.message.edit(view=new_view)

@bot.event
async def on_modal_submit(interaction: nextcord.Interaction, modal: ConfigAccountModal):
    token = modal.token  # Obtém o token do modal
    interaction.client.user_token = token  # Armazena o token globalmente

    await interaction.followup.send("Token configurado com sucesso!", ephemeral=True)

@bot.slash_command(name="painel", description="Abre o Painel Multiuso")
async def painel(interaction: nextcord.Interaction):
    # Verifica se o comando foi invocado em um servidor
    if interaction.guild is None:
        await interaction.response.send_message(
            "Este comando não pode ser usado em mensagens diretas (DM).", ephemeral=True
        )
        return

    # Verifica se o usuário que invocou o comando é o dono do servidor
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message(
            "Você não tem permissão para usar esse comando.", ephemeral=True
        )
        return

    embed = nextcord.Embed(
        title="Manutenção da conta",
        description=(
            "Para pegar seu token, [clique aqui](https://www.youtube.com/watch?v=bMjXRDG3aHA).\n"
            "Projeto em fase beta, reporte qualquer bug adicionando @gqai"
        ),
        color=nextcord.Color.from_rgb(0, 0, 0)
    )
    embed.set_image(url="https://i.pinimg.com/736x/a6/34/0c/a6340c131b5283ab9e1abc15a15bb8e9.jpg")

    # Criando a View e enviando a mensagem com a view associada
    view = MainView()
    # Envia a mensagem com o painel para o canal onde o comando foi usado
    message = await interaction.response.send_message(embed=embed, view=view)

    # Salva o estado da view no arquivo para persistência
    save_state({'message_id': message.id, 'guild_id': interaction.guild.id})

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

    # Carregar estado persistido e enviar painel caso haja estado salvo
    state = load_state()
    if state:
        channel = bot.get_channel(state['guild_id'])
        message = await channel.fetch_message(state['message_id'])
        view = MainView()  # A view é reconstruída a cada reinício
        await message.edit(view=view)

# Insira o token do bot aqui
bot.run("")  # Substitua "SEU_TOKEN_AQUI" pelo token correto do bot
