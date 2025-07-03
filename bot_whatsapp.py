
# 1. IMPORTAÇÕES
from flask import Flask, request
import sqlite3
import json
from datetime import datetime
import requests
import os

# 2. CONFIGURAÇÕES E CONSTANTES GLOBAIS
app = Flask(__name__)

print("--- VERIFICANDO VARIÁVEIS DE AMBIENTE ---")
print(f"PHONE_NUMBER_ID carregado: {os.environ.get('PHONE_NUMBER_ID')}")
print(f"VERIFY_TOKEN carregado: {os.environ.get('VERIFY_TOKEN')}")
print(f"WHATSAPP_TOKEN carregado: {os.environ.get('WHATSAPP_TOKEN')}")
print("-----------------------------------------")

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# -- Mensagens Iniciais e de Coleta de Dados --
MENSAGEM_BEM_VINDO = "Bem vindo, Casa Padim agradece seu contato."
PERGUNTA_NOME = "Para iniciar, poderia me informar o seu nome?"
PERGUNTA_CIDADE = "Obrigado, {nome}! Para prosseguir com seu atendimento, poderia me informar a cidade de onde você fala?"

# -- NÍVEL 1: Menu Principal --
MENSAGEM_MENU_PRINCIPAL = """
Ok, {nome}. Anotado!\n

Como podemos ajudá-lo(a) hoje?\n

\n1️⃣ Informações sobre nossos produtos/serviços
\n2️⃣ Suporte ou Atendimento
"""
RESPOSTAS_MENU_PRINCIPAL = {
    "1": "Para informações sobre nossos produtos e serviços, por favor, visite nosso catálogo online: [SEU LINK AQUI]."
}

# -- NÍVEL 2: Sub-menu de Suporte --
MENSAGEM_SUPORTE_SUBMENU = """
Entendido. Por favor, digite o número do setor que melhor representa sua demanda:\n

\n1️⃣ Financeiro
\n2️⃣ Comercial
\n3️⃣ Vendas
\n4️⃣ RH
\n5️⃣ Outros
"""


# Financeiro
MENSAGEM_FINANCEIRO_SUBMENU = "Setor Financeiro. Em que podemos ajudar?\n1️⃣ Boletos\n2️⃣ Contatos"
RESPOSTAS_FINANCEIRO_SUBMENU = {
    "1": "[RESPOSTA PROVISÓRIA] Para segunda via de boletos, acesse nosso portal do cliente.",
    "2": "[RESPOSTA PROVISÓRIA] Para outros assuntos financeiros, contate financeiro@casapadim.com.br."
}
# Comercial
MENSAGEM_COMERCIAL_SUBMENU = "Setor Comercial. Qual o assunto?\n1️⃣ Patrocínio\n2️⃣ Sugestão\n3️⃣ Precificação"
RESPOSTAS_COMERCIAL_SUBMENU = {
    "1": "[RESPOSTA PROVISÓRIA] Para propostas de patrocínio, por favor, envie seu projeto para marketing@casapadim.com.br.",
    "2": "[RESPOSTA PROVISÓRIA] Sua sugestão é muito bem-vinda! Por favor, envie para sugestoes@casapadim.com.br.",
    "3": "[RESPOSTA PROVISÓRIA] Para informações sobre preços, por favor, entre em contato com um de nossos vendedores."
}
# Vendas
MENSAGEM_VENDAS_SUBMENU = "Setor de Vendas. Sobre qual assunto?\n1️⃣ Contato de Vendedores\n2️⃣ Cadastro de Cliente"
RESPOSTA_CADASTRO_CLIENTE = "[RESPOSTA PROVISÓRIA] Para se cadastrar como nosso cliente, por favor, preencha o formulário em nosso site: [LINK CADASTRO]."
# RH
MENSAGEM_RH_SUBMENU = "Setor de RH. Qual o assunto?\n1️⃣ Envio de currículo"
RESPOSTAS_RH_SUBMENU = {
    "1": "Para enviar seu currículo, por favor, utilize o e-mail rh@casapadim.com.br. Boa sorte!"
}
# Outros
RESPOSTA_OUTROS = "[RESPOSTA PROVISÓRIA] Entendi. Para outros assuntos, por favor, aguarde que um de nossos atendentes irá te ajudar."



