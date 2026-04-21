import os
import sys
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

# Raiz do projeto no path para importar extract.visualizar_dados
PROJETO_ROOT = Path(__file__).resolve().parent.parent
if str(PROJETO_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJETO_ROOT))

from extract.visualizar_dados import (  # noqa: E402
    padronizar_colunas,
    preparar_vendas_para_grafico,
)

# =========================================================
# CONFIGURACAO
# =========================================================
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "projeto-modulo2")
# Staging (bronze): alinhado a transform/create_and_transform_dataset.sql opcao B
DATASET_ID = os.environ.get("BQ_DATASET_ID", "staging_modulo2")
BQ_LOCATION = os.environ.get("BQ_LOCATION", "US")

RAW_DIR = PROJETO_ROOT / "raw"

FILE_FILIAL = RAW_DIR / "dim_filial.csv"
FILE_PRODUTO = RAW_DIR / "dim_produto.csv"
FILE_VENDAS = RAW_DIR / "fato_vendas.csv"

TABLE_STG_FILIAL = f"{PROJECT_ID}.{DATASET_ID}.stg_dim_filial"
TABLE_STG_PRODUTO = f"{PROJECT_ID}.{DATASET_ID}.stg_dim_produto"
TABLE_STG_VENDAS = f"{PROJECT_ID}.{DATASET_ID}.stg_fato_vendas"


# Cria cliente BigQuery para o projeto configurado.
def criar_cliente_bq():
    return bigquery.Client(project=PROJECT_ID)


# Garante que o conjunto de dados existe; cria na primeira execucao.
def garantir_conjunto_dados(client, project_id, dataset_id, location):
    dataset_ref = f"{project_id}.{dataset_id}"
    try:
        client.get_dataset(dataset_ref)
        print(f"Conjunto de dados ja existe: {dataset_ref}")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = location
        client.create_dataset(dataset)
        print(f"Conjunto de dados criado: {dataset_ref} (local: {location})")


# Le os tres CSVs brutos (caminhos relativos ao projeto; padronizacao no extract).
def ler_csvs_raw():
    df_filial_raw = pd.read_csv(FILE_FILIAL)
    df_produto_raw = pd.read_csv(FILE_PRODUTO)
    df_vendas_raw = pd.read_csv(FILE_VENDAS)
    return df_filial_raw, df_produto_raw, df_vendas_raw


# Envia os tres dataframes para BigQuery com truncate.
def carregar_tabelas_bigquery(client, df_filial, df_produto, df_vendas):
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")

    client.load_table_from_dataframe(
        df_filial, TABLE_STG_FILIAL, job_config=job_config
    ).result()
    print(f"OK -> {TABLE_STG_FILIAL}: {len(df_filial)} linhas")

    client.load_table_from_dataframe(
        df_produto, TABLE_STG_PRODUTO, job_config=job_config
    ).result()
    print(f"OK -> {TABLE_STG_PRODUTO}: {len(df_produto)} linhas")

    client.load_table_from_dataframe(
        df_vendas, TABLE_STG_VENDAS, job_config=job_config
    ).result()
    print(f"OK -> {TABLE_STG_VENDAS}: {len(df_vendas)} linhas")

    print("Carga dos tres CSVs (staging) finalizada com sucesso.")


# Orquestra: CSVs locais -> padronizar_colunas + preparar_vendas_para_grafico (extract) -> BQ.
def main():
    client = criar_cliente_bq()
    garantir_conjunto_dados(client, PROJECT_ID, DATASET_ID, BQ_LOCATION)

    df_filial_raw, df_produto_raw, df_vendas_raw = ler_csvs_raw()
    df_filial, df_produto, df_vendas = padronizar_colunas(
        df_filial_raw, df_produto_raw, df_vendas_raw
    )
    df_vendas = preparar_vendas_para_grafico(df_vendas)

    carregar_tabelas_bigquery(client, df_filial, df_produto, df_vendas)


if __name__ == "__main__":
    main()
