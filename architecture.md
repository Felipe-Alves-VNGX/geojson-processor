# Arquitetura do Sistema de Processamento GeoJSON

## Visão Geral

Sistema modular orientado a objetos para processar arquivos GeoJSON com capacidades avançadas de transformação e visualização.

## Hierarquia de Classes

```
BaseProcessor (ABC)
├── DataProcessor
│   ├── FilterProcessor
│   ├── GroupByProcessor
│   └── CalculateProcessor
│
OutputGenerator (ABC)
├── SpreadsheetGenerator
├── ChartGenerator
│   ├── BarChartGenerator
│   ├── PieChartGenerator
│   ├── LineChartGenerator
│   └── ScatterChartGenerator
└── MapGenerator
    ├── SimpleMapGenerator
    ├── ChoroplethMapGenerator
    └── HeatMapGenerator
```

## Componentes Principais

### 1. BaseProcessor (Classe Abstrata)
- Responsabilidade: Definir interface comum para processamento de dados
- Métodos: `process(gdf) -> GeoDataFrame`

### 2. DataProcessor (Subclasses)
- **FilterProcessor**: Filtragem dinâmica com operadores (==, !=, >, <, >=, <=, in, contains)
- **GroupByProcessor**: Agrupamento com funções de agregação (sum, mean, count, min, max, std)
- **CalculateProcessor**: Criação de colunas calculadas com expressões

### 3. OutputGenerator (Classe Abstrata)
- Responsabilidade: Definir interface para geração de outputs
- Métodos: `generate(gdf, output_path, **kwargs)`

### 4. SpreadsheetGenerator
- Gera planilhas Excel com formatação
- Suporta múltiplas abas
- Usa recursos nativos do pandas/openpyxl

### 5. ChartGenerator (Subclasses)
- Usa matplotlib e seaborn nativamente
- Suporta customização completa via kwargs
- Tipos: barras, pizza, linhas, dispersão

### 6. MapGenerator (Subclasses)
- Usa geopandas.plot() nativamente
- Suporta mapas coropléticos, de calor e simples
- Integração com contextily para basemaps

## Pipeline de Processamento

```
GeoJSON → Load → [Processors] → [Generators] → Outputs
                     ↓
              Filter → GroupBy → Calculate
                     ↓
              Planilha | Gráfico | Mapa
```

## Formato de Configuração (JSON)

```json
{
  "operations": [
    {
      "type": "filter",
      "column": "populacao",
      "operator": ">",
      "value": 10000
    },
    {
      "type": "groupby",
      "columns": ["estado"],
      "aggregations": {
        "populacao": "sum",
        "area": "mean"
      }
    },
    {
      "type": "calculate",
      "new_column": "densidade",
      "expression": "populacao / area"
    }
  ],
  "outputs": [
    {
      "type": "spreadsheet",
      "path": "resultado.xlsx"
    },
    {
      "type": "chart",
      "chart_type": "bar",
      "path": "grafico.png",
      "x": "estado",
      "y": "populacao"
    },
    {
      "type": "map",
      "map_type": "choropleth",
      "path": "mapa.png",
      "column": "densidade"
    }
  ]
}
```

## Vantagens da Arquitetura

1. **Extensibilidade**: Fácil adicionar novos processadores ou geradores
2. **Reutilização**: Herança permite compartilhar código comum
3. **Testabilidade**: Cada componente pode ser testado isoladamente
4. **Manutenibilidade**: Separação clara de responsabilidades
5. **Flexibilidade**: Pipeline configurável via JSON
