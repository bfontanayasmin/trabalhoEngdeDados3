# Execução do pipeline

O Job **pipeline de dados** encadeia os cinco notebooks:

| Ordem | Tarefa | Depende de |
|---|---|---|
| 1 | Preparar ambiente | — |
| 2 | Extrair do Neon | Preparar ambiente |
| 3 | Landing para Bronze | Extrair do Neon |
| 4 | Bronze para Silver | Landing para Bronze |
| 5 | Silver para Gold | Bronze para Silver |

Todas as tarefas utilizam notebooks com compute **Serverless**. Cada tarefa começa somente após o sucesso da anterior.

Para executar, acesse **Jobs & Pipelines**, abra o Job e clique em **Run now**. A aba **Runs** mostra o andamento e o resultado das tarefas.

## Resultado registrado

Em **20/10/2026**, a execução completa terminou com sucesso em **2 minutos e 56 segundos**.

| Camada | Resultado |
|---|---|
| Landing | 5 CSVs e 32 registros |
| Bronze | 5 tabelas Delta e 32 registros |
| Silver | 5 tabelas tratadas e 32 registros |
| Gold | 3 dimensões e 1 fato com 10 itens |

A configuração do Job está disponível na pasta `jobs/` do repositório.

![Cinco tarefas concluídas com sucesso](assets/execucao_job.png)
