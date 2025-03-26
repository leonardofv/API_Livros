# 📚 API de Doação de Livros

Esta é uma API simples feita com **Flask** e **SQLite** que permite cadastrar e listar livros doados.

---

## ▶️ Como rodar o projeto

1. Clone o repositório:
```bash
git clone <URL_DO_REPOSITORIO>
cd nome-do-projeto
```

2. Crie um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Inicie o servidor:
```bash
python app.py
```

> A API estará disponível em `http://localhost:5000`

---

## 🔗 Endpoints

### ➕ POST `/doar`

Cadastra um novo livro.

**Requisição (JSON):**
```json
{
  "titulo": "Dom Casmurro",
  "categoria": "Romance",
  "autor": "Machado de Assis",
  "image_url": "https://link-da-imagem.com"
}
```

**Resposta (201):**
```json
{
  "mensagem": "Livro cadastrado com sucesso!"
}
```

---

### 📚 GET `/livros`

Retorna todos os livros cadastrados.

**Resposta (200):**
```json
[
  {
    "id": 1,
    "titulo": "Dom Casmurro",
    "categoria": "Romance",
    "autor": "Machado de Assis",
    "image_url": "https://link-da-imagem.com"
  }
]
```

---
### ❌ DELETE `/livros/id`

Deletar um Livro.

**Resposta (200):**
```json
{
    "menssagem": "Livro excluido com sucesso!"
}
```

## 🧰 Tecnologias utilizadas

- Python 3
- Flask
- SQLite
- Flask-CORS

---
