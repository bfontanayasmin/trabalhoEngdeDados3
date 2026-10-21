# Modelo dimensional

A camada Gold organiza os dados em um modelo dimensional, seguindo a proposta de Ralph Kimball apresentada em aula.

## Dimensões

| Tabela | Conteúdo |
|---|---|
| `dim_produto` | Produto e sua categoria |
| `dim_cliente` | Identificador, nome e e-mail do cliente |
| `dim_tempo` | Data, ano, trimestre, mês, dia e dia da semana |

Produto e cliente possuem chaves substitutas geradas pelo Databricks. Seus atributos são atualizados por `MERGE`, sem manter versões históricas desses atributos.

A dimensão tempo possui uma linha por dia e cobre os anos dos pedidos. Para os dados utilizados, foram geradas **365 datas de 2026**.

## Tabela fato

A `fato_itens_pedido` possui **uma linha por item de pedido**, ligada às dimensões produto, cliente e tempo.

Armazena quantidade, preço unitário e valor total do item, calculado por **quantidade × preço unitário**. O preço utilizado é o registrado no pedido.

Também mantém o identificador do pedido e seu status, permitindo distinguir pedidos concluídos dos que estão em preparação.

## Validação

A fato contém **10 itens**, sem duplicidade de `id_item`. Sua quantidade e o total de **R$ 690,40**, considerando todos os status, foram conferidos com a Silver.
