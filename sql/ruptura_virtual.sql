-- Produtos que possuem estoque no sistema, mas foi detectado pela IA que o cliente não os encontrou, ou seja,
-- maior número de Ruptura Virtual.

SELECT 
    produto, 
    estoque_sistema, 
    count(*) as reclamacoes_ruptura
FROM tb_analise_varejo360
WHERE alerta_ruptura = TRUE
GROUP BY produto, estoque_sistema
ORDER BY reclamacoes_ruptura DESC;

SELECT produto,
		COUNT(*)
FROM tb_analise_varejo360
GROUP BY produto
ORDER BY COUNT(*);
