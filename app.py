from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Função que irá iniciar o banco de dados
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        # Criação da tabela 'livros'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                autor TEXT NOT NULL,
                imagem_url TEXT NOT NULL
            )
        """)

        # Criação da tabela 'clientes'
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT NOT NULL,
                livro_escolhido TEXT NOT NULL
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

    if not all([titulo, categoria, autor, imagem_url]):
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, categoria, autor, imagem_url)
            VALUES (?, ?, ?, ?)
        """, (titulo, categoria, autor, imagem_url))
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

# Rota para deletar um livro e registrar o cliente
@app.route('/deletar/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    dados = request.get_json()
    nome = dados.get('nome')
    cpf = dados.get('cpf')

    if not all([nome, cpf]):
        return jsonify({"erro": "Nome e CPF são obrigatórios"}), 400

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()

        # Verifica se o livro existe
        cursor.execute("SELECT titulo FROM livros WHERE id = ?", (id,))
        livro = cursor.fetchone()

        if not livro:
            return jsonify({"erro": "Livro não encontrado"}), 404

        livro_titulo = livro[0]

        # Registra o cliente na tabela 'clientes'
        cursor.execute("""
            INSERT INTO clientes (nome, cpf, livro_escolhido)
            VALUES (?, ?, ?)
        """, (nome, cpf, livro_titulo))
        conn.commit()

        # Deleta o livro da tabela 'livros'
        cursor.execute("DELETE FROM livros WHERE id = ?", (id,))
        conn.commit()

        return jsonify({"mensagem": "Livro deletado com sucesso e cliente registrado!"}), 200




if __name__ == "__main__":
    app.run(debug=True)