def ler_estado(numero_usuario):
    """Lê o estado atual e os dados de um usuário no banco de dados."""
    try:
        conexao = sqlite3.connect('vendedores.db')
        cursor = conexao.cursor()
        cursor.execute("SELECT estado, dados_json FROM conversas WHERE numero_usuario = ?", (numero_usuario,))
        resultado = cursor.fetchone()
        conexao.close()
        if resultado:
            return {"estado": resultado[0], "dados": json.loads(resultado[1] or '{}')}
        return None
    except sqlite3.Error as e:
        print(f"Erro ao ler estado: {e}")
        return None

def salvar_estado(numero_usuario, estado, dados):
    """Salva ou atualiza o estado de um usuário no banco de dados."""
    try:
        conexao = sqlite3.connect('vendedores.db')
        cursor = conexao.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO conversas (numero_usuario, estado, dados_json, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (numero_usuario, estado, json.dumps(dados), datetime.now()))
        conexao.commit()
        conexao.close()
    except sqlite3.Error as e:
        print(f"Erro ao salvar estado: {e}")

def apagar_estado(numero_usuario):
    """Apaga o registro de conversa de um usuário, finalizando o ciclo."""
    try:
        conexao = sqlite3.connect('vendedores.db')
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM conversas WHERE numero_usuario = ?", (numero_usuario,))
        conexao.commit()
        conexao.close()
    except sqlite3.Error as e:
        print(f"Erro ao apagar estado: {e}")


def buscar_vendedor_por_cidade(cidade_cliente):
    """Busca vendedores no banco de dados pela cidade informada."""
    vendedores_encontrados = []
    try:
        conexao = sqlite3.connect('vendedores.db')
        cursor = conexao.cursor()
        cidade_formatada = cidade_cliente.lower().strip()
        
        cursor.execute('''
            SELECT nome, contato, tipo_vendedor FROM vendedores, json_each(vendedores.cidades_atendidas)
            WHERE json_each.value = ?
        ''', (cidade_formatada,))
        
        resultados = cursor.fetchall()
        for resultado in resultados:
            vendedores_encontrados.append({
                "nome": resultado[0], "contato": resultado[1], "tipo_vendedor": resultado[2]
            })
    except sqlite3.Error as e:
        print(f"Erro ao buscar vendedor: {e}")
        return []
    finally:
        if conexao:
            conexao.close()
    return vendedores_encontrados

def formatar_resposta_vendedor(vendedores):
    """Cria a mensagem de texto final com os dados dos vendedores."""
    if not vendedores:
        return "No momento, não encontramos um vendedor específico para sua região. Por favor, entre em contato com nossa equipe interna na matriz."
    
    resposta = "Encontrei esses contatos para sua região:\n\n"
    for vendedor in vendedores:
        tipo = vendedor['tipo_vendedor'].replace("externo", "Vendedor Externo").replace("interno", "Vendedor Interno")
        resposta += f"👤 *{vendedor['nome']}* ({tipo})\n"
        if vendedor['contato']:
            resposta += f"📞 *Contato:* {vendedor['contato']}\n"
        resposta += "--------------------\n"
    return resposta

