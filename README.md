# Arquitetura — Projeto avaliativo Módulo 2 (Clamed)

Projeto alinhado ao **enunciado** (`enunciado.txt`): arquitetura **Medallion**, **Python + Pandas** para leitura e tratamento, **BigQuery** como “nuvem” (Opção B estendida com SQL analítico), **EDA com Matplotlib** e **Looker Studio** para consumo.

**Pipeline real:** CSVs em `raw/` → carga com Python no BigQuery (staging) → transformação SQL (modelo dimensional + fato) → tabelas materializadas para dashboard → Looker Studio.

```mermaid
%%{init: {
  "theme": "base",
  "themeVariables": {
    "background": "#050014",
    "primaryColor": "#1a0a2e",
    "primaryTextColor": "#e8dcff",
    "primaryBorderColor": "#00f5ff",
    "secondaryColor": "#12061f",
    "tertiaryColor": "#0d0221",
    "lineColor": "#7df9ff",
    "arrowheadColor": "#ff2a6d",
    "textColor": "#d4c4f7",
    "fontFamily": "ui-sans-serif, system-ui, sans-serif"
  },
  "flowchart": {
    "curve": "basis",
    "padding": 12
  }
}}%%
flowchart LR
  subgraph extract["⚡ EXTRACT (local)"]
    X1["raw/dim_filial.csv"]
    X2["raw/dim_produto.csv"]
    X3["raw/fato_vendas.csv"]
    EDA["extract/visualizar_dados.py<br/>EDA + PNG em processed/"]
    X1 --> EDA
    X2 --> EDA
    X3 --> EDA
  end

  subgraph load["⚡ LOAD — load/upload_data_BQ.py"]
    PY["pandas + google-cloud-bigquery<br/>padronizar_colunas + receita numérica<br/>WRITE_TRUNCATE"]
    STG1[("stg_dim_filial")]
    STG2[("stg_dim_produto")]
    STG3[("stg_fato_vendas")]
    PY --> STG1
    PY --> STG2
    PY --> STG3
  end

  subgraph transform["⚡ TRANSFORM — transform/criacao_dataset/create_and_transform_dataset.sql"]
    DIM1[("dim_brick")]
    DIM2[("dim_filial")]
    SCD[("dim_produto_scd2")]
    FACT[("fact_vendas")]
    STG1 --> DIM1
    STG1 --> DIM2
    DIM1 --> DIM2
    STG2 --> SCD
    STG3 --> FACT
    DIM1 --> FACT
    SCD -->|fk_sk_produto| FACT
  end

  subgraph viz["⚡ DASHBOARD — transform/dashboard/CTEs_dashboard_modulo2.sql"]
    DASH[("fact_vendas_dashboard")]
    PIZZA1[("pizza_consolidado_total")]
    PIZZA2[("pizza_produto_destaque")]
    BARRAS[("grafico_barras_top_produtos")]
    STATS[("estatisticas_gerais")]
    SERIE[("serie_participacao_tempo")]
    FACT --> DASH
    DIM1 --> DASH
    DASH --> PIZZA1
    DASH --> PIZZA2
    DASH --> BARRAS
    DASH --> STATS
    FACT --> SERIE
  end

  subgraph consume["⚡ CONSUMO"]
    LK["Looker Studio<br/>BigQuery: dataset `dataset`"]
  end

  X1 --> PY
  X2 --> PY
  X3 --> PY
  PIZZA1 --> LK
  PIZZA2 --> LK
  BARRAS --> LK
  STATS --> LK
  DASH --> LK
  SERIE --> LK

  linkStyle default stroke:#00fff7,stroke-width:3px

  classDef cyberExtract fill:#12082a,stroke:#00f5ff,stroke-width:2px,color:#9bf6ff
  classDef cyberLoad fill:#1a0528,stroke:#ff2a6d,stroke-width:2px,color:#ffc9e6
  classDef cyberStaging fill:#0a1628,stroke:#00fff0,stroke-width:2px,color:#7df9ff
  classDef cyberModel fill:#14061f,stroke:#b967ff,stroke-width:2px,color:#e0b8ff
  classDef cyberScd fill:#2a0a32,stroke:#ff00ea,stroke-width:2px,color:#ff9eed
  classDef cyberViz fill:#1a0f2e,stroke:#fcee0a,stroke-width:2px,color:#fff8b8
  classDef cyberConsume fill:#061a12,stroke:#39ff14,stroke-width:3px,color:#b8ffc4

  class X1,X2,X3,EDA cyberExtract
  class PY cyberLoad
  class STG1,STG2,STG3 cyberStaging
  class DIM1,DIM2,FACT cyberModel
  class SCD cyberScd
  class DASH,PIZZA1,PIZZA2,BARRAS,STATS,SERIE cyberViz
  class LK cyberConsume

  style extract fill:#080018,stroke:#00e5ff,stroke-width:2px,color:#00e5ff
  style load fill:#080018,stroke:#ff2a6d,stroke-width:2px,color:#ff6b9d
  style transform fill:#080018,stroke:#b967ff,stroke-width:2px,color:#d4a5ff
  style viz fill:#080018,stroke:#fcee0a,stroke-width:2px,color:#fff066
  style consume fill:#080018,stroke:#39ff14,stroke-width:2px,color:#5cff5c
```

