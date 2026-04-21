import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

FILE_FILIAL = (
    r"c:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\mini-projeto\samples\filial-brick_sample.xlsx"
)
FILE_MS = (
    r"c:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\mini-projeto\samples\MS_12_2022_sample.xlsx"
)

# Inicio do script com leitura dos arquivos via pandas.
df_filial_raw = pd.read_excel(FILE_FILIAL)
df_ms_raw = pd.read_excel(FILE_MS)

print("\n" + "=" * 100)
print("VISUALIZACAO DE DADOS - IQVIA")
print("=" * 100)
print(f"Arquivo filial: {FILE_FILIAL}")
print(f"Arquivo MS: {FILE_MS}")

# ---------------------------
# Analise: filial (original)
# ---------------------------
print("\n" + "=" * 100)
print("ANALISE: filial-brick_sample.xlsx (original)")
print("=" * 100)
print(f"Linhas: {len(df_filial_raw)} | Colunas: {len(df_filial_raw.columns)}")
print(f"Colunas: {list(df_filial_raw.columns)}")
print("\nTipos de dados:")
print(df_filial_raw.dtypes.to_string())
print("\nAmostra (head):")
print(df_filial_raw.head(8).to_string(index=False))

nulls_filial = df_filial_raw.isna().sum()
nulls_pct_filial = (nulls_filial / len(df_filial_raw) * 100).round(2)
null_report_filial = pd.DataFrame(
    {"nulos": nulls_filial, "pct_nulos": nulls_pct_filial}
).sort_values("nulos", ascending=False)
print("\nNulos por coluna:")
print(null_report_filial.to_string())
print(
    f"\nLinhas duplicadas (todas as colunas): "
    f"{int(df_filial_raw.duplicated().sum())}"
)

obj_cols_filial = df_filial_raw.select_dtypes(include=["object", "string"]).columns.tolist()
num_cols_filial = df_filial_raw.select_dtypes(include=["number"]).columns.tolist()

# IDs/codigos nao devem entrar em estatistica descritiva numerica
num_cols_filial_stats = [
    c for c in num_cols_filial
    if all(token not in c.lower() for token in ["filial", "id", "cod", "ean"])
]

if obj_cols_filial:
    print("\nCardinalidade e top valores (colunas de texto):")
    for col in obj_cols_filial:
        nunique = df_filial_raw[col].nunique(dropna=True)
        top_values = df_filial_raw[col].value_counts(dropna=False).head(10)
        print(f"\n- {col} | unicos: {nunique}")
        print(top_values.to_string())

if num_cols_filial_stats:
    print("\nEstatisticas descritivas (colunas numericas):")
    print(df_filial_raw[num_cols_filial_stats].describe().T.to_string())
else:
    print("\nEstatisticas descritivas (colunas numericas):")
    print("Sem colunas numericas analiticas (apenas identificadores/codigos).")

# -----------------------
# Analise: MS (original)
# -----------------------
print("\n" + "=" * 100)
print("ANALISE: MS_12_2022_sample.xlsx (original)")
print("=" * 100)
print(f"Linhas: {len(df_ms_raw)} | Colunas: {len(df_ms_raw.columns)}")
print(f"Colunas: {list(df_ms_raw.columns)}")
print("\nTipos de dados:")
print(df_ms_raw.dtypes.to_string())
print("\nAmostra (head):")
print(df_ms_raw.head(8).to_string(index=False))

nulls_ms = df_ms_raw.isna().sum()
nulls_pct_ms = (nulls_ms / len(df_ms_raw) * 100).round(2)
null_report_ms = pd.DataFrame(
    {"nulos": nulls_ms, "pct_nulos": nulls_pct_ms}
).sort_values("nulos", ascending=False)
print("\nNulos por coluna:")
print(null_report_ms.to_string())
print(f"\nLinhas duplicadas (todas as colunas): {int(df_ms_raw.duplicated().sum())}")

obj_cols_ms = df_ms_raw.select_dtypes(include=["object", "string"]).columns.tolist()
num_cols_ms = df_ms_raw.select_dtypes(include=["number"]).columns.tolist()

