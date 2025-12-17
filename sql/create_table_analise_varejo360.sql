DROP TABLE IF EXISTS tb_analise_varejo360;

CREATE TABLE tb_analise_varejo360 (
    id SERIAL PRIMARY KEY,
    data_ocorrencia DATE,
    loja_id VARCHAR(50),
    produto VARCHAR(100),
    estoque_sistema INT,
    comentario TEXT,
    categoria_ia VARCHAR(50),
    sentimento_ia VARCHAR(20),
    alerta_ruptura BOOLEAN,
    custo_analise FLOAT,
    data_processamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);