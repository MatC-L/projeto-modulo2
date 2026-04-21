import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

FILIAIS = (
    r"C:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\projeto\raw\dim_filial.csv"
)

PRODUTOS = (
    r"C:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\projeto\raw\dim_produto.csv"
)

VENDAS = (
    r"C:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2"
    r"\projeto\raw\fato_vendas.csv"
)

df_filiais_raw = pd.read_csv(FILIAIS)

df_produtos_raw = pd.read_csv(PRODUTOS)

df_vendas_raw = pd.read_csv(VENDAS)

print("\n" + "=" * 100)
print("ANALISE DE dim_filial.csv:")
print("=" * 100)
print(f"Linhas: {len(df_filiais_raw)} | Colunas: {len(df_filiais_raw.columns)}")
print(f"Nome das colunas: {list(df_filiais_raw)}")
print("\nQualidade dos dados:")
print(df_filiais_raw.dtypes.to_string())
print("\nAmostra (head):")
print(df_filiais_raw.head().to_string(index=False))

nulls_filiais = df_filiais_raw.isna().sum()
nulls_pct_filiais = (nulls_filiais / len(df_filiais_raw) * 100).round(2)
nulls_report_filiais = pd.DataFrame(
    {"nulos": nulls_filiais, "pct_nulos": nulls_pct_filiais}
).sort_values("nulos", ascending=False)
print("\nNulos por coluna:")
print(nulls_report_filiais.to_string())
print(
    f"\nLinhas duplicadas (todas as colunas): "
    f"{int(df_filiais_raw.duplicated().sum())}"
)

obj_cols_filiais = df_filiais_raw.select_dtypes(include=["object", "string"]).columns.tolist()
num_cols_filiais = df_filiais_raw.select_dtypes(include=["number"]).columns.tolist()

num_cols_filiais_stats = [
    c for c in num_cols_filiais
    if all(token not in c.lower() for token in ["filial_id", "brick", "regiao", "cluster"])
]

if obj_cols_filiais:
    print("\nCardinalidade e top valores (colunas de texto):")
    for col in obj_cols_filiais:
        nunique = df_filiais_raw[col].nunique(dropna=True)
        top_values = df_filiais_raw[col].value_counts(dropna=False).head()
        print(f"\n- {col} | unicos: {nunique}")
        print(top_values.to_string())

if num_cols_filiais_stats:
    print("\nEstatisticas descritivas (colunas numéricas):")
    print(df_filiais_raw[num_cols_filiais_stats].describe().T.to_string())
else:
    print("\nEstatisticas descritivas (colunas numéricas):")
    print("Não há colunas numéricas, apenas identificadores.")

print("\n" + "=" * 100)
print("ANALISE: dim_produtos.csv (original)")
print("=" * 100)
print(f"Linhas{len(df_produtos_raw)} | Colunas: {len(df_produtos_raw.columns)}")
print(f"Nome das colunas: {list(df_produtos_raw.columns)}")
print(f"Qualidade dos dados:")
print(df_produtos_raw.dtypes.to_string())
print("\nAmostra: ")
print(df_produtos_raw.head().to_string(index=False))

nulls_produtos = df_produtos_raw.isna().sum()

nulls_produtos_pct = (nulls_produtos / len(df_produtos_raw) * 100).round(2)

nulls_report_produtos = pd.DataFrame(
    {"nulos": nulls_produtos, "percentual_nulos": nulls_produtos_pct}
).sort_values("nulos", ascending=False)

print("\nNulos por coluna:")
print(nulls_report_produtos.to_string())
print("Linhas e colunas duplicadas: ")
print(f"\nLinhas duplicadas (todas as colunas): {int(df_produtos_raw).duplicated().sum()}")

obj_cols_produtos = df_produtos_raw.select_dtypes(include=["object", "string"]).columns.tolist()
num_cols_produtos = df_produtos_raw.select_dtypes(include=["number"]).columns.tolist()

num_cols_produtos_stats = [
    c for c in num_cols_produtos
    if all(token not in c.lower() for token in ["produtos_id", "categoria", "nome_produto"])
]

if obj_cols_produtos:
    print("\nCardinalidade e top valores (colunas de texto):")
    for col in obj_cols_produtos:
        nunique = df_produtos_raw[col].nunique(dropna=True)
        top_values = df_produtos_raw[col].value_counts(dropna=False).head()
        print(top_values.to_string())
else:
    print("\nEstatísticas descritivas (colunas numéricas):")
    print("Sem colunas numéricas analíticas (apenas identificadores/códigos).")



rename_map_filiais = {}
for col in df_filiais_raw.columns:
    new_col = (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        .replace("/", "_")
    )
    rename_map_filiais[col] = new_col
df_filiais = df_filiais_raw.rename(columns=rename_map_filiais)

rename_map_produtos = {}
for col in df_produtos_raw.columns:
    new_col = (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "_")
        .replace("-", "_")
        .replace("/", "_")
    )
    rename_map_produtos[col] = new_col