# IDs/codigos nao devem entrar em estatistica descritiva numerica
num_cols_ms_stats = [
    c for c in num_cols_ms
    if all(token not in c.lower() for token in ["filial", "id", "cod", "ean"])
]

if obj_cols_ms:
    print("\nCardinalidade e top valores (colunas de texto):")
    for col in obj_cols_ms:
        nunique = df_ms_raw[col].nunique(dropna=True)
        top_values = df_ms_raw[col].value_counts(dropna=False).head(10)
        print(f"\n- {col} | unicos: {nunique}")
        print(top_values.to_string())

if num_cols_ms_stats:
    print("\nEstatisticas descritivas (colunas numericas):")
    print(df_ms_raw[num_cols_ms_stats].describe().T.to_string())
else:
    print("\nEstatisticas descritivas (colunas numericas):")
    print("Sem colunas numericas analiticas (apenas identificadores/codigos).")

# -------------------------
# Normalizacao das colunas
# -------------------------
rename_map_filial = {}
for col in df_filial_raw.columns:
    new_col = (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        .replace("/", "_")
    )
    rename_map_filial[col] = new_col
df_filial = df_filial_raw.rename(columns=rename_map_filial)

rename_map_ms = {}
for col in df_ms_raw.columns:
    new_col = (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        .replace("/", "_")
    )
    rename_map_ms[col] = new_col
df_ms = df_ms_raw.rename(columns=rename_map_ms)

# --------------------------------------------------------------------
# Ajuste final de nomes para equivalencia com schema SQL do BigQuery
# --------------------------------------------------------------------
# dim_filial (schema): filial, fk_brick ...
# o arquivo de origem pode vir com variacoes de encoding para "cod filial"
if "c�d_filial" in df_filial.columns:
    df_filial = df_filial.rename(columns={"c�d_filial": "filial"})
elif "cód_filial" in df_filial.columns:
    df_filial = df_filial.rename(columns={"cód_filial": "filial"})
elif "cod_filial" in df_filial.columns:
    df_filial = df_filial.rename(columns={"cod_filial": "filial"})

# fact_vendas_iqvia (schema): vol_concorrente_indep, vol_concorrente_rede, vol_clamed_pp
df_ms = df_ms.rename(
    columns={
        "tipo_informacao_si_bandeira_concorrente_unidade": "vol_concorrente_indep",
        "tipo_informacao_so_bandeira_concorrente_unidade": "vol_concorrente_rede",
        "tipo_informacao_so_bandeira_preco_popular_unidade": "vol_clamed_pp",
    }
)

print("\n" + "=" * 100)
print("ANALISE: filial-brick_sample.xlsx (colunas normalizadas)")
print("=" * 100)
print(f"Colunas: {list(df_filial.columns)}")
print(df_filial.head(8).to_string(index=False))

print("\n" + "=" * 100)
print("ANALISE: MS_12_2022_sample.xlsx (colunas normalizadas)")
print("=" * 100)
print(f"Colunas: {list(df_ms.columns)}")
print(df_ms.head(8).to_string(index=False))

# Estatisticas descritivas focadas nas medidas de negocio (volumes)
colunas_volume = [
    "vol_concorrente_indep",
    "vol_concorrente_rede",
    "vol_clamed_pp",
]
for c in colunas_volume:
    if c not in df_ms.columns:
        df_ms[c] = pd.NA

for c in colunas_volume:
    df_ms[c] = pd.to_numeric(df_ms[c], errors="coerce").fillna(0.0)

df_ms["vol_total_mercado"] = (
    df_ms["vol_concorrente_indep"] +
    df_ms["vol_concorrente_rede"] +
    df_ms["vol_clamed_pp"]
)
df_ms["participacao_clamed"] = (
    (df_ms["vol_clamed_pp"] / df_ms["vol_total_mercado"].replace(0, pd.NA)) * 100
).fillna(0.0)

