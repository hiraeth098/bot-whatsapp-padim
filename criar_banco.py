
import sqlite3
import json

dados_vendedores_para_db = [
    # Adicionei a coluna "tipo_vendedor" em todos
    {"nome": "Alan Souza", "contato": "73 8150-7011", "cidades_atendidas": ["macarani", "maiquinique", "potiragua", "itarantim"], "entregas": {"quinta-feira": "macarani"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Andre", "contato": "73 99804-7736", "cidades_atendidas": ["ilhéus sul"], "entregas": {"terça-feira": "ilhéus sul"}, "observacao": "ATACADO PADIM", "tipo_vendedor": "externo"},
    {"nome": "Antonio Carlos", "contato": "73 98222-5386", "cidades_atendidas": ["cruz das almas", "governador mangabeira"], "entregas": {"segunda-feira": "cruz das almas"}, "observacao": "PADIM", "tipo_vendedor": "externo"},
    {"nome": "Aronico", "contato": "73 98118-6890", "cidades_atendidas": ["poções", "manuel vitorino", "jequié"], "entregas": {"segunda-feira": "poções", "quinta-feira": "jequié/manoel vitorino"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Ataanderson", "contato": "73 99807-4488 / 98803-9697", "cidades_atendidas": ["una", "canavieiras"], "entregas": {"quarta-feira": "canavieiras", "quinta-feira": "una"}, "observacao": "PADIM", "tipo_vendedor": "externo"},
    {"nome": "Bruno Ribeiro", "contato": "75 98253-6220", "cidades_atendidas": ["santo antônio de jesus", "muniz ferreira", "nazaré", "camassandi", "jaguaribem", "vera cruz", "barra grande", "itapariqua"], "entregas": {"quarta-feira": "nazaré (st antonio/ilha)"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Café", "contato": "73 99904-4242", "cidades_atendidas": ["porto seguro", "santa cruz cabrália", "trancoso", "arraial", "belmonte"], "entregas": {"sexta-feira": "arraial/trancoso, belmonte/stª cruz cabrália", "terça-feira": "porto seguro"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Eliézio", "contato": "73 99832-9196", "cidades_atendidas": ["camacan", "jussarí", "santa luzia", "santa maria eterna", "mascote"], "entregas": {"segunda-feira": "camacan", "terça-feira": "mascote"}, "observacao": "PADIM", "tipo_vendedor": "externo"},
    {"nome": "Everaldo Nascimento", "contato": "73 98811-4931", "cidades_atendidas": ["barra grande", "maraú"], "entregas": {"segunda-feira": "maraú, barra grande"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Genivaldo", "contato": "73 98242-2771", "cidades_atendidas": ["ilhéus-norte", "salobrinho"], "entregas": {"terça-feira": "ilhéus norte", "segunda-feira": "salobrinho"}, "observacao": "ATACADO PADIM", "tipo_vendedor": "externo"},
    {"nome": "Geovaldo", "contato": "73 99924-0428 / 98838-3825", "cidades_atendidas": ["ibicuí", "iguaí", "nova canaã"], "entregas": {"sexta-feira": "ibicuí"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Getulio da Silva", "contato": "73 9107-0118", "cidades_atendidas": ["itaquara", "cravolândia", "santa inês", "planaltino", "maracá", "lajedo", "itiruçu", "entrocamento irajuba", "jaguaquara"], "entregas": {"quarta-feira": "jaguaquara (vale/planaltino)"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Ginaldo", "contato": "73 99944-7565", "cidades_atendidas": ["itamaraju", "prado", "montinho", "alcobaça", "caravelas", "medeiros neto", "tanhém", "itabatan", "posto da mata", "mucuri", "nova viçosa"], "entregas": {"segunda-feira": "itamaraju, teixeira de freitas, prado"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Joaci", "contato": "73 99827-4288", "cidades_atendidas": ["itabuna"], "entregas": {"semana": "Itabuna"}, "observacao": "PADIM", "tipo_vendedor": "externo"},
    {"nome": "Jucilene", "contato": "73 99860-2204", "cidades_atendidas": ["itapé", "buerarema", "itajuípe", "uruçuca"], "entregas": {"terça-feira": "uruçuca", "quarta-feira": "buerarema", "quinta-feira": "itajuípe", "sexta-feira": "itapé"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Jussie", "contato": "73 99914-0572 / 98821-2285", "cidades_atendidas": ["itororó", "bandeira do colonio", "itapetinga", "ibicaraí", "floresta azul-firmino alves"], "entregas": {"segunda-feira": "ibicaraí, floresta azul", "sexta-feira": "itapetinga/itororó"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Kevin", "contato": "73 9130-0719", "cidades_atendidas": ["ipiaú", "ibirataia", "ubatã", "barra do rocha", "jequié"], "entregas": {"segunda-feira": "ubatã", "quinta-feira": "ipiaú"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Lilian", "contato": "73 98122-3041 / 98816-0729", "cidades_atendidas": ["itabuna"], "entregas": {"semana": "Itabuna"}, "observacao": "PADIM", "tipo_vendedor": "externo"},
    {"nome": "Marcelo Brandão", "contato": "73 99913-9125", "cidades_atendidas": ["itacaré", "serra grande"], "entregas": {"sexta-feira": "itacaré", "terça-feira": "itacaré"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Marcos Teixeira", "contato": "73 8814-3737", "cidades_atendidas": ["itabela", "guaratinga", "eunápolis"], "entregas": {"terça-feira": "itabela/guaratinga", "segunda-feira": "eunápolis"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Matheus", "contato": None, "cidades_atendidas": ["coaraci"], "entregas": {"segunda-feira": "coaraci(alm/itp)"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Moacy", "contato": "A ser definido", "cidades_atendidas": ["itabuna", "todas"], "entregas": {}, "observacao": "Atendimento na matriz.", "tipo_vendedor": "interno"},
    {"nome": "Maria do Carmo", "contato": "A ser definido", "cidades_atendidas": ["itabuna", "todas"], "entregas": {}, "observacao": "Atendimento na matriz.", "tipo_vendedor": "interno"},
    {"nome": "Paulo Davi Coutinho", "contato": "73 99811-8211", "cidades_atendidas": ["vitória da conquista", "barra do choça"], "entregas": {"segunda-feira": "v. da conquista"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Rosálio", "contato": "73 99819-2501", "cidades_atendidas": ["ubaitaba-gongogi"], "entregas": {"sexta-feira": "gongogi", "segunda-feira": "ubaitaba/aurelino"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Ronaldo", "contato": "75 8363-6207", "cidades_atendidas": ["itatim", "santa terezinha", "ubaíra", "jiquiriçá", "mutuípe", "amargosa"], "entregas": {"quarta-feira": "amargosa"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Valdir", "contato": "75 99911-6753", "cidades_atendidas": ["valença", "cairú", "itaberá", "taperoa", "nilo peçanha", "camamu", "igrapiúna", "ibirapitanga"], "entregas": {"sexta-feira": "ibirapitanga", "terça-feira": "valença, camamu", "quarta-feira": "ituberá"}, "observacao": None, "tipo_vendedor": "externo"},
    {"nome": "Valdino", "contato": "75 98163-1218", "cidades_atendidas": ["gandu", "presidente tancredo neves", "wenceslau guimarães"], "entregas": {"quarta-feira": "gandu", "quinta-feira": "p. tancredo"}, "observacao": None, "tipo_vendedor": "externo"},
]

def criar_e_popular_banco():
    conexao = sqlite3.connect('vendedores.db')
    cursor = conexao.cursor()
    cursor.execute('DROP TABLE IF EXISTS vendedores')
    cursor.execute('''
        CREATE TABLE vendedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            contato TEXT,
            cidades_atendidas TEXT NOT NULL,
            entregas TEXT,
            observacao TEXT,
            tipo_vendedor TEXT NOT NULL
        )
    ''')
    for vendedor in dados_vendedores_para_db:
        cursor.execute('''
            INSERT INTO vendedores (nome, contato, cidades_atendidas, entregas, observacao, tipo_vendedor)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            vendedor['nome'],
            vendedor['contato'],
            json.dumps(vendedor['cidades_atendidas']),
            json.dumps(vendedor['entregas']),
            vendedor['observacao'],
            vendedor['tipo_vendedor']
        ))

    cursor.execute('DROP TABLE IF EXISTS conversas')
    cursor.execute('''
        CREATE TABLE conversas (
            numero_usuario TEXT PRIMARY KEY,
            estado TEXT NOT NULL,
            dados_json TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conexao.commit()
    conexao.close()
    print("Banco de dados com as tabelas 'vendedores' e 'conversas' criado com sucesso!")

if __name__ == '__main__':
    criar_e_popular_banco()