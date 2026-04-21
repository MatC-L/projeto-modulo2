import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import uuid

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

OUTPUT_DIR = Path(
    r"C:\Users\mateu\OneDrive\Documentos\GitHub\CienciaDeDados\Curso\modulo2\projeto\processed\relatorio_estatistico"
)


# Carrega os CSVs brutos usados na analise.
def carregar_bases():
    df_filiais_raw = pd.read_csv(FILIAIS)
    df_produtos_raw = pd.read_csv(PRODUTOS)
    df_vendas_raw = pd.read_csv(VENDAS)
    return df_filiais_raw, df_produtos_raw, df_vendas_raw


# Gera um mapa para padronizar colunas em snake_case.
def criar_rename_map(columns, ponto_para_underscore=False):
    rename_map = {}
    for col in columns:
        new_col = (
            str(col)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace(".", "_" if ponto_para_underscore else "")
            .replace("-", "_")
            .replace("/", "_")
        )
        rename_map[col] = new_col
    return rename_map


# Calcula tabela de nulos (qtd e percentual) por coluna.
def calcular_relatorio_nulos(df, nome_pct="pct_nulos"):
    nulls = df.isna().sum()
    nulls_pct = (nulls / len(df) * 100).round(2)
    return pd.DataFrame({"nulos": nulls, nome_pct: nulls_pct}).sort_values(
        "nulos", ascending=False
    )


# Imprime cardinalidade e top valores das colunas de texto.
def imprimir_cardinalidade_texto(df, titulo, mostrar_nunique=True):
    obj_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    if not obj_cols:
        return

    print(titulo)
    for col in obj_cols:
        nunique = df[col].nunique(dropna=True)
        top_values = df[col].value_counts(dropna=False).head()
        if mostrar_nunique:
            print(f"\n- {col} | unicos: {nunique}")
        print(top_values.to_string())


# Imprime estatisticas descritivas para colunas numericas analiticas.
def imprimir_estatisticas_numericas(df, tokens_ignorados, mensagem_vazio):
    num_cols = df.select_dtypes(include=["number"]).columns.tolist()
    num_cols_stats = [
        c
        for c in num_cols
        if all(token not in c.lower() for token in tokens_ignorados)
    ]

    if num_cols_stats:
        print(df[num_cols_stats].describe().T.to_string())
    else:
        print(mensagem_vazio)


# Executa e imprime a analise exploratoria de filiais.
def analisar_filiais(df_filiais_raw):
    print("\n" + "=" * 100)
    print("ANALISE DE dim_filial.csv:")
    print("=" * 100)
    print(f"Linhas: {len(df_filiais_raw)} | Colunas: {len(df_filiais_raw.columns)}")
    print(f"Nome das colunas: {list(df_filiais_raw)}")
    print("\nQualidade dos dados:")
    print(df_filiais_raw.dtypes.to_string())
    print("\nAmostra (head):")
    print(df_filiais_raw.head().to_string(index=False))

    nulls_report_filiais = calcular_relatorio_nulos(df_filiais_raw, "pct_nulos")
    print("\nNulos por coluna:")
    print(nulls_report_filiais.to_string())
    print(
        f"\nLinhas duplicadas (todas as colunas): "
        f"{int(df_filiais_raw.duplicated().sum())}"
    )

    imprimir_cardinalidade_texto(
        df_filiais_raw, "\nCardinalidade e top valores (colunas de texto):"
    )
    print("\nEstatisticas descritivas (colunas numéricas):")
    imprimir_estatisticas_numericas(
        df_filiais_raw,
        tokens_ignorados=["filial_id", "brick", "regiao", "cluster"],
        mensagem_vazio="Não há colunas numéricas, apenas identificadores.",
    )


# Executa e imprime a analise exploratoria de produtos.
def analisar_produtos(df_produtos_raw):
    print("\n" + "=" * 100)
    print("ANALISE: dim_produtos.csv (original)")
    print("=" * 100)
    print(f"Linhas: {len(df_produtos_raw)} | Colunas: {len(df_produtos_raw.columns)}")
    print(f"Nome das colunas: {list(df_produtos_raw.columns)}")
    print("Qualidade dos dados:")
    print(df_produtos_raw.dtypes.to_string())
    print("\nAmostra:")
    print(df_produtos_raw.head().to_string(index=False))

    nulls_report_produtos = calcular_relatorio_nulos(df_produtos_raw, "percentual_nulos")
    print("\nNulos por coluna:")
    print(nulls_report_produtos.to_string())
    print("Linhas e colunas duplicadas:")
    print(
        f"\nLinhas duplicadas (todas as colunas): "
        f"{int(df_produtos_raw.duplicated().sum())}"
    )

    imprimir_cardinalidade_texto(
        df_produtos_raw,
        "\nCardinalidade e top valores (colunas de texto):",
        mostrar_nunique=False,
    )
    print("\nEstatísticas descritivas (colunas numéricas):")
    imprimir_estatisticas_numericas(
        df_produtos_raw,
        tokens_ignorados=["produto_id", "categoria", "nome_produto"],
        mensagem_vazio="Sem colunas numéricas analíticas (apenas identificadores/códigos).",
    )


