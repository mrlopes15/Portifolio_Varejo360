import os
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOTAL_LINHAS = 200
TAMANHO_LOTE = 50
ARQUIVO_SAIDA = "dados_varejo.csv"

def gerar_lote_csv():
    prompt = """
    Gere 50 linhas de um CSV fictício com reclamações e comentários de clientes de varejo.

    Formato:
    - Use ponto e vírgula (;) como separador.
    - NÃO inclua cabeçalho.
    - NÃO use blocos de código ou crases.
    - Não utilize ponto e vírgula dentro dos textos.
    - Todos os campos devem estar na mesma linha.

    Colunas:
    1) data: datas variadas dos últimos 5 meses, no formato YYYY-MM-DD
    2) id_loja: 'Filial Centro', 'Filial Norte' ou 'Filial Sul'
    3) produto: produtos comuns de farmácia e higiene pessoal, como medicamentos, cosméticos, vitaminas, sabonetes, xampus, hidratantes, fraldas, protetor solar, antigripais, etc.
    4) estoque_sistema: número inteiro entre 0 e 100
    5) comentario_cliente: texto curto em português, simulando falas reais de consumidores

    Distribuição das linhas:
    - 40%:  ruptura virtual (estoque > 0, cliente não encontrou o produto)
    - 30%: reclamações de preço ou atendimento
    - 30%: elogios ou comentários neutros
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )

    conteudo = response.choices[0].message.content.strip()
    conteudo = conteudo.replace("```csv", "").replace("```", "").strip()
    return conteudo

def main():
    lotes = int(TOTAL_LINHAS / TAMANHO_LOTE)
    print(f"Gerando {TOTAL_LINHAS} linhas em {lotes} lotes...")
    print(f"Arquivo de saída: {ARQUIVO_SAIDA}")

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write("data;loja_id;produto;estoque_sistema;comentario_cliente\n")

    for i in range(lotes):
        print(f"Lote {i + 1} de {lotes}...")
        try:
            dados_lote = gerar_lote_csv()
            with open(ARQUIVO_SAIDA, "a", encoding="utf-8") as f:
                f.write(dados_lote + "\n")
        except Exception as e:
            print(f"Erro ao gerar o lote {i + 1}: {e}")

        time.sleep(1)

    print("Ajustando datas para o período jul-nov/2025...")
    df = pd.read_csv(ARQUIVO_SAIDA, sep=";")

    datas_2025 = pd.date_range(start="2025-07-01", end="2025-11-30", periods=len(df))
    df ["data"] = datas_2025.strftime("%Y-%m-%d")

    df.to_csv(ARQUIVO_SAIDA, sep=";", index=False, encoding="utf-8-sig")

    print(f"Arquivo final contém {len(df)} linhas e {len(df.columns)} colunas.")
    print("Datas atualizadas para 2025 e geração concluída com sucesso.")
    print(f"Arquivo salvo em: {os.path.abspath(ARQUIVO_SAIDA)}")

if __name__ == "__main__":
    main()