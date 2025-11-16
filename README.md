# GeoJSON Processor

Sistema sofisticado e dinâmico para processamento de arquivos GeoJSON com capacidades avançadas de filtragem, agrupamento, cálculos e geração de planilhas, gráficos e mapas.

## 🎯 Características

### Arquitetura Orientada a Objetos

- **Herança e Polimorfismo**: Sistema modular com classes base abstratas
- **Padrões de Design**: Factory Method, Chain of Responsibility, Facade
- **Extensibilidade**: Fácil adicionar novos processadores e geradores
- **Reutilização**: Código compartilhado através de herança

### Processamento de Dados

- **Filtragem Dinâmica**: Suporte a múltiplos operadores (==, !=, >, <, >=, <=, in, contains, between, isnull)
- **Agrupamento**: Agregações com funções estatísticas (sum, mean, median, count, min, max, std, var)
- **Cálculos**: Criação de colunas calculadas com expressões matemáticas
- **Ordenação**: Ordenação por múltiplas colunas
- **Limitação**: Seleção de top N registros

### Geração de Outputs

#### Planilhas Excel
- Formatação automática
- Congelamento de painéis
- Filtros automáticos
- Ajuste de largura de colunas

#### Gráficos
- **Barras**: Vertical e horizontal com ordenação
- **Pizza**: Com destaque de fatias e percentuais
- **Linhas**: Múltiplas séries com marcadores
- **Dispersão**: Com tamanho e cor variáveis

#### Mapas
- **Simples**: Visualização básica de geometrias
- **Coroplético**: Cores baseadas em valores de colunas
- **Calor**: Densidade e intensidade de pontos

## 📦 Instalação

### Dependências

```bash
sudo pip3 install geopandas matplotlib seaborn openpyxl
```

### Estrutura do Projeto

```
geojson_processor/
├── geojson_processor.py    # Script principal
├── processors.py            # Processadores de dados
├── generators.py            # Geradores de output
├── architecture.md          # Documentação da arquitetura
├── README.md               # Este arquivo
└── examples/               # Exemplos e testes
    ├── cidades_brasil.geojson
    ├── config_avancado.json
    ├── config_agrupamento.json
    └── output/             # Arquivos gerados
```

## 🚀 Uso

### Modo 1: Arquivo de Configuração JSON (Recomendado)

Para operações complexas com múltiplas transformações:

```bash
python3 geojson_processor.py dados.geojson --config config.json
```

#### Exemplo de Configuração

```json
{
  "operations": [
    {
      "type": "calculate",
      "calculations": [
        {
          "new_column": "densidade",
          "expression": "populacao / area_km2"
        }
      ]
    },
    {
      "type": "filter",
      "column": "populacao",
      "operator": ">",
      "value": 1000000
    },
    {
      "type": "groupby",
      "columns": ["regiao"],
      "aggregations": {
        "populacao": "sum",
        "area_km2": "mean"
      }
    },
    {
      "type": "sort",
      "columns": ["populacao"],
      "ascending": false
    }
  ],
  "outputs": [
    {
      "type": "spreadsheet",
      "path": "resultado.xlsx",
      "sheet_name": "Dados Processados"
    },
    {
      "type": "bar_chart",
      "path": "grafico.png",
      "x": "regiao",
      "y": "populacao",
      "title": "População por Região"
    },
    {
      "type": "choropleth_map",
      "path": "mapa.png",
      "column": "densidade",
      "cmap": "YlOrRd"
    }
  ]
}
```

### Modo 2: Argumentos de Linha de Comando (Simples)

Para operações rápidas sem transformações complexas:

```bash
# Apenas planilha
python3 geojson_processor.py dados.geojson --spreadsheet relatorio.xlsx

# Planilha + gráfico de barras
python3 geojson_processor.py dados.geojson \
  --spreadsheet relatorio.xlsx \
  --bar-chart grafico.png --bar-column tipo

# Mapa coroplético
python3 geojson_processor.py dados.geojson \
  --choropleth-map mapa.png --choropleth-column densidade

# Múltiplos outputs
python3 geojson_processor.py dados.geojson \
  --spreadsheet dados.xlsx \
  --bar-chart barras.png --bar-column categoria \
  --pie-chart pizza.png --pie-column tipo \
  --simple-map mapa.png
```

## 📚 Operações Disponíveis

### 1. Filter (Filtragem)

Filtra registros baseado em condições.

#### Filtro Simples

