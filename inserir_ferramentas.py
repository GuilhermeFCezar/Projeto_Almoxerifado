import sqlite3

conexao = sqlite3.connect('almoxerifado.db')
cursor = conexao.cursor()

print("Criando as tabelas...")

# 1. Cria a tabela de ferramentas primeiro
cursor.execute('''
CREATE TABLE IF NOT EXISTS ferramentas (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    quantidade_em_estoque INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ferramenta_id TEXT NOT NULL,
    quem_pegou TEXT NOT NULL,
    quem_autorizou TEXT NOT NULL,
    quantidade_retirada INTEGER NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ferramenta_id) REFERENCES ferramentas (id)
)
''')

lista_de_ferramentas = [
    ('FER-001', 'Furadeira de Impacto', 5),
    ('FER-002', 'Chave Phillips', 20),
    ('FER-003', 'Esmerilhadeira', 2),
    ('FER-004', 'Marreta 2kg', 8)
]

print("Inserindo ferramentas no estoque...")

# Inserindo dados
try:
    cursor.executemany('''
        INSERT INTO ferramentas (id, nome, quantidade_em_estoque)
        VALUES (?, ?, ?)
    ''', lista_de_ferramentas)
    
    print("Sucesso Total! Banco criado e ferramentas cadastradas.")

except sqlite3.IntegrityError:
    #tratamento de erro casso já esteja cadastrado
    print("Estrutura verificada! As ferramentas já estavam cadastradas no banco.")

    
conexao.commit()
conexao.close()