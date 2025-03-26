# Discord Bot - Funções de Gerenciamento e Automação
Este bot do Discord oferece funcionalidades automatizadas para gerenciar servidores e realizar tarefas como limpar mensagens, fazer farm de horas em calls, sair de servidores automaticamente, entre outros. O bot é baseado em diferentes módulos, cada um responsável por uma função específica, acessada através de um menu interativo (select).
Funcionalidades

O bot contém os seguintes módulos:
cl.py

    Descrição: Limpa mensagens de um usuário específico em um servidor.

    Como usar: Quando você invocar este comando, o bot abrirá um select para escolher o usuário cujas mensagens serão limpas.

farm.py

    Descrição: Realiza o farm de horas na sua conta em uma call específica.

    Como usar: Após selecionar a opção desejada, o bot começará a acumular horas automaticamente na call especificada.

leave.py

    Descrição: Sai automaticamente dos servidores que o bot está.

    Como usar: Ao invocar esse comando, o bot pedirá a confirmação para sair de todos os servidores que está participando.

modal.py

    Descrição: Recebe o token do Discord para realizar todas as funções acima.

    Como usar: O bot solicita o seu token de autenticação para garantir que todas as funções sejam realizadas na sua conta do Discord.

Como Rodar o Bot
Requisitos

    Python 3.8 ou superior

    Biblioteca discord.py (recomendada a versão mais recente)

    Outros módulos necessários (veja as dependências abaixo)

Dependências

    Instale as dependências necessárias: 
# pip install nextcord
# pip install websockets
# pip uninstall discord.py