# Executa e imprime a analise exploratoria de vendas.
def analisar_vendas(df_vendas_raw):
    print("\n" + "=" * 100)
    print("ANÁLISE: fato_vendas.csv (original)")
    print("=" * 100)
    print(f"Linhas: {len(df_vendas_raw)} | Colunas: {len(df_vendas_raw.columns)}")
    print(f"Colunas: {list(df_vendas_raw.columns)}")
    print("\nTipos de dados:")
    print(df_vendas_raw.dtypes.to_string())
    print("\nAmostra (head):")
    print(df_vendas_raw.head().to_string(index=False))

    nulls_report_vendas = calcular_relatorio_nulos(df_vendas_raw, "percentual_nulos")
    print("\nNulos por coluna:")
    print(nulls_report_vendas.to_string())
    print(f"Linhas duplicadas no dataframe: {int(df_vendas_raw.duplicated().sum())}")

    obj_cols_vendas = df_vendas_raw.select_dtypes(include=["object", "string"]).columns.tolist()
    if obj_cols_vendas:
        print("\nCardinalidade e top valores:")
        for col in obj_cols_vendas:
            nunique = df_vendas_raw[col].nunique(dropna=True)
            top_values = df_vendas_raw[col].value_counts(dropna=False).head()
            print(f"\n- {col} | Unicos: {nunique}")
            print(top_values.to_string())

    print("\nEstatísticas descritivas das colunas numéricas:")
    imprimir_estatisticas_numericas(
        df_vendas_raw,
        tokens_ignorados=["data", "produto_id", "filial_id", "empresa"],
        mensagem_vazio="Sem colunas numéricas, somente identificadores.",
    )

    return nulls_report_vendas


# Padroniza os nomes de colunas dos dataframes.
def padronizar_colunas(df_filiais_raw, df_produtos_raw, df_vendas_raw):
    rename_map_filiais = criar_rename_map(df_filiais_raw.columns, ponto_para_underscore=False)
    rename_map_produtos = criar_rename_map(df_produtos_raw.columns, ponto_para_underscore=True)
    rename_map_vendas = criar_rename_map(df_vendas_raw.columns, ponto_para_underscore=False)

    df_filiais = df_filiais_raw.rename(columns=rename_map_filiais)
    df_produtos = df_produtos_raw.rename(columns=rename_map_produtos)
    df_vendas = df_vendas_raw.rename(columns=rename_map_vendas)
    return df_filiais, df_produtos, df_vendas


# Garante tipos numericos necessarios para os graficos de vendas.
def preparar_vendas_para_grafico(df_vendas):
    df_vendas = df_vendas.copy()
    receita_invalida = df_vendas["receita"].isna().sum()
    df_vendas["receita"] = pd.to_numeric(df_vendas["receita"], errors="coerce")
    novos_nulos = df_vendas["receita"].isna().sum() - receita_invalida
    if novos_nulos > 0:
        print(
            f"\nAviso: {novos_nulos} valores invalidos em 'receita' "
            f"foram convertidos para NaN para permitir os graficos."
        )
    return df_vendas


# Cria e salva o relatorio grafico estatistico de vendas.
def gerar_relatorio_grafico_vendas(df_vendas, nulls_report_vendas):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = OUTPUT_DIR / f"relatorio_estatistico_{timestamp}.png"

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Relatório estatístico — fato_vendas", fontsize=16, fontweight="bold")

    # 1) Receita por empresa
    rec_emp = df_vendas.groupby("empresa", dropna=False)["receita"].sum()
    axes[0, 0].bar(
        rec_emp.index.astype(str),
        rec_emp.values,
        color=["#2ecc71", "#3498db", "#9b59b6"][: len(rec_emp)],
    )
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
    axes[1, 0].hist(
        df_vendas["receita"].dropna(),
        bins=30,
        color="#2ecc71",
        edgecolor="black",
        alpha=0.8,
    )
    axes[1, 0].set_title("Distribuição da receita (por linha)")
    axes[1, 0].set_xlabel("Receita")
    axes[1, 0].set_ylabel("Frequência")
    axes[1, 0].grid(axis="y", alpha=0.3)

    # 4) Nulos por coluna
    if nulls_report_vendas.empty:
        axes[1, 1].text(0.5, 0.5, "Sem nulos", ha="center", va="center")
        axes[1, 1].set_axis_off()
    else:
        null_plot = nulls_report_vendas.reset_index().rename(columns={"index": "coluna"})
        axes[1, 1].barh(null_plot["coluna"], null_plot["nulos"], color="#e67e22")
        axes[1, 1].set_title("Nulos por coluna (fato_vendas)")
        axes[1, 1].set_xlabel("Quantidade de nulos")
        axes[1, 1].grid(axis="x", alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Salva em arquivo temporario e valida assinatura PNG antes de publicar.
    tmp_file = OUTPUT_DIR / f".tmp_relatorio_{uuid.uuid4().hex}.png"
    try:
        fig.savefig(tmp_file, format="png", dpi=200, bbox_inches="tight")
    finally:
        plt.close(fig)

    with open(tmp_file, "rb") as f:
        png_header = f.read(8)

    if png_header != b"\x89PNG\r\n\x1a\n":
        tmp_file.unlink(missing_ok=True)
        raise RuntimeError(
            "Arquivo gerado nao e um PNG valido. "
            "Verifique execucao e possivel interferencia externa."
        )

    tmp_file.replace(output_file)
    print(f"Relatório gráfico salvo em: {output_file}")


# Orquestra o fluxo de leitura, analise, padronizacao e relatorio grafico.
def main():
    df_filiais_raw, df_produtos_raw, df_vendas_raw = carregar_bases()

    analisar_filiais(df_filiais_raw)
    analisar_produtos(df_produtos_raw)
    nulls_report_vendas = analisar_vendas(df_vendas_raw)

    _, _, df_vendas = padronizar_colunas(df_filiais_raw, df_produtos_raw, df_vendas_raw)
    df_vendas = preparar_vendas_para_grafico(df_vendas)
    gerar_relatorio_grafico_vendas(df_vendas, nulls_report_vendas)


if __name__ == "__main__":
    main()