```json
{
  "type": "filter",
  "column": "populacao",
  "operator": ">",
  "value": 100000
}
```

#### Múltiplos Filtros

```json
{
  "type": "filter",
  "filters": [
    {"column": "populacao", "operator": ">", "value": 100000},
    {"column": "regiao", "operator": "in", "value": ["Sudeste", "Sul"]}
  ],
  "logic": "and"
}
```

#### Operadores Disponíveis

- `==`: Igual
- `!=`: Diferente
- `>`: Maior que
- `<`: Menor que
- `>=`: Maior ou igual
- `<=`: Menor ou igual
- `in`: Contido em lista
- `contains`: Contém substring
- `startswith`: Começa com
- `endswith`: Termina com
- `between`: Entre dois valores
- `isnull`: É nulo/não nulo

### 2. GroupBy (Agrupamento)

Agrupa dados e aplica funções de agregação.

```json
{
  "type": "groupby",
  "columns": ["estado", "regiao"],
  "aggregations": {
    "populacao": "sum",
    "area_km2": "mean",
    "pib_milhoes": "sum"
  },
  "keep_geometry": false
}
```

#### Funções de Agregação

- `sum`: Soma
- `mean`: Média
- `median`: Mediana
- `count`: Contagem
- `min`: Mínimo
- `max`: Máximo
- `std`: Desvio padrão
- `var`: Variância
- `first`: Primeiro valor
- `last`: Último valor
- `nunique`: Valores únicos

### 3. Calculate (Cálculo)

Cria novas colunas com expressões matemáticas.

```json
{
  "type": "calculate",
  "calculations": [
    {
      "new_column": "densidade",
      "expression": "populacao / area_km2"
    },
    {
      "new_column": "log_populacao",
      "expression": "log(populacao)"
    }
  ]
}
```

#### Funções Matemáticas Disponíveis

- Aritméticas: `+`, `-`, `*`, `/`, `**`
- Logarítmicas: `log`, `log10`
- Raiz: `sqrt`
- Trigonométricas: `sin`, `cos`, `tan`
- Outras: `abs`, `exp`

### 4. Sort (Ordenação)

Ordena registros por uma ou mais colunas.

```json
{
  "type": "sort",
  "columns": ["populacao", "nome"],
  "ascending": [false, true]
}
```

### 5. Limit (Limitação)

Limita o número de registros.

```json
{
  "type": "limit",
  "n": 10,
  "method": "head"
}
```

Métodos: `head`, `tail`, `sample`

## 📊 Outputs Disponíveis

### 1. Spreadsheet (Planilha Excel)

```json
{
  "type": "spreadsheet",
  "path": "relatorio.xlsx",
  "sheet_name": "Dados",
  "freeze_panes": true,
  "auto_filter": true,
  "include_geometry": false,
  "columns": ["col1", "col2"]
}
```

### 2. Bar Chart (Gráfico de Barras)

```json
{
  "type": "bar_chart",
  "path": "grafico_barras.png",
  "x": "categoria",
  "y": "valor",
  "orientation": "vertical",
  "color": "steelblue",
  "sort": true,
  "top_n": 10,
  "title": "Título do Gráfico",
  "xlabel": "Eixo X",
  "ylabel": "Eixo Y",
  "rotation": 45,
  "figsize": [10, 6]
}
```

### 3. Pie Chart (Gráfico de Pizza)

```json
{
  "type": "pie_chart",
  "path": "grafico_pizza.png",
  "column": "categoria",
  "values": "valor",
  "autopct": "%1.1f%%",
  "top_n": 10,
  "explode_max": true,
  "title": "Distribuição",
  "figsize": [10, 10]
}
```

### 4. Line Chart (Gráfico de Linhas)

```json
{
  "type": "line_chart",
  "path": "grafico_linhas.png",
  "x": "tempo",
  "y": ["serie1", "serie2"],
  "marker": "o",
  "linestyle": "-",
  "title": "Evolução Temporal",
  "grid": true
}
```

### 5. Scatter Chart (Gráfico de Dispersão)

```json
{
  "type": "scatter_chart",
  "path": "grafico_dispersao.png",
  "x": "variavel_x",
  "y": "variavel_y",
  "size": "tamanho",
  "color": "categoria",
  "alpha": 0.6,
  "cmap": "viridis"
}
```

### 6. Simple Map (Mapa Simples)

```json
{
  "type": "simple_map",
  "path": "mapa_simples.png",
  "color": "blue",
  "edgecolor": "black",
  "alpha": 0.7,
  "markersize": 50,
  "axis_off": false
}
```

