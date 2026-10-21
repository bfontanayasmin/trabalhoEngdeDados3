# Databricks notebook source
# MAGIC %md
# MAGIC # Preparação do ambiente
# MAGIC
# MAGIC **Participante:** Yasmin Bez Fontana.
# MAGIC
# MAGIC Cria os schemas Landing, Bronze, Silver e Gold no catálogo `workspace`, além do volume `workspace.landing.dados`. O volume guarda os CSVs extraídos do PostgreSQL no Neon. As demais camadas armazenam tabelas Delta.
# MAGIC
# MAGIC `IF NOT EXISTS` permite repetir a preparação sem apagar os dados existentes.

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.landing
# MAGIC COMMENT 'Dados brutos extraídos do banco de dados';
# MAGIC
# MAGIC CREATE VOLUME IF NOT EXISTS workspace.landing.dados
# MAGIC COMMENT 'Arquivos CSV da loja';
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.bronze
# MAGIC COMMENT 'Dados brutos em tabelas Delta';
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.silver
# MAGIC COMMENT 'Dados tratados e validados';
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS workspace.gold
# MAGIC COMMENT 'Modelo dimensional para análise de vendas';

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferência dos schemas
# MAGIC
# MAGIC Lista os schemas do catálogo para verificar a criação das quatro camadas.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW SCHEMAS IN workspace;

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conferência do volume
# MAGIC
# MAGIC Lista os volumes de Landing. O volume `dados` é acessado pelo caminho `/Volumes/workspace/landing/dados`.

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW VOLUMES IN workspace.landing;
