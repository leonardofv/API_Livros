from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Função que irá iniciar o banco de dados
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        # Tabela de livros disponíveis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                autor TEXT NOT NULL,
                imagem_url TEXT NOT NULL,
                doador TEXT NOT NULL
            )
        """)

        # Tabela de livros doados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros_doados(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                autor TEXT NOT NULL,
                imagem_url TEXT NOT NULL,
                doador TEXT NOT NULL,
                cliente_nome TEXT NOT NULL,
                cliente_email TEXT NOT NULL
            )
        """)

        # Tabela doadores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doadores(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                livro_doado INTEGER NOT NULL,
                FOREIGN KEY (livro_doado) REFERENCES livros(id)
            )
        """)

        # Tabela clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                livro_escolhido INTEGER NOT NULL,
                FOREIGN KEY (livro_escolhido) REFERENCES livros(id)
            )
        """)

        print("Banco de dados inicializado com sucesso! ✅")

init_db()

@app.route('/')
def homepage():
    return render_template('index.html')

# Rota para cadastrar um livro
@app.route('/doar', methods=['POST'])
def doar():
    dados = request.get_json()
    titulo = dados.get('titulo')
    categoria = dados.get('categoria')
    autor = dados.get('autor')
    imagem_url = dados.get('imagem_url')
    doador = dados.get('doador')

    if not all([titulo, categoria, autor, imagem_url, doador]):
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, categoria, autor, imagem_url, doador)
            VALUES (?, ?, ?, ?, ?)
        """, (titulo, categoria, autor, imagem_url, doador))
        livro_id = cursor.lastrowid #id do livro inserido

        # Inserir o doador na tabela 'doadores'
        cursor.execute("""
            INSERT INTO doadores (nome, livro_doado)
            VALUES (?, ?)
        """, (doador, livro_id))

        conn.commit()

        return jsonify({"mensagem": "Livro cadastrado com sucesso"}), 201

# Rota para listar todos os livros
@app.route('/livros', methods=['GET'])
def listar():
    with sqlite3.connect('database.db') as conn:
        livros = conn.execute("SELECT * FROM livros").fetchall()
        livros_formatados = [
            {
                "id": livro[0],
                "titulo": livro[1],
                "categoria": livro[2],
                "autor": livro[3],
                "imagem_url": livro[4]
            }
            for livro in livros
        ]
        return jsonify(livros_formatados)

#Rota para listar livros doados
@app.route('/doados', methods=['GET'])
def listar_livros_doados():
    with sqlite3.connect('database.db') as conn:
        livros_doados = conn.execute("SELECT * FROM livros_doados").fetchall()
        livros_formatados = [
            {
            "id": livro[0],
                "titulo": livro[1],
                "categoria": livro[2],
                "autor": livro[3],
                "imagem_url": livro[4],
                "doador": livro[5],
                "cliente_nome": livro[6],
                "cliente_email": livro[7]
            }
            for livro in livros_doados
        ]
        return jsonify(livros_formatados), 200



#Rota para listar doadores
@app.route('/doadores', methods=['GET'])
def listar_doadores():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        doadores = cursor.execute("SELECT doadores.id, doadores.nome, livros.titulo FROM doadores JOIN livros ON doadores.livro_doado = livros.id" 
        "").fetchall() 
        doadores_formatados = [
            {
                "id": doador[0], 
                "nome": doador[1],
                "livro_doado": doador[2]
            }
            for doador in doadores
        ]
        return jsonify(doadores_formatados), 200


# Rota para listar todos os clientes
@app.route('/clientes', methods=['GET'])
def listar_clientes():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        # JOIN para trazer nome, email do cliente e título do livro escolhido
        clientes = cursor.execute("""
            SELECT clientes.id, clientes.nome, clientes.email, livros_doados.titulo
            FROM clientes
            LEFT JOIN livros_doados ON clientes.livro_escolhido = livros_doados.id
        """).fetchall()
        clientes_formatados = [
            {
                "id": cliente[0],
                "nome": cliente[1],
                "email": cliente[2],
                "livro_escolhido": cliente[3]
            }
            for cliente in clientes
        ]
        return jsonify(clientes_formatados), 200

# Rota para deletar um livro e registrar o cliente
@app.route('/deletar/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')

    if not all([nome, email]):
        return jsonify({"ERROR": "nome e email são obrigatórios"}), 400

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        # Busca o livro a ser doado
        cursor.execute("SELECT * FROM livros WHERE id = ?", (livro_id,))
        livro = cursor.fetchone()

        if not livro:
            return jsonify({"ERROR": "Livro não encontrado"}), 404

        # Insere o cliente
        cursor.execute("""
            INSERT INTO clientes (nome, email, livro_escolhido)
            VALUES (?, ?, ?)
        """, (nome, email, livro_id))

        # Insere o livro na tabela livros_doados, junto com os dados do cliente
        cursor.execute("""
            INSERT INTO livros_doados (titulo, categoria, autor, imagem_url, doador, cliente_nome, cliente_email)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (livro[1], livro[2], livro[3], livro[4], livro[5], nome, email))

        # Remove o livro da tabela livros
        cursor.execute("DELETE FROM livros WHERE id = ?", (livro_id,))

        conn.commit()

    return jsonify({"menssagem": "Livro doado"}), 200

if __name__ == '__main__':
    app.run(debug=True)