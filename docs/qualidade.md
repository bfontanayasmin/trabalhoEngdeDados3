# Qualidade dos dados

Na camada Silver, os dados passam por tratamento e validação antes de serem gravados.

| Regra | Aplicação |
|---|---|
| Padronização de textos | Remoção de espaços no início e no fim |
| Padronização de e-mails | Conversão para letras minúsculas |
| Conversão de tipos | Identificadores e quantidades como inteiros, preços como decimais e datas como `DATE` |
| Campos obrigatórios | Verificação de valores nulos ou textos vazios |
| Identificadores | Verificação de valores positivos e ausência de duplicidade nas chaves |
| Valores numéricos | Preços e estoque não negativos; quantidade dos itens maior que zero |
| Relacionamentos | Verificação de referências entre produtos, categorias, clientes, pedidos e itens |
| Quantidade de registros | Comparação das contagens da Silver com a Bronze |

Se uma validação falhar, o notebook é interrompido antes da etapa de gravação, e as tarefas seguintes do Job não são executadas.

Os registros inválidos não são descartados automaticamente. No conjunto utilizado, todas as validações passaram, preservando os **32 registros**.
