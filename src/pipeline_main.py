import os
import pandas as pd
from openai import OpenAI
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
db_url = os.getenv("DATABASE_URL")

print("Lendo dados de entrada...")

# Caminho do arquivo de dados, relativo ao próprio script
diretorio_script = os.path.dirname(os.path.abspath(__file__))
caminho_arquivo = os.path.join(diretorio_script, "dados_varejo.csv")

if not os.path.exists(caminho_arquivo):
    print(f"Arquivo 'dados_varejo.csv' não encontrado em: {caminho_arquivo}")
    raise FileNotFoundError("Verifique se o arquivo foi gerado e está na mesma pasta do script.")

df = pd.read_csv(
    caminho_arquivo,
    sep=";",
    engine="python"
)
print(f"Arquivo carregado com {len(df)} linhas e {len(df.columns)} colunas.")


def classificar_ocorrencia(texto, estoque):
    prompt = f"""
    Você é um analista de operações de varejo.

    Analise a reclamação abaixo e classifique:

    Texto: "{texto}"
    Estoque no sistema: {estoque}

    Responda exatamente no formato:
    CATEGORIA|SENTIMENTO|ALERTA_RUPTURA

    Categorias válidas:
    - Ruptura Virtual (estoque > 0 e o cliente não encontrou o produto)
    - Ruptura Real
    - Preço
    - Atendimento
    - Elogio

    Sentimento: Positivo, Negativo ou Neutro.

    ALERTA_RUPTURA:
    - TRUE apenas se a categoria for Ruptura Virtual
    - FALSE nos demais casos.
    """

    # Cálculo aproximado de custo da chamada (FinOps simples)
    custo_estimado = (len(prompt) / 4) * (0.15 / 1_000_000)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        saida = response.choices[0].message.content.strip()
        return f"{saida}|{custo_estimado:.8f}"
    
    except Exception as e:
        print(f"Falha na classificação por IA: {e}")
        return "Erro|Neutro|FALSE|0.0"

print("Processando ocorrências com IA, linha a linha...")

# Aplica a função de IA para cada linha
resultados = df.apply(
    lambda x: classificar_ocorrencia(
        x["comentario_cliente"],
        x["estoque_sistema"]
    ),
    axis=1
)

# Divide o retorno nas novas colunas
df[["categoria_ia", "sentimento_ia", "alerta_ruptura", "custo_analise"]] = (
    resultados.str.split("|", expand=True)
)

# Ajuste de tipos
df["alerta_ruptura"] = (
    df["alerta_ruptura"]
    .str.strip()
    .map({"TRUE": True, "FALSE": False})
    .fillna(False)
)

df["custo_analise"] = pd.to_numeric(
    df["custo_analise"], errors="coerce"
).fillna(0.0)

print("Padronizando nomes de produtos...")

# Normaliza texto: tira acentos quebrados, espaços e coloca em minúsculo
df["produto"] = (
    df["produto"]
    .astype(str)
    .str.normalize("NFKD")
    .str.encode("ascii", errors="ignore")
    .str.decode("utf-8")
    .str.strip()
    .str.lower()
)

