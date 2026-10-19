import sqlite3
from pathlib import Path

# Localiza automaticamente a pasta principal do projeto
pasta_projeto = Path(__file__).resolve().parent.parent

# Caminho do banco SQLite
caminho_banco = pasta_projeto / "projeto_manutencao.db"

print("Banco localizado em:")
print(caminho_banco)

# Abre a conexão
conexao = sqlite3.connect(caminho_banco)
cursor = conexao.cursor()

# Testes
cursor.execute("SELECT COUNT(*) FROM equipamentos")
total_equipamentos = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM leituras")
total_leituras = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM manutencoes")
total_manutencoes = cursor.fetchone()[0]

print("\nConexão realizada com sucesso!")
print(f"Equipamentos: {total_equipamentos}")
print(f"Leituras: {total_leituras}")
print(f"Manutenções: {total_manutencoes}")

conexao.close()