df_produtos = df_produtos_raw.rename(columns=rename_map_produtos)

print("\n" + "=" * 100)
print("ANÁLISE: fato_vendas.csv (original)")
print("=" * 100)
print(f"Linhas: {len(df_vendas_raw)} | Colunas {len(df_vendas_raw.columns)}")
print(f"Colunas: {list(df_produtos_raw.columns)}")
print("\nTipos de dados:")
print(df_vendas_raw.dtypes.to_string())
print("\nAmostra (head): ")
print(df_vendas_raw.head().to_string(index=False))

nulls_vendas = df_vendas_raw.isna().sum()
nulls_vendas_pct = (nulls_vendas / len(df_vendas_raw) * 100).round(2)
nulls_report_vendas = pd.DataFrame(
    {"nulos": nulls_vendas, "percentual_nulos": nulls_vendas_pct}
).sort_values("nulos", ascending=False)
print("\nNulos por coluna:")
print(nulls_report_vendas.to_string())
print(f"Linhas duplicadas no dataframe: {int(df_vendas_raw.duplicated().sum())}")

obj_cols_vendas = df_vendas_raw.select_dtypes(include=["object", "string"]).columns.tolist()
num_cols_vendas = df_vendas_raw.select_dtypes(include=["number"]).columns.tolist()

num_cols_vendas_stats = [
    c for c in num_cols_vendas
    if all (token not in c.lower() for token in ["data", "produto_id", "filial_id", "empresa"])
]

if obj_cols_vendas:
    print("\nCardinalidade e top valores:")
    for col in obj_cols_vendas:
        nunique = df_vendas_raw[col].nunique(dropna=True)
        top_values = df_vendas_raw[col].value_counts(dropna=False).head()
        print(f"\n- {col} | Unicos: {nunique}")
        print(top_values.to_string())

if num_cols_vendas_stats:
    print("\nEstatísticas descritivas das colunas numéricas:")
    print(df_vendas_raw[num_cols_vendas_stats].describe().T.to_string())
else:
    print("\nEstatísticas descritivas (colunas numéricas):")
    print("Sem colunas numéricas, somente identificadores.")

rename_map_vendas = {}
for col in df_vendas_raw.columns:
    new_col = (
        str(col)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        .replace("/", "_")
    )
    rename_map_vendas[col] = new_col
df_vendas = df_vendas_raw.rename(columns=rename_map_vendas)

#-----------------------------------------------------------------
# Relatório gráfico estatístico
#------------------------------------------------------------------

output_dir = Path(
    r"C:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2\projeto\processed\visualization_graphs"
)
output_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = output_dir / f"relatorio_estatisticas_fato_vendas_{timestamp}.png"

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Relatório estatístico — fato_vendas", fontsize=16, fontweight="bold")

# 1) Receita por empresa
rec_emp = df_vendas.groupby("empresa", dropna=False)["receita"].sum()
axes[0, 0].bar(rec_emp.index.astype(str), rec_emp.values, color=["#2ecc71", "#3498db", "#9b59b6"][: len(rec_emp)])
axes[0, 0].set_title("Receita total por empresa")
axes[0, 0].set_ylabel("Receita")
axes[0, 0].grid(axis="y", alpha=0.3)

# 2) Top 5 produtos por receita
df_top = (
    df_vendas.groupby("produto_id", dropna=False)["receita"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
axes[0, 1].bar(df_top.index.astype(str), df_top.values, color="#34495e")
axes[0, 1].set_title("Top 5 produtos por receita")
axes[0, 1].set_ylabel("Receita")
axes[0, 1].tick_params(axis="x", rotation=45)
axes[0, 1].grid(axis="y", alpha=0.3)

# 3) Distribuição da receita (por transação)
axes[1, 0].hist(df_vendas["receita"].dropna(), bins=30, color="#2ecc71", edgecolor="black", alpha=0.8)
axes[1, 0].set_title("Distribuição da receita (por linha)")
axes[1, 0].set_xlabel("Receita")
axes[1, 0].set_ylabel("Frequência")
axes[1, 0].grid(axis="y", alpha=0.3)

# 4) Nulos por coluna
if null_report_vendas.empty:
    axes[1, 1].text(0.5, 0.5, "Sem nulos", ha="center", va="center")
    axes[1, 1].set_axis_off()
else:
    null_plot = null_report_vendas.reset_index().rename(columns={"index": "coluna"})
    axes[1, 1].barh(null_plot["coluna"], null_plot["nulos"], color="#e67e22")
    axes[1, 1].set_title("Nulos por coluna (fato_vendas)")
    axes[1, 1].set_xlabel("Quantidade de nulos")
    axes[1, 1].grid(axis="x", alpha=0.3)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(output_file, dpi=200, bbox_inches="tight")
plt.close(fig)
print(f"Relatório gráfico salvo em: {output_file}")