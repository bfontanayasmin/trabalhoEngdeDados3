# Databricks notebook source
# MAGIC %md
# MAGIC # Conversão de Landing para Bronze
# MAGIC
# MAGIC Lê os cinco CSVs do volume `workspace.landing.dados`. Mantém os campos de negócio como texto nesta camada bruta e acrescenta `data_hora_bronze` e `nome_arquivo` para rastrear o processamento e a origem.
# MAGIC
# MAGIC Grava tabelas Delta gerenciadas em `workspace.bronze` com `saveAsTable`, sem definir `LOCATION`. Para cada tabela, confere o formato Delta e a quantidade de registros em relação ao CSV.
# MAGIC
# MAGIC A carga substitui o conteúdo atual de cada tabela. A execução inicial validou cinco tabelas e 32 registros.

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit

caminho_landing = "/Volumes/workspace/landing/dados"

tabelas = [
    "categorias",
    "clientes",
    "itens_pedido",
    "pedidos",
    "produtos"
]

total = 0

for tabela in tabelas:
    arquivo = f"{tabela}.csv"

    # Preserva os valores do CSV como texto na camada bruta.
    df = (
        spark.read
        .option("header", "true")
        .option("encoding", "UTF-8")
        .option("inferSchema", "false")
        .csv(f"{caminho_landing}/{arquivo}")
        .withColumn("data_hora_bronze", current_timestamp())
        .withColumn("nome_arquivo", lit(arquivo))
    )

    quantidade_origem = df.count()
    destino = f"workspace.bronze.{tabela}"

    # Grava uma tabela Delta gerenciada.
    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(destino)
    )

    quantidade_destino = spark.table(destino).count()
    formato = (
        spark.sql(f"DESCRIBE DETAIL {destino}")
        .select("format")
        .first()[0]
    )

    assert quantidade_destino == quantidade_origem
    assert formato == "delta"

    total += quantidade_destino
    print(
        f"Validado: {tabela} — "
        f"{quantidade_destino} registros — formato Delta"
    )

print(f"\nBronze concluída: {len(tabelas)} tabelas, {total} registros.")