def enviar_mensagem_whatsapp(numero_usuario, mensagem):

    
    # Pega as credenciais do ambiente
    token = os.environ.get("WHATSAPP_TOKEN")
    phone_id = os.environ.get("PHONE_NUMBER_ID")

    # Verificação de segurança para garantir que as variáveis foram carregadas
    if not token or not phone_id:
        print("ERRO CRÍTICO: Token ou Phone Number ID não encontrados nas variáveis de ambiente.")
        return

    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    
    headers = {
        # A MÁGICA ESTÁ AQUI: .strip() remove espaços/quebras de linha invisíveis
        "Authorization": "Bearer " + token.strip(),
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero_usuario,
        "text": { "body": mensagem }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        # Lança um erro se a requisição falhar (status code 4xx ou 5xx)
        response.raise_for_status() 
        print(f"Mensagem enviada com sucesso para {numero_usuario}!")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")


# =======================================================
# 5. FUNÇÃO PRINCIPAL DE LÓGICA DO BOT (O CÉREBRO)
# =======================================================
def processar_mensagem(mensagem_usuario, numero_usuario):
    info_usuario = ler_estado(numero_usuario)
    
    if not info_usuario:
        salvar_estado(numero_usuario, "aguardando_nome", {})
        return f"{MENSAGEM_BEM_VINDO}\n\n{PERGUNTA_NOME}"

    estado_atual = info_usuario["estado"]
    dados_atuais = info_usuario["dados"]
    
    if estado_atual == "aguardando_nome":
        nome = mensagem_usuario.strip()
        dados_atuais["nome"] = nome
        salvar_estado(numero_usuario, "aguardando_cidade", dados_atuais)
        return PERGUNTA_CIDADE.format(nome=nome)

    elif estado_atual == "aguardando_cidade":
        cidade = mensagem_usuario.strip()
        dados_atuais["cidade"] = cidade
        salvar_estado(numero_usuario, "aguardando_opcao_menu", dados_atuais)
        nome = dados_atuais["nome"]
        return MENSAGEM_MENU_PRINCIPAL.format(nome=nome)

    elif estado_atual == "aguardando_opcao_menu":
        escolha = mensagem_usuario.strip()
        if escolha == "1":
            apagar_estado(numero_usuario)
            return RESPOSTAS_MENU_PRINCIPAL["1"]
        elif escolha == "2":
            salvar_estado(numero_usuario, "aguardando_opcao_suporte", dados_atuais)
            return MENSAGEM_SUPORTE_SUBMENU
        else:
            return "Opção inválida. Por favor, digite 1 ou 2."

    elif estado_atual == "aguardando_opcao_suporte":
        escolha = mensagem_usuario.strip()
        if escolha == "1": # Financeiro
            salvar_estado(numero_usuario, "aguardando_opcao_financeiro", dados_atuais)
            return MENSAGEM_FINANCEIRO_SUBMENU
        elif escolha == "2": # Comercial
            salvar_estado(numero_usuario, "aguardando_opcao_comercial", dados_atuais)
            return MENSAGEM_COMERCIAL_SUBMENU
        elif escolha == "3": # Vendas
            salvar_estado(numero_usuario, "aguardando_opcao_vendas", dados_atuais)
            return MENSAGEM_VENDAS_SUBMENU
        elif escolha == "4": # RH
            salvar_estado(numero_usuario, "aguardando_opcao_rh", dados_atuais)
            return MENSAGEM_RH_SUBMENU
        elif escolha == "5": # Outros
            apagar_estado(numero_usuario)
            return RESPOSTA_OUTROS
        else:
            return "Opção de setor inválida."

    elif estado_atual == "aguardando_opcao_financeiro":
        resposta = RESPOSTAS_FINANCEIRO_SUBMENU.get(mensagem_usuario.strip())
        apagar_estado(numero_usuario)
        return resposta or "Opção inválida."
    
    elif estado_atual == "aguardando_opcao_comercial":
        resposta = RESPOSTAS_COMERCIAL_SUBMENU.get(mensagem_usuario.strip())
        apagar_estado(numero_usuario)
        return resposta or "Opção inválida."

    elif estado_atual == "aguardando_opcao_rh":
        resposta = RESPOSTAS_RH_SUBMENU.get(mensagem_usuario.strip())
        apagar_estado(numero_usuario)
        return resposta or "Opção inválida."
        
    elif estado_atual == "aguardando_opcao_vendas":
        escolha = mensagem_usuario.strip()
        if escolha == "1": # Contato de Vendedores
            cidade_cliente = dados_atuais.get("cidade")
            vendedores = buscar_vendedor_por_cidade(cidade_cliente)
            resposta = formatar_resposta_vendedor(vendedores)
            apagar_estado(numero_usuario)
            return resposta
        elif escolha == "2": # Cadastro de Cliente
            apagar_estado(numero_usuario)
            return RESPOSTA_CADASTRO_CLIENTE
        else:
            return "Opção inválida."

    return "Desculpe, não entendi. Vamos começar de novo."



@app.route('/webhook', methods=['GET', 'POST'])
def webhook_whatsapp():
    if request.method == 'GET':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge')
        return 'Erro de verificação', 403

    if request.method == 'POST':
        dados = request.get_json()
        if dados and dados.get('object') == 'whatsapp_business_account':
            try:
                mudanca = dados['entry'][0]['changes'][0]
                if mudanca['field'] == 'messages':
                    mensagem = mudanca['value']['messages'][0]
                    numero_usuario = mensagem['from']
                    mensagem_recebida = mensagem['text']['body']
                    
                    print(f"Mensagem de '{numero_usuario}': '{mensagem_recebida}'")
                    
                    resposta_bot = processar_mensagem(mensagem_recebida, numero_usuario)
                    
                    print(f"Resposta do bot: {resposta_bot}")

                    # AQUI ESTÁ A "BOCA" DO BOT!
                    if resposta_bot:
                        enviar_mensagem_whatsapp(numero_usuario, resposta_bot)

            except (KeyError, IndexError):
                pass
        
        return 'OK', 200

    return 'Método não suportado', 405

if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
# /agradecimento Casa Padim agradece seu contato, tenha um bom dia/uma boa tarde!
# /encominhar Irei te encaminhar o contato do nosso representante que atende na sua região.
# /aguarde Aguarde um momento que estarei iniciando seu atendimento!
# /boleto Estarei encaminhando seu contato para o setor do financeiro.
# /curriculo Você pode enviar o currículo para o email do RH, que é o setor responsável, e aguardar a resposta!
#Email para envio do currículo: rh@casapadim.com.br

# /Obrigado Agradecemos por utilizar nossos serviços! Esperamos trabalhar com você novamente em breve.
# /reclamação Obrigada! Sua reclamação será encaminhada para setor da Qualidade, é necessário aguardar o retorno do setor.
''' /recusa Prezado(a) - -,

Agradecemos imensamente pelo seu contato e pelo convite para participar como patrocinadores.

No entanto, após análise interna, informamos que, no momento, não será possível atender à solicitação de patrocínio. 
Desejamos muito sucesso em seu projeto e ficamos à disposição para futuras oportunidades.

Casa Padim agradece o seu contato!'''

# /registroreclamação Sua reclamação foi registrada, é necessário aguardar o retorno do setor responsável.

''' /atendente Olá, bom dia/boa tarde.
Me chamo Thaísa e estarei iniciando seu atendimento!
Em que posso ajudar?'''

# /numero Esse número que encaminhei também é WhatsApp, pode entrar em contato com ele, que ele irá te fornecer as informações necessárias!

#Nome do atendendente acima da mensagem
#Mensagem de terminado o atendimento 
#Atendentes: 1, 2 e 3

'''Mensagem automática para escolha de opções
 Ex.: Olá! Seja bem-vindo(a) a Casa Padim.

Como podemos ajudá-lo(a) hoje?

⿡ Informações sobre nossos produtos/serviços - Me informe por favor de qual cidade você é? - Aguarde um momento enquanto eu verfico o representante que atende na sua região.
    
⿢ Suporte ou atendimento ao cliente
     - Você gostaria de fazer? 1. Registrar uma reclamação 2. Pedido 3. Cadastro
⿣ Falar com um atendente
    Olá, bom dia/boa tarde.
Me chamo Thaísa e estarei iniciando seu atendimento!
Em que posso ajudar?'''


# Audio - Não é possivel ouvir audios se puder envie mensagem em texto;



'''Setorização do ponto 2'''
#Calendário de entregas

