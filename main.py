from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# 1. Configuração Initial
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Criar a instância do FastAPI
app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# Modelo para o Aluno (os campos que vamos receber via POST)
class AlunoCreate(BaseModel):
    nome: str
    email: str
    data_nascimento: str

# 3. Função para conectar ao banco de dados
def get_db_connection():
    # RealDictCursor faz com que o resultado venha como dicionário {coluna: valor}
    # Isso é ótimo porque o FastAPI transforma dicionários em JSON automaticamente!
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

# 4. Rota GET para listar alunos
@app.get("/alunos")
def listar_alunos():
    try:
        # Abre a conexão
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Executa a consulta
        cur.execute("SELECT * FROM alunos;")
        
        # Busca todos os registros
        alunos = cur.fetchall()
        
        # Fecha cursor e conexão
        cur.close()
        conn.close()
        
        # Retorna a lista de alunos (o FastAPI converte para JSON sozinho)
        return alunos
        
    except Exception as e:
        return {"error": f"Erro ao buscar alunos: {str(e)}"}

# 5. Rota POST para criar um novo aluno
@app.post("/alunos")
def criar_aluno(aluno: AlunoCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQL para inserção
        sql = "INSERT INTO alunos (nome, email, data_nascimento) VALUES (%s, %s, %s) RETURNING *;"
        cur.execute(sql, (aluno.nome, aluno.email, aluno.data_nascimento))
        
        # Salva (commit) as alterações no banco
        novo_aluno = cur.fetchone()
        conn.commit()
        
        # Fecha cursor e conexão
        cur.close()
        conn.close()
        
        return {"message": "Aluno criado com sucesso!", "aluno": novo_aluno}

    except Exception as e:
        return {"error": f"Erro ao criar aluno: {str(e)}"}

# 6. Rota DELETE para remover um aluno pelo ID
@app.delete("/alunos/{aluno_id}")
def deletar_aluno(aluno_id: int):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQL para deleção (usando RETURNING para confirmar se foi deletado)
        sql = "DELETE FROM alunos WHERE id = %s RETURNING *;"
        cur.execute(sql, (aluno_id,))
        
        aluno_deletado = cur.fetchone()
        conn.commit()
        
        cur.close()
        conn.close()
        
        if aluno_deletado:
            return {"message": "Aluno deletado com sucesso!", "aluno": aluno_deletado}
        else:
            return {"error": f"Nenhum aluno encontrado com o ID {aluno_id}."}

    except Exception as e:
        return {"error": f"Erro ao deletar aluno: {str(e)}"}

# 7. Rota PUT para atualizar os dados de um aluno
@app.put("/alunos/{aluno_id}")
def atualizar_aluno(aluno_id: int, aluno: AlunoCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # SQL para atualização (usando RETURNING para confirmar se foi atualizado)
        sql = """
            UPDATE alunos 
            SET nome = %s, email = %s, data_nascimento = %s 
            WHERE id = %s 
            RETURNING *;
        """
        cur.execute(sql, (aluno.nome, aluno.email, aluno.data_nascimento, aluno_id))
        
        aluno_atualizado = cur.fetchone()
        conn.commit()
        
        cur.close()
        conn.close()
        
        if aluno_atualizado:
            return {"message": "Aluno atualizado com sucesso!", "aluno": aluno_atualizado}
        else:
            return {"error": f"Nenhum aluno encontrado com o ID {aluno_id}."}

    except Exception as e:
        return {"error": f"Erro ao atualizar aluno: {str(e)}"}

# 8. Rota inicial simples só para testar se a API está online
@app.get("/")
def home():
    return {"message": "API de Alunos - Online!"}

# Rota para acessar a página de CRUD
@app.get("/home", response_class=HTMLResponse)
def get_home():
    return FileResponse("index.html")

# Para rodar: uvicorn main:app --reload
