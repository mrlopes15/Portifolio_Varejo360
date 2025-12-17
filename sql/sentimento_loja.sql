--Aparece a quantidade de ocorrências negativas, separado por loja e por categoria.
SELECT 
    loja_id,
    categoria_ia,
    count(*) as qtd
FROM tb_analise_varejo360
WHERE sentimento_ia = 'Negativo'
GROUP BY loja_id, categoria_ia
ORDER BY qtd DESC;