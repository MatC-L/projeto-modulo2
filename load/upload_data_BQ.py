import pandas as pd
from google.cloud import bigquery

# =========================================================
# CONFIGURACAO
# =========================================================
PROJECT_ID = "root-isotope-490823-b1"
DATASET_ID = "clamed_iqvia_dataset"

FILE_FILIAL = (
    r"c:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\mini-projeto\samples\filial-brick_sample.xlsx"
)
FILE_MS = (
    r"c:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\mini-projeto\samples\MS_12_2022_sample.xlsx"
)

TABLE_STG_FILIAL = f"{PROJECT_ID}.{DATASET_ID}.stg_filial_brick_raw"
TABLE_STG_MS = f"{PROJECT_ID}.{DATASET_ID}.stg_ms_raw"

client = bigquery.Client(project=PROJECT_ID)

# =========================================================
# 1) LEITURA DOS ARQUIVOS
# =========================================================
df_filial_raw = pd.read_excel(FILE_FILIAL)
df_ms_raw = pd.read_excel(FILE_MS)

# =========================================================
# 2) NORMALIZACAO PARA STAGING RAW
# =========================================================
df_filial_raw.columns = (
    df_filial_raw.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
    .str.replace(".", "", regex=False)
    .str.replace("-", "_", regex=False)
    .str.replace("/", "_", regex=False)
)
df_ms_raw.columns = (
    df_ms_raw.columns.astype(str)
    .str.strip()
    .str.lower()
    .str.replace(" ", "_", regex=False)
    .str.replace(".", "", regex=False)
    .str.replace("-", "_", regex=False)
    .str.replace("/", "_", regex=False)
)

# Ajusta nome da coluna de filial para cod_filial
if "c�d_filial" in df_filial_raw.columns:
    df_filial_raw = df_filial_raw.rename(columns={"c�d_filial": "cod_filial"})
elif "cód_filial" in df_filial_raw.columns:
    df_filial_raw = df_filial_raw.rename(columns={"cód_filial": "cod_filial"})
elif "cod_filial" not in df_filial_raw.columns:
    second_col = df_filial_raw.columns[1]
    df_filial_raw = df_filial_raw.rename(columns={second_col: "cod_filial"})

# Ajusta nomes do MS para staging esperado pelo transform.sql
df_ms_raw = df_ms_raw.rename(
    columns={
        "tipo_informacao_si_bandeira_concorrente_unidade": "vol_concorrente_indep",
        "tipo_informacao_so_bandeira_concorrente_unidade": "vol_concorrente_rede",
        "tipo_informacao_so_bandeira_preco_popular_unidade": "vol_clamed_pp",
    }
)

# Mantem somente colunas necessarias para a transformacao no BigQuery
df_stg_filial = df_filial_raw[["brick", "cod_filial"]].copy()
df_stg_ms = df_ms_raw[
    [
        "brick",
        "ean",
        "cod_prod_catarinense",
        "vol_concorrente_indep",
        "vol_concorrente_rede",
        "vol_clamed_pp",
    ]
].copy()

# =========================================================
# 3) UPLOAD STAGING RAW PARA BIGQUERY
# =========================================================
job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

client.load_table_from_dataframe(df_stg_filial, TABLE_STG_FILIAL, job_config=job_config).result()
print(f"OK -> {TABLE_STG_FILIAL}: {len(df_stg_filial)} linhas")

client.load_table_from_dataframe(df_stg_ms, TABLE_STG_MS, job_config=job_config).result()
print(f"OK -> {TABLE_STG_MS}: {len(df_stg_ms)} linhas")

print("Carga RAW finalizada com sucesso.")