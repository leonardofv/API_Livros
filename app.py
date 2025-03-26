from flask import Flask, request, jsonify, render_template
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Função que irá iniciar o banco de dados
def init_db():
    # Nessa linha estamos abrindo a conexão com o banco de dados sqlite3, se o arquivo do banco de dados não existir ele será criado automaticamente, isso acontece graças ao comando IF NOT EXISTS, o uso do with garante que a conexão seja fechada automaticamente depois que as operações forem concluídas (boa prática para evitar vazamento de memória)
    with sqlite3.connect('database.db') as conn:
        # Traduzindo a linha acima: "Na conexão do sqlite3 conecte o arquivo database.db como conn(connection), o conn será necessário para podermos manipular o banco de dados SQL (inserir, atualizar ou buscar dados)"

        cursor = conn.cursor() # O cursor é um objeto que permite interagir com o banco de dados, ele é responsável por executar comandos SQL e recuperar os resultados.



        # Agora o conn que está conectado com o arquivo database.db poderá interagir com o banco de dados, nesse comando abaixo estamos criando nossa tabela, precisamos colocar em """ aspas, isso em python é chamado de string multilinha, dessa forma fica melhor de se visualizar do que colocar todas as colunas em uma única linha.
        cursor.execute("""CREATE TABLE IF NOT EXISTS livros(
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     titulo TEXT NOT NULL,
                     categoria TEXT NOT NULL,
                     autor TEXT NOT NULL,
                     imagem_url TEXT NOT NULL
                     )""")
        # Os tipos de dados INTEGER é equivalente ao INT do MySQl e pode armazenar até 9 quintilhões de números
        # O tipo de dado TEXT é equivalente ao varchar, porém a quantidade de texto que pode armazenar depende da memória ram disponível, se tivermos 2GB de ram disponível poderemos armazenar 2.147.483.647 (Dois bilhões, cento e quarenta e sete milhões, quatrocentos e oitenta e três mil, seiscentos e quarenta e sete caracteres)

        # Se quisermos confirmar que o banco foi criado com sucesso podemos utilizar esse print
        print("Banco de dados inicializado com sucesso! ✅")


init_db()


@app.route('/')
def homepage():
    return render_template('index.html')


# Define uma rota '/doar' que aceita requisições do tipo POST
@app.route('/doar', methods=['POST'])
def doar():
    # Obtém os dados enviados na requisição em formato JSON
    dados = request.get_json()

    # Extrai os valores dos campos do JSON recebido
    titulo = dados.get('titulo')
    categoria = dados.get('categoria')
    autor = dados.get('autor')
    imagem_url = dados.get('imagem_url')

    # Verifica se algum dos campos obrigatórios está ausente
    if not all([titulo, categoria, autor, imagem_url]):
        # Retorna erro 400 (Bad Request)
        return jsonify({"erro": "Todos os campos são obrigatórios"}), 400

    
    # Conecta ao banco de dados SQLite
    with sqlite3.connect('database.db') as conn:

        cursor = conn.cursor()

        # Executa um comando SQL para inserir os dados na tabela 'livros'
        cursor.execute(""" INSERT INTO livros (titulo, categoria, autor, imagem_url)
                     VALUES(?,?,?,?)
                     """,(titulo, categoria, autor, imagem_url))
        # Confirma a transação para salvar as alterações no banco de dados
        conn.commit()

        # Retorna uma mensagem de sucesso com o código 201 (Created)
        return jsonify({"mensagem": "Livro cadastrado com sucesso"}), 201



# retornar todos os livros cadastrados no banco
@app.route('/livros', methods=['GET'])
def listar():
    with sqlite3.connect('database.db') as conn:

        livros = conn.execute("SELECT * FROM livros").fetchall()

        livros_formatados = []

        for livro in livros:
            dicionario_livros = {
                "id": livro[0],
                "titulo": livro[1],
                "categoria": livro[2],
                "autor": livro[3],
                "imagem_url": livro[4]
            }
            livros_formatados.append(dicionario_livros)

        return jsonify(livros_formatados)



# rota para deletar
@app.route('/deletar/<int:id>', methods=['DELETE'])
def deletar_livro(id):

    with sqlite3.connect('database.db') as conn:

        cursor = conn.cursor()

        cursor.execute("DELETE FROM livros WHERE id = ?", (id,))

        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"erro": "Livro não encontrado"}), 404
        
        return jsonify({"messagem": "Livro deletado com sucesso"})




if __name__ == "__main__":
    app.run(debug=True)