## Resumo por etapa

| Etapa | O que acontece |
|-------|----------------|
| **Bronze (Raw)** | Três CSVs imutáveis em `raw/`: `dim_filial.csv`, `dim_produto.csv`, `fato_vendas.csv` (colunas conforme amostra do curso). |
| **Extract / EDA** | `extract/visualizar_dados.py` — análise exploratória (tipos, nulos, cardinalidade), `snake_case` via `padronizar_colunas`, coerção de `receita` para gráficos (`preparar_vendas_para_grafico`), PNG em `processed/relatorio_estatistico/`. O pacote `extract` é importável (`extract/__init__.py`). |
| **Load (staging BQ)** | `load/upload_data_BQ.py` — lê os CSVs, reutiliza `padronizar_colunas` + `preparar_vendas_para_grafico`, cria o dataset se não existir e carrega com `WRITE_TRUNCATE` para `stg_dim_filial`, `stg_dim_produto`, `stg_fato_vendas` no dataset **`staging_modulo2`** (padrão). Variáveis: `GCP_PROJECT_ID`, `BQ_DATASET_ID`, `BQ_LOCATION`. |
| **Silver (trusted BQ)** | `transform/criacao_dataset/create_and_transform_dataset.sql` — lê staging em `` `projeto-modulo2.staging_modulo2` `` e grava em `` `projeto-modulo2.dataset` ``: `dim_brick` → `dim_filial` → `dim_produto_scd2` → `fact_vendas` (join inner com `dim_filial`; `LEFT JOIN` produto ativo). |
| **Gold (dashboard BQ)** | `transform/dashboard/CTEs_dashboard_modulo2.sql` — materializa `fact_vendas_dashboard`, pizzas, top produtos, `estatisticas_gerais` e `serie_participacao_tempo` (série mensal de shares). |
| **Looker Studio** | Conecta ao BigQuery; guia de campos e storytelling em `transform/dashboard/guia_dashboard_banca_modulo2.md`. |

## Dados brutos (`raw/`)

| Arquivo | Conteúdo (grão) |
|---------|------------------|
| `dim_filial.csv` | Loja: `filial_id`, `brick`, `regiao`, `cluster`. |
| `dim_produto.csv` | Produto: `produto_id`, `categoria`, `nome_produto`. |
| `fato_vendas.csv` | Venda: `data`, `produto_id`, `filial_id`, `empresa`, `volume`, `preco_unitario`, `receita` (pode conter texto inválido em `receita`; tratado no Python antes da carga). |

## Como executar (ordem)

1. **Credenciais Google Cloud** (Application Default ou conta de serviço) com permissão no projeto e datasets.
2. **Ambiente Python** na pasta `projeto/` (ex.: `python -m venv .venv` e instalar `pandas`, `google-cloud-bigquery`, `pyarrow`, `matplotlib`).
3. **Carga staging:** `python load/upload_data_BQ.py`
4. **Silver:** executar no BigQuery o script `transform/criacao_dataset/create_and_transform_dataset.sql`.
5. **Gold / dashboard:** executar `transform/dashboard/CTEs_dashboard_modulo2.sql`.
6. **EDA local (opcional):** `python extract/visualizar_dados.py`

## Observações técnicas importantes

- No SQL do dashboard, os campos `vol_*` representam **receita** repartida por `empresa` (nomenclatura herdada do template IQVIA). `vol_concorrente_indep` tende a **zero** se só existirem `Clamed` e `Concorrente` no fato.
- A tabela `serie_participacao_tempo` expõe `receita_clamed`, `receita_rede`, `share_clamed_pct` e `share_rede_pct`; **não** expõe `receita_total` no `SELECT` final — use `receita_rede > 0` ou acrescente a coluna no SQL se precisar dela no Looker.
- O enunciado pede também **view `vw_market_share_mensal` com MoM**, **KPIs adicionais** (gap de preço, brick com maior potencial), **mapa/treemap por brick** e **filtros** (brick, mês, categoria). O que está neste repositório cobre o núcleo de **market share + série temporal + guia de banca**; complete o restante conforme o roteiro da disciplina.

## Estrutura de pastas

```
projeto/
  raw/                 # Bronze
  extract/             # EDA + funções reutilizadas na carga
  load/                # Carga BigQuery (staging)
  transform/
    criacao_dataset/   # SQL silver
    dashboard/         # SQL gold + guia Looker
  processed/           # Saída EDA (PNG)
  enunciado.txt
  sbs.md
```
