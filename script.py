import json
import os
import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()  # Carrega variáveis do .env

key = os.getenv("CHAVE_CRIPTOGRAFIA").encode()
fernet = Fernet(key)

def conectar_mysql():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "my_database")
    )

def executar_script(cursor, caminho_sql):
    with open(caminho_sql, 'r', encoding='utf-8') as f:
        cursor.execute(f.read())

def carregar_dados_json(caminho_json):
    with open(caminho_json, 'r', encoding='utf-8') as f:
        return json.load(f)

def listar_menssage_by_id(conexao):
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT id, sender, message, timestamp FROM mensagens ORDER BY timestamp DESC LIMIT 5")
    resultados = cursor.fetchall()
    print("\n📥 MENSAGENS DESCRIPTOGRAFADAS:\n")
    for msg in resultados:
        try:
            mensagem_original = fernet.decrypt(msg['message'].encode()).decode()
        except Exception as e:
            mensagem_original = "[Erro ao descriptografar]"
        print(f"[{msg['timestamp']}] {msg['sender']}: {mensagem_original}")

def main():
    try:
        conn = conectar_mysql()
        cursor = conn.cursor()

        print("Criando tabela...")
        executar_script(cursor, 'migration/mensagens.sql')

        print("Carregando mensagens JSON...")
        dados = carregar_dados_json('massica/mock_chat_messages.json')

        print("Inserindo dados...")
        with open('migration/insert_mensagens.sql', 'r', encoding='utf-8') as f:
            insert_sql = f.read()

        valores = [
            (
                item['id'],
                item['sender'],
                fernet.encrypt(item['message'].encode()).decode(),  # <-- AQUI criptografado
                datetime.fromisoformat(item['timestamp'])
            ) for item in dados
        ]
        cursor.executemany(insert_sql, valores)

        conn.commit()
        print("Tabela criada e mensagens inseridas com sucesso!")
        listar_menssage_by_id(conn)

    except mysql.connector.Error as e:
        print(f"Erro MySQL: {e}")
    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    main()
