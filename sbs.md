# Step by Step - Projeto Avaliativo Modulo 2

## 1) Preparacao inicial

- [ ] Criar/organizar o repositorio no GitHub.
- [ ] Garantir estrutura de pastas por etapa: `raw`, `extract`, `transform`, `load`, `processed`, `dashboard`.
- [ ] Criar/atualizar `README.md` com objetivo do projeto e instrucoes de execucao.

## 2) Ambiente de desenvolvimento

- [ ] Criar ambiente virtual (`venv`).
- [ ] Instalar bibliotecas necessarias (pandas, matplotlib/seaborn/plotly, etc.).
- [ ] Salvar dependencias em `requirements.txt`.

## 3) Camada Bronze (Raw)

- [ ] Colocar os arquivos originais em `raw` sem alterar conteudo.
- [ ] Documentar quais arquivos entraram e data da carga.

## 4) Camada Silver (Trusted)

- [ ] Ler dados com Python/Pandas.
- [ ] Padronizar nomes de colunas para `snake_case`.
- [ ] Corrigir tipos de dados (datas, numericos, texto).
- [ ] Tratar valores nulos conforme regra definida.
- [ ] Remover duplicidades.
- [ ] Validar integridade basica entre tabelas.
- [ ] Salvar datasets tratados (CSV/tabela) na camada Silver.

## 5) Camada Gold (Business)

- [ ] Criar agregacoes de negocio para BI.
- [ ] Preparar dados para KPIs e visoes obrigatorias.
- [ ] Criar a view/consulta de negocio com market share mensal e MoM (quando aplicavel).
- [ ] Salvar/publicar dataset final da camada Gold.

## 6) Estrutura ETL obrigatoria

- [ ] Separar scripts por responsabilidade:
  - `extract.py`
  - `transform.py`
  - `load.py`
- [ ] Evitar script linear grande; usar funcoes.
- [ ] Criar `main.py` para orquestrar Bronze -> Silver -> Gold em ordem.

## 7) Logging e tratamento de erro

- [ ] Adicionar `logging` com inicio/fim de cada etapa.
- [ ] Capturar e registrar erros de leitura, transformacao e carga.
- [ ] Garantir mensagens claras para depuracao.

## 8) EDA (analise exploratoria)

- [ ] Gerar analise textual: tipos, nulos, duplicados, cardinalidade.
- [ ] Criar graficos de validacao (distribuicoes, top categorias, nulos).
- [ ] Salvar relatorios graficos em pasta de saida.

## 9) Dashboard (Looker Studio ou Streamlit)

- [ ] Construir os KPIs principais:
  - Market Share do negocio (PP/Total)
  - Gap de Preco Medio (Clamed vs Concorrencia)
  - Brick com maior potencial de crescimento
- [ ] Construir visoes obrigatorias:
  - Mapa de Calor ou Treemap por Brick
  - Linha do tempo PP vs Concorrentes (ultimos meses)
- [ ] Adicionar filtros dinamicos obrigatorios:
  - Brick
  - Mes
  - Categoria de Produto

## 10) Storytelling e organizacao visual

- [ ] Organizar paginas/setores com conexao logica.
- [ ] Colocar titulos claros em todas as visoes.
- [ ] Melhorar legibilidade (cores, escalas, rotulos, espacamento).
- [ ] Garantir que filtros gerem novos insights.

## 11) Checklist de avaliacao (antes de entregar)

- [ ] Documentacao clara (README completo).
- [ ] Padronizacao + tratamento de nulos/tipos.
- [ ] Remocao de duplicatas + validacao de integridade.
- [ ] Conexao com base funcional (se opcao SQL).
- [ ] Scripts ETL separados por etapa.
- [ ] Uso adequado da ferramenta de BI.
- [ ] KPIs e visoes obrigatorias implementados.
- [ ] Boa visualizacao e storytelling.
- [ ] Interatividade real via filtros.

## 12) Entrega

- [ ] Subir codigo final no GitHub.
- [ ] Manter repositorio privado.
- [ ] Adicionar os usuarios avaliadores solicitados no enunciado.
- [ ] Enviar link no AVA dentro do prazo.
- [ ] Nao alterar o repositorio apos entrega, ate a correcao.
