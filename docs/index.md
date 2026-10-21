# Lakehouse da loja

**Trabalho 3 — Engenharia de Dados**  
**Participante:** Yasmin Bez Fontana

Este projeto implementa um pipeline no Databricks Free Edition, utilizando dados de uma loja armazenados em PostgreSQL no Neon.

Os dados percorrem as camadas **Landing, Bronze, Silver e Gold**, passando pela extração em CSV, armazenamento em Delta, tratamento e modelagem dimensional.

Um Job encadeia os cinco notebooks, executando cada etapa após o sucesso da anterior.

## Conjunto de dados

Foram utilizados dados fictícios criados para a atividade, distribuídos em cinco tabelas: categorias, clientes, produtos, pedidos e itens de pedido, totalizando **32 registros**.

## Resultados

A execução completa foi validada com sucesso. A Gold contém três dimensões e uma tabela fato com dez itens de pedido, cujo valor total é **R$ 690,40**, considerando todos os status dos pedidos.
