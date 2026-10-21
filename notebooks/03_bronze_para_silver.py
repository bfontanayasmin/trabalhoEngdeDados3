# Databricks notebook source
# MAGIC %md
# MAGIC # Tratamento e Data Quality na Silver
# MAGIC
# MAGIC Lê as cinco tabelas Bronze e aplica as regras abaixo antes de gravar a Silver:
# MAGIC
# MAGIC - Remove espaços no início e no fim dos textos e padroniza e-mails em minúsculas.
# MAGIC - Converte identificadores e quantidades para inteiro, preços para decimal e a data do pedido para data.
# MAGIC - Rejeita campos obrigatórios vazios, valores nulos e conversões inválidas.
# MAGIC - Confere identificadores positivos e ausência de duplicidade nas chaves de cada tabela.
# MAGIC - Confere preços e estoque não negativos e quantidade de item maior que zero.
# MAGIC - Confere as referências de produtos para categorias, pedidos para clientes e itens para pedidos e produtos.
# MAGIC
# MAGIC Uma falha interrompe o notebook antes da etapa de gravação. O código não descarta silenciosamente registros inválidos e não cria restrições de chave estrangeira nas tabelas Delta.
# MAGIC
# MAGIC Se as validações passarem, grava as cinco tabelas em `workspace.silver`, acrescentando horário de processamento e tabela de origem, e reconcilia as contagens com a Bronze. A carga inicial contém 32 registros.

# COMMAND ----------

from functools import reduce
from pyspark.sql import functions as F

# Colunas e tipos esperados para cada tabela.
esquemas = {
    "categorias": {
        "id_categoria": "INT",
        "nome_categoria": "STRING"
    },
    "clientes": {
        "id_cliente": "INT",
        "nome_cliente": "STRING",
        "email": "STRING"
    },
    "produtos": {
        "id_produto": "INT",
        "nome_produto": "STRING",
        "preco": "DECIMAL(10,2)",
        "estoque": "INT",
        "id_categoria": "INT"
    },
    "pedidos": {
        "id_pedido": "INT",
        "id_cliente": "INT",
        "data_pedido": "DATE",
        "status_pedido": "STRING"
    },
    "itens_pedido": {
        "id_item": "INT",
        "id_pedido": "INT",
        "id_produto": "INT",
        "quantidade": "INT",
        "preco_unitario": "DECIMAL(10,2)"
    }
}

chaves = {
    "categorias": "id_categoria",
    "clientes": "id_cliente",
    "produtos": "id_produto",
    "pedidos": "id_pedido",
    "itens_pedido": "id_item"
}

tratadas = {}
contagens = {}

# 1. Tratamento dos textos e conversão dos tipos.
for tabela, colunas in esquemas.items():
    origem = spark.table(f"workspace.bronze.{tabela}")

    expressoes = []
    for coluna, tipo in colunas.items():
        if tipo == "STRING":
            expressao = F.trim(F.col(coluna))
        else:
            expressao = F.expr(
                f"try_cast(trim(`{coluna}`) AS {tipo})"
            )
        expressoes.append(expressao.alias(coluna))

    df = origem.select(*expressoes)

    if tabela == "clientes":
        df = df.withColumn("email", F.lower(F.col("email")))

    # Todos os campos deste cenário são obrigatórios.
    problemas = []
    for coluna, tipo in colunas.items():
        problema = F.col(coluna).isNull()
        if tipo == "STRING":
            problema = problema | (F.col(coluna) == "")
        problemas.append(problema)

    assert df.filter(reduce(lambda a, b: a | b, problemas)).limit(1).count() == 0, (
        f"{tabela}: campo obrigatório vazio ou conversão inválida."
    )

    # Identificadores devem ser positivos.
    for coluna in colunas:
        if coluna.startswith("id_"):
            assert df.filter(F.col(coluna) <= 0).limit(1).count() == 0, (
                f"{tabela}: identificador inválido em {coluna}."
            )

    # Cada chave primária deve identificar apenas uma linha.
    duplicados = (
        df.groupBy(chaves[tabela])
        .count()
        .filter(F.col("count") > 1)
    )
    assert duplicados.limit(1).count() == 0, (
        f"{tabela}: identificador duplicado."
    )

    tratadas[tabela] = df
    contagens[tabela] = origem.count()
    print(f"Campos, tipos e identificadores validados: {tabela}")

# 2. Validação dos valores numéricos.
assert tratadas["produtos"].filter(
    (F.col("preco") < 0) | (F.col("estoque") < 0)
).limit(1).count() == 0, "Produto com preço ou estoque negativo."

assert tratadas["itens_pedido"].filter(
    (F.col("quantidade") <= 0) | (F.col("preco_unitario") < 0)
).limit(1).count() == 0, "Item com quantidade ou preço inválido."

# 3. Validação dos relacionamentos entre as tabelas.
relacionamentos = [
    ("produtos", "id_categoria", "categorias", "id_categoria"),
    ("pedidos", "id_cliente", "clientes", "id_cliente"),
    ("itens_pedido", "id_pedido", "pedidos", "id_pedido"),
    ("itens_pedido", "id_produto", "produtos", "id_produto")
]

for filha, coluna_filha, pai, coluna_pai in relacionamentos:
    referencias = tratadas[pai].select(
        F.col(coluna_pai).alias(coluna_filha)
    )

    sem_correspondencia = tratadas[filha].join(
        referencias,
        on=coluna_filha,
        how="left_anti"
    )

    assert sem_correspondencia.limit(1).count() == 0, (
        f"Relacionamento inválido: {filha} → {pai}."
    )

print("Valores e relacionamentos validados.")

# 4. Gravação das cinco tabelas Delta na Silver.
total = 0

for tabela, df in tratadas.items():
    destino = f"workspace.silver.{tabela}"

    df = (
        df.withColumn("data_hora_silver", F.current_timestamp())
        .withColumn(
            "tabela_origem",
            F.lit(f"workspace.bronze.{tabela}")
        )
    )

    (
        df.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(destino)
    )

    quantidade = spark.table(destino).count()
    assert quantidade == contagens[tabela], (
        f"{tabela}: quantidade diferente da Bronze."
    )

    total += quantidade
    print(f"Validado: {tabela} — {quantidade} registros — Silver")

print(f"\nSilver concluída: {len(tratadas)} tabelas, {total} registros.")