# Mapeamento simples de variações para nomes mais profissionais
substituicoes_produto = {
    # Medicamentos
    "paracetamol": "Paracetamol 500mg EMS 20 comprimidos",
    "paracetamol 500mg": "Paracetamol 500mg EMS 20 comprimidos",
    "analgesico": "Paracetamol 500mg EMS 20 comprimidos",
    "antibiotico": "Amoxicilina EMS 500mg 21 cápsulas",
    "antigripal": "Antigripal Benegrip 20 comprimidos",
    "antigripais": "Antigripal Benegrip 20 comprimidos",
    "antialergico": "Loratadina 10mg 12 comprimidos",

    # Vitaminas e suplementos
    "vitamina": "Multivitamínico Centrum 60 comprimidos",
    "vitaminas": "Multivitamínico Centrum 60 comprimidos",
    "vitaminico": "Complexo Vitamínico Lavitan 60 comprimidos",
    "vitamina c": "Vitamina C Sundown 1000mg 60 comprimidos",
    "vitamina d": "Vitamina D 2000UI Neo Química 30 cápsulas",
    "suplemento": "Suplemento Alimentar Whey Protein 900g",

    # Higiene pessoal
    "shampoo": "Shampoo Clear Anticaspa 200ml",
    "xampu": "Shampoo Clear Anticaspa 200ml",
    "condicionador": "Condicionador Pantene Liso Extremo 200ml",
    "sabonete": "Sabonete Dove Original 90g",
    "sabonete liquido": "Sabonete Líquido Dove 250ml",
    "creme dental": "Creme Dental Colgate Total 12 90g",
    "pasta de dente": "Creme Dental Colgate Total 12 90g",
    "desodorante": "Desodorante Rexona Aerosol 150ml",

    # Pele e cuidados
    "hidratante": "Hidratante Corporal Nivea Milk 200ml",
    "creme hidratante": "Creme Hidratante Nivea Soft 100ml",
    "protetor solar": "Protetor Solar Nivea FPS 50 200ml",
    "filtro solar": "Protetor Solar Nivea FPS 50 200ml",
    "protetor labial": "Protetor Labial Nivea Med Repair",
    "pomada": "Pomada Bepantol Baby 30g",

    # Infantil
    "fralda": "Fralda Pampers Supersec G 32 unidades",
    "fraldas": "Fralda Pampers Supersec G 32 unidades",
    "lenco umedecido": "Lenço Umedecido Huggies 48 unidades",

    # Outros
    "cotonete": "Cotonete Johnson's 150 unidades",
    "agua oxigenada": "Água Oxigenada 10 Volumes 100ml",
    "soro fisiologico": "Soro Fisiológico 0,9% 500ml",
    "cha": "Chá Camomila 20 sachês",
    "locao hidratante": "Loção Hidratante Johnson's 200ml",
    "locao para o corpo": "Hidratante Corporal Neutrogena 200ml",
    "remedio para dor de cabeca": "Analgésico e Relaxante Muscular Dorflex 300mg",
    "remedio para gripe": "Antigripal Benegrip 20 comprimidos",
    "vitamina e": "Vitamina E 400UI Sundown 60 cápsulas",
    "vitamina b12": "Vitamina B12 Lavitan 60 comprimidos",
    "creme antienvelhecimento": "Creme Facial Anti-Idade L'Oréal Revitalift",
    "creme anti-idade": "Creme Facial Anti-Idade L'Oréal Revitalift",
    "creme para maos": "Creme para Mãos Nivea 100ml",
    "cosmeticos": "Kit Cuidados com a Pele Neutrogena",
    "medicamentos": "Dipirona 500mg EMS 20 comprimidos",
    }

df["produto"] = df["produto"].str.replace(r"\s+", " ", regex=True)
df["produto"] = df["produto"].replace(substituicoes_produto, regex=False)

print("Padronização de produtos concluída.")

# Ajuste de nomes para o banco
df_final = df.rename(columns={
    "data": "data_ocorrencia",
    "comentario_cliente": "comentario"
})

print("Gravando dados no banco (Neon/PostgreSQL)...")

try:
    engine = create_engine(db_url)
    df_final.to_sql("tb_analise_varejo360", engine, if_exists="replace", index=False)

    print("Pipeline concluído. Dados gravados com sucesso em 'tb_analise_varejo360'.")

except Exception as e:
    print(f"Erro ao salvar no banco: {e}")
    raise

print(f"Diretório atual do script: {diretorio_script}")

saida_csv =  r"C:\Users\Notebook\Documents\PROGRAMACAO\projeto_varejo360\src\dados_varejo_tratado.csv"
df_final.to_csv(saida_csv, index=False, sep=";", encoding="utf-8-sig")
print(f"Arquivo atualizado salvo em: {saida_csv}")