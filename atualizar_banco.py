import sqlite3

conexao = sqlite3.connect('almoxerifado.db')
cursor = conexao.cursor()

# Apaga a tabela antiga para recriar com a nova coluna
cursor.execute('DROP TABLE IF EXISTS movimentacoes')
cursor.execute('DROP TABLE IF EXISTS ferramentas')

# Cria a tabela nova com a coluna "imagem"
cursor.execute('''
CREATE TABLE ferramentas (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    quantidade_em_estoque INTEGER NOT NULL,
    imagem TEXT NOT NULL
)
''')

# Recria a tabela de movimentações
cursor.execute('''
CREATE TABLE movimentacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ferramenta_id TEXT NOT NULL,
    quem_pegou TEXT NOT NULL,
    quem_autorizou TEXT NOT NULL,
    quantidade_retirada INTEGER NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ferramenta_id) REFERENCES ferramentas (id)
)
''')

# Inserindo dados de teste com o nome do arquivo da imagem
# IMPORTANTE: Você precisará colocar essas imagens na sua pasta static/Imagens/
lista_de_ferramentas = [
    ('FER-001', 'Furadeira de Impacto', 5, 'Furadeira-Eletrica-Impacto-DWD502.png'),
    ('FER-002', 'Chave Phillips', 20, 'chave_phillips.png'),
    ('FER-003', 'Esmerilhadeira', 2, 'esmerilhadeira.png')
]

cursor.executemany('''
    INSERT INTO ferramentas (id, nome, quantidade_em_estoque, imagem)
    VALUES (?, ?, ?, ?)
''', lista_de_ferramentas)

conexao.commit()
conexao.close()
print("Banco atualizado com a coluna de imagens!")