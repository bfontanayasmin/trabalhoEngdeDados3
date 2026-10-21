# Pipeline de dados

O pipeline utiliza o catálogo `workspace`, organizado nos schemas `landing`, `bronze`, `silver` e `gold`.

## Landing — extração

O notebook acessa o PostgreSQL no Neon e extrai todas as cinco tabelas da loja. Cada tabela gera um arquivo CSV com cabeçalho e codificação UTF-8, armazenado no volume `workspace.landing.dados`.

Após a gravação, o código confere os cabeçalhos e as quantidades de registros. A conexão é recuperada dos Secrets do Databricks.

## Bronze — armazenamento em Delta

Os CSVs são lidos e gravados como tabelas Delta. Os campos de negócio permanecem como texto, acompanhados do nome do arquivo de origem e do horário de processamento.

## Silver — tratamento e validação

Os textos são padronizados, os tipos são convertidos e os dados passam por validações antes da gravação das tabelas tratadas.

## Gold — modelo dimensional

Os dados da Silver alimentam as dimensões produto, cliente e tempo e a fato de itens de pedido, preparando os dados para consultas analíticas.

## Reexecução

A extração substitui os CSVs. Bronze e Silver sobrescrevem suas tabelas. Na Gold, produto e cliente são atualizados por `MERGE`, enquanto o calendário e a fato são reconstruídos. Assim, repetir a carga com a mesma origem não acumula os mesmos itens na fato.