print("\nEstatisticas descritivas (medidas normalizadas):")
print(
    df_ms[
        ["vol_concorrente_indep", "vol_concorrente_rede", "vol_clamed_pp", "vol_total_mercado", "participacao_clamed"]
    ].describe().T.to_string()
)

# -----------------------------------
# Consistencia entre os dois arquivos
# -----------------------------------
print("\n" + "=" * 100)
print("CONSISTENCIA ENTRE ARQUIVOS")
print("=" * 100)

filial_cols = {c.lower(): c for c in df_filial.columns}
ms_cols = {c.lower(): c for c in df_ms.columns}
brick_filial = filial_cols.get("brick")
brick_ms = ms_cols.get("brick")

if brick_filial and brick_ms:
    fset = set(df_filial[brick_filial].dropna().astype(str).str.strip())
    mset = set(df_ms[brick_ms].dropna().astype(str).str.strip())
    print(f"Bricks no arquivo filial: {len(fset)}")
    print(f"Bricks no arquivo MS: {len(mset)}")
    print(f"Interseccao: {len(fset & mset)}")
    print(f"Bricks no MS que nao existem em filial: {len(mset - fset)}")
    print(f"Bricks em filial que nao aparecem no MS: {len(fset - mset)}")
    if mset - fset:
        print("\nExemplos de bricks no MS sem mapeamento em filial:")
        print("\n".join(sorted(list(mset - fset))[:20]))
else:
    print("Nao foi possivel comparar BRICK entre os arquivos.")

# -----------------------------------
# Relatorio grafico de estatisticas
# -----------------------------------
print("\n" + "=" * 100)
print("RELATORIO GRAFICO DE ESTATISTICAS")
print("=" * 100)

output_dir = Path(
    r"c:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2\mini-projeto\processed\visualization_graphs"
)
output_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = output_dir / f"relatorio_estatisticas_iqvia_{timestamp}.png"

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Relatorio Estatistico - IQVIA (MS_12_2022_sample)", fontsize=16, fontweight="bold")

# 1) Volumes totais por categoria
totais = pd.Series(
    {
        "Clamed PP": df_ms["vol_clamed_pp"].sum(),
        "Conc. Indep.": df_ms["vol_concorrente_indep"].sum(),
        "Conc. Rede": df_ms["vol_concorrente_rede"].sum(),
    }
)
axes[0, 0].bar(totais.index, totais.values, color=["#2ecc71", "#3498db", "#9b59b6"])
axes[0, 0].set_title("Volumes Totais por Categoria")
axes[0, 0].set_ylabel("Unidades")
axes[0, 0].grid(axis="y", alpha=0.3)

# 2) Top produtos por volume total
df_top = df_ms.sort_values("vol_total_mercado", ascending=False).head(5).copy()
axes[0, 1].bar(df_top["ean"].astype(str), df_top["vol_total_mercado"], color="#34495e")
axes[0, 1].set_title("Top 5 Produtos por Volume Total")
axes[0, 1].set_ylabel("Unidades")
axes[0, 1].tick_params(axis="x", rotation=45)
axes[0, 1].grid(axis="y", alpha=0.3)

# 3) Distribuicao da participacao clamed
axes[1, 0].hist(df_ms["participacao_clamed"], bins=8, color="#2ecc71", edgecolor="black", alpha=0.8)
axes[1, 0].set_title("Distribuicao da Participacao Clamed (%)")
axes[1, 0].set_xlabel("Participacao (%)")
axes[1, 0].set_ylabel("Frequencia")
axes[1, 0].grid(axis="y", alpha=0.3)

# 4) Nulos por coluna (dataset original MS)
null_plot = null_report_ms.reset_index().rename(columns={"index": "coluna"})
axes[1, 1].barh(null_plot["coluna"], null_plot["nulos"], color="#e67e22")
axes[1, 1].set_title("Nulos por Coluna (MS original)")
axes[1, 1].set_xlabel("Quantidade de nulos")
axes[1, 1].grid(axis="x", alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Relatorio grafico salvo em: {output_file}")

print("\n" + "=" * 100)
print("FIM")
print("=" * 100)
print("Analise concluida com sucesso.")