### 7. Choropleth Map (Mapa Coroplético)

```json
{
  "type": "choropleth_map",
  "path": "mapa_coropletico.png",
  "column": "densidade",
  "cmap": "YlOrRd",
  "legend": true,
  "scheme": "quantiles",
  "k": 5,
  "edgecolor": "black"
}
```

Esquemas de classificação: `quantiles`, `equal_interval`, `fisher_jenks`

### 8. Heat Map (Mapa de Calor)

```json
{
  "type": "heat_map",
  "path": "mapa_calor.png",
  "column": "intensidade",
  "markersize": 100,
  "alpha": 0.5,
  "cmap": "hot"
}
```

## 🎓 Exemplos Práticos

### Exemplo 1: Análise de Cidades Grandes

Filtrar cidades com mais de 1.5 milhão de habitantes, calcular densidade e PIB per capita, e gerar relatórios.

```bash
python3 geojson_processor.py examples/cidades_brasil.geojson \
  --config examples/config_avancado.json
```

**Resultado**: Planilha, gráfico de barras e mapa das maiores cidades.

### Exemplo 2: Agregação por Região

Agrupar cidades por região, somar população e PIB, e visualizar distribuição.

```bash
python3 geojson_processor.py examples/cidades_brasil.geojson \
  --config examples/config_agrupamento.json
```

**Resultado**: Planilha agregada, gráfico de barras de população e gráfico de pizza de PIB.

### Exemplo 3: Uso Rápido

Gerar planilha e gráfico sem configuração JSON.

```bash
python3 geojson_processor.py examples/cidades_brasil.geojson \
  --spreadsheet dados.xlsx \
  --bar-chart grafico.png --bar-column regiao
```

## 🏗️ Arquitetura

### Padrões de Design Implementados

1. **Abstract Base Class (ABC)**: Classes base `BaseProcessor` e `OutputGenerator`
2. **Factory Method**: `OutputFactory` para criar geradores
3. **Chain of Responsibility**: `ProcessorPipeline` para encadear operações
4. **Facade**: `GeoJSONProcessor` simplifica interface complexa

### Hierarquia de Classes

```
BaseProcessor (ABC)
├── FilterProcessor
├── GroupByProcessor
├── CalculateProcessor
├── SortProcessor
└── LimitProcessor

OutputGenerator (ABC)
├── SpreadsheetGenerator
├── ChartGenerator (Base)
│   ├── BarChartGenerator
│   ├── PieChartGenerator
│   ├── LineChartGenerator
│   └── ScatterChartGenerator
└── MapGenerator (Base)
    ├── SimpleMapGenerator
    ├── ChoroplethMapGenerator
    └── HeatMapGenerator
```

### Uso de Recursos Nativos

- **Geopandas**: `read_file()`, `plot()`, `groupby()`, `eval()`
- **Pandas**: `DataFrame.eval()`, agregações, filtros booleanos
- **Matplotlib**: `pyplot`, `subplots()`, `savefig()`
- **Seaborn**: Estilos de visualização

## 🔧 Extensibilidade

### Adicionar Novo Processador

```python
from processors import BaseProcessor

class MeuProcessador(BaseProcessor):
    def process(self, gdf):
        # Sua lógica aqui
        return gdf_processado
```

Registre em `ProcessorPipeline.PROCESSOR_TYPES`:

```python
PROCESSOR_TYPES = {
    'meu_tipo': MeuProcessador,
    # ...
}
```

### Adicionar Novo Gerador

```python
from generators import OutputGenerator

class MeuGerador(OutputGenerator):
    def generate(self, gdf, output_path):
        # Sua lógica aqui
        return output_path
```

Registre em `OutputFactory.GENERATOR_TYPES`:

```python
GENERATOR_TYPES = {
    'meu_output': MeuGerador,
    # ...
}
```

## 📄 Licença

Sistema desenvolvido para processamento avançado de dados geoespaciais.

## 🤝 Contribuições

Para adicionar novas funcionalidades:

1. Crie uma nova classe herdando de `BaseProcessor` ou `OutputGenerator`
2. Implemente os métodos abstratos
3. Registre no factory/pipeline apropriado
4. Adicione testes e documentação

## 📞 Suporte

Para dúvidas sobre uso ou extensão do sistema, consulte:

- `architecture.md`: Documentação detalhada da arquitetura
- `examples/`: Exemplos práticos de uso
- Código fonte: Comentários inline explicam a lógica
