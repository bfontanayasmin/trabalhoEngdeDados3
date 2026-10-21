-- Execute no SQL Editor do projeto Neon exclusivo deste trabalho.
-- Reexecuções preservam registros já existentes com o mesmo identificador.
BEGIN;
CREATE TABLE IF NOT EXISTS categorias (
 id_categoria INTEGER PRIMARY KEY,
 nome_categoria VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS produtos (
 id_produto INTEGER PRIMARY KEY,
 nome_produto VARCHAR(100) NOT NULL,
 preco NUMERIC(10,2) NOT NULL,
 estoque INTEGER NOT NULL,
 id_categoria INTEGER NOT NULL REFERENCES categorias(id_categoria)
);
CREATE TABLE IF NOT EXISTS clientes (
 id_cliente INTEGER PRIMARY KEY,
 nome_cliente VARCHAR(100) NOT NULL,
 email VARCHAR(150) NOT NULL
);
CREATE TABLE IF NOT EXISTS pedidos (
 id_pedido INTEGER PRIMARY KEY,
 id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
 data_pedido DATE NOT NULL,
 status_pedido VARCHAR(30) NOT NULL
);
CREATE TABLE IF NOT EXISTS itens_pedido (
 id_item INTEGER PRIMARY KEY,
 id_pedido INTEGER NOT NULL REFERENCES pedidos(id_pedido),
 id_produto INTEGER NOT NULL REFERENCES produtos(id_produto),
 quantidade INTEGER NOT NULL,
 preco_unitario NUMERIC(10,2) NOT NULL
);
INSERT INTO categorias VALUES
 (1,'Informática'),(2,'Papelaria')
ON CONFLICT DO NOTHING;
INSERT INTO produtos VALUES
 (1,'Mouse',49.90,20,1),(2,'Teclado',120.00,10,1),
 (3,'Caderno',19.90,30,2),(4,'Caneta',3.50,100,2),
 (5,'Headset',199.90,12,1),(6,'Webcam',149.90,8,1),
 (7,'Pendrive',39.90,25,1),(8,'Lapiseira',9.90,40,2),
 (9,'Borracha',2.50,60,2),(10,'Marcador',6.90,35,2)
ON CONFLICT DO NOTHING;
INSERT INTO clientes VALUES
 (1,'Ana Souza','ana@example.com'),(2,'Bruno Lima','bruno@example.com'),
 (3,'Carla Santos','carla@example.com'),(4,'Diego Alves','diego@example.com'),
 (5,'Elisa Costa','elisa@example.com')
ON CONFLICT DO NOTHING;
INSERT INTO pedidos VALUES
 (1,1,'2026-10-01','Concluído'),(2,2,'2026-10-02','Concluído'),
 (3,3,'2026-10-03','Em preparação'),(4,4,'2026-10-04','Concluído'),
 (5,5,'2026-10-05','Em preparação')
ON CONFLICT DO NOTHING;
INSERT INTO itens_pedido VALUES
 (1,1,1,1,49.90),(2,1,2,1,120.00),(3,2,3,2,19.90),
 (4,2,8,1,9.90),(5,3,5,1,199.90),(6,3,6,1,149.90),
 (7,4,7,2,39.90),(8,4,9,3,2.50),(9,5,10,2,6.90),(10,5,3,1,19.90)
ON CONFLICT DO NOTHING;
COMMIT;
SELECT 'categorias' AS tabela, COUNT(*) AS registros FROM categorias
UNION ALL SELECT 'clientes', COUNT(*) FROM clientes
UNION ALL SELECT 'produtos', COUNT(*) FROM produtos
UNION ALL SELECT 'pedidos', COUNT(*) FROM pedidos
UNION ALL SELECT 'itens_pedido', COUNT(*) FROM itens_pedido
ORDER BY tabela;
