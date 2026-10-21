# Databricks notebook source
# MAGIC %md
# MAGIC # Extração do PostgreSQL no Neon para Landing
# MAGIC
# MAGIC Instala o driver `pg8000`, recupera a URL de conexão de `loja_neon/connection_url` nos Secrets e conecta ao Neon com TLS e validação de certificado.
# MAGIC
# MAGIC Consulta `information_schema.tables` para descobrir as tabelas do schema `public` e confere se estão presentes exatamente as cinco tabelas da loja: categorias, clientes, produtos, pedidos e itens de pedido. A senha não é escrita no notebook.
# MAGIC
# MAGIC O driver utilizado é escrito em Python. A instalação e a conexão são executadas novamente quando o Job roda este notebook em uma nova sessão.

# COMMAND ----------

# DBTITLE 1,Conectar ao Neon e validar tabelas
import subprocess
import sys
import importlib

# Instala o driver PostgreSQL escrito em Python.
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "pg8000"
])
importlib.invalidate_caches()

import ssl
from urllib.parse import urlparse, unquote

import pg8000.dbapi

# Recupera a conexão armazenada nos Secrets do Databricks.
url = dbutils.secrets.get(
    scope="loja_neon",
    key="connection_url"
)
config = urlparse(url)

# Abre a conexão com TLS e validação de certificado.
conexao = pg8000.dbapi.connect(
    host=config.hostname,
    port=config.port or 5432,
    database=unquote(config.path.lstrip("/")),
    user=unquote(config.username),
    password=unquote(config.password),
    ssl_context=ssl.create_default_context(),
    timeout=30
)

try:
    cursor = conexao.cursor()

    # Consulta todas as tabelas do schema public.
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)

    tabelas = [linha[0] for linha in cursor.fetchall()]
    cursor.close()

finally:
    conexao.close()

# Confere se as cinco tabelas da loja estão presentes.
esperadas = {
    "categorias",
    "clientes",
    "itens_pedido",
    "pedidos",
    "produtos"
}

assert set(tabelas) == esperadas, (
    f"Tabelas diferentes das esperadas: {tabelas}"
)

print("Conexão com o Neon validada.")
for tabela in tabelas:
    print(tabela)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Extração e validação dos CSVs
# MAGIC
# MAGIC Lê todas as linhas e colunas das cinco tabelas e grava um CSV por tabela, com cabeçalho e codificação UTF-8, no volume de Landing.
# MAGIC
# MAGIC Depois da gravação, lê os arquivos novamente e confere os cabeçalhos e a quantidade de registros. A carga inicial contém 32 registros no total. Ao repetir a execução, os arquivos são substituídos; o banco de origem não é alterado.
# MAGIC
# MAGIC Esta extração foi feita para um conjunto pequeno de dados e traz cada tabela para a memória do processo Python.

# COMMAND ----------

import csv
from pathlib import Path

destino = Path("/Volumes/workspace/landing/dados")

conexao = pg8000.dbapi.connect(
    host=config.hostname,
    port=config.port or 5432,
    database=unquote(config.path.lstrip("/")),
    user=unquote(config.username),
    password=unquote(config.password),
    ssl_context=ssl.create_default_context(),
    timeout=30
)

total = 0

try:
    cursor = conexao.cursor()

    for tabela in tabelas:
        # Protege o identificador usado na consulta SQL.
        nome_sql = tabela.replace('"', '""')
        cursor.execute(f'SELECT * FROM public."{nome_sql}"')

        colunas = [coluna[0] for coluna in cursor.description]
        registros = cursor.fetchall()

        arquivo = destino / f"{tabela}.csv"

        # Grava o CSV com cabeçalho e codificação UTF-8.
        with arquivo.open("w", encoding="utf-8", newline="") as f:
            escritor = csv.writer(f)
            escritor.writerow(colunas)
            escritor.writerows(registros)

        # Confere o conteúdo gravado.
        with arquivo.open(encoding="utf-8", newline="") as f:
            leitor = csv.reader(f)
            cabecalho = next(leitor)
            quantidade = sum(1 for _ in leitor)

        assert cabecalho == colunas
        assert quantidade == len(registros)

        total += quantidade
        print(f"Validado: {arquivo.name} — {quantidade} registros")

    cursor.close()

finally:
    conexao.close()

print(f"\nExtração concluída: {len(tabelas)} arquivos, {total} registros.")
print(f"Destino: {destino}")
