import psycopg2
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# URL que você forneceu diretamente ou que está no .env
DATABASE_URL = os.getenv("DATABASE_URL")

def test_connection():
    try:
        # 1. Tentar conectar
        print("Tentando conectar ao banco de dados...")
        conn = psycopg2.connect(DATABASE_URL)
        
        # 2. Criar um cursor (para executar comandos)
        cur = conn.cursor()
        
        # 3. Executar uma consulta simples (ex: Versão do PostgreSQL)
        cur.execute("SELECT version();")
        
        # 4. Obter o resultado
        db_version = cur.fetchone()
        
        print("\n✅ Conexão bem-sucedida!")
        print(f"🖥️ Versão do Banco de Dados: {db_version[0]}")
        
        # Fechar o que abrirmos
        cur.close()
        conn.close()
        
    except Exception as error:
        print(f"\n❌ Erro ao conectar: {error}")

if __name__ == "__main__":
    test_connection()
