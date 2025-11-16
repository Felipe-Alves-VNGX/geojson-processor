# Guia Rápido - GeoJSON Processor

## Instalação Rápida

```bash
# Instalar dependências
sudo pip3 install geopandas matplotlib seaborn openpyxl

# Clonar/baixar o projeto
cd geojson_processor
```

## 5 Minutos para Começar

### 1. Uso Mais Simples: Apenas Planilha

```bash
python3 geojson_processor.py meu_arquivo.geojson --spreadsheet saida.xlsx
```

### 2. Planilha + Gráfico de Barras

```bash
python3 geojson_processor.py meu_arquivo.geojson \
  --spreadsheet dados.xlsx \
  --bar-chart grafico.png --bar-column categoria
```

### 3. Gerar Mapa

```bash
python3 geojson_processor.py meu_arquivo.geojson \
  --simple-map mapa.png
```

### 4. Tudo de Uma Vez

```bash
python3 geojson_processor.py meu_arquivo.geojson \
  --spreadsheet dados.xlsx \
  --bar-chart grafico.png --bar-column tipo \
  --simple-map mapa.png
```

## Uso Avançado com Configuração JSON

### Passo 1: Criar arquivo de configuração

Crie `config.json`:

```json
{
  "operations": [
    {
      "type": "filter",
      "column": "populacao",
      "operator": ">",
      "value": 100000
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
      "type": "bar_chart",
      "path": "grafico.png",
      "x": "nome",
      "y": "populacao",
      "title": "População por Cidade"
    }
  ]
}
```

### Passo 2: Executar

```bash
python3 geojson_processor.py dados.geojson --config config.json
```

## Exemplos Prontos

### Testar com Dados de Exemplo

```bash
# Exemplo 1: Análise de cidades grandes
python3 geojson_processor.py examples/cidades_brasil.geojson \
  --config examples/config_avancado.json

# Exemplo 2: Agregação por região
python3 geojson_processor.py examples/cidades_brasil.geojson \
  --config examples/config_agrupamento.json
```

### Ver Resultados

```bash
ls -lh examples/output/
```

## Operações Mais Comuns

### Filtrar Dados

```json
{
  "type": "filter",
  "column": "tipo",
  "operator": "==",
  "value": "Capital"
}
```

### Agrupar e Somar

```json
{
  "type": "groupby",
  "columns": ["regiao"],
  "aggregations": {
    "populacao": "sum",
    "area": "mean"
  }
}
```

### Calcular Nova Coluna

```json
{
  "type": "calculate",
  "new_column": "densidade",
  "expression": "populacao / area"
}
```

### Ordenar

```json
{
  "type": "sort",
  "columns": ["populacao"],
  "ascending": false
}
```

### Top 10

```json
{
  "type": "limit",
  "n": 10,
  "method": "head"
}
```

## Outputs Mais Comuns

### Planilha Excel

```json
{
  "type": "spreadsheet",
  "path": "dados.xlsx",
  "sheet_name": "Resultados"
}
```

### Gráfico de Barras

```json
{
  "type": "bar_chart",
  "path": "barras.png",
  "x": "categoria",
  "y": "valor",
  "title": "Meu Gráfico"
}
```

### Gráfico de Pizza

```json
{
  "type": "pie_chart",
  "path": "pizza.png",
  "column": "tipo",
  "title": "Distribuição"
}
```

### Mapa Coroplético

```json
{
  "type": "choropleth_map",
  "path": "mapa.png",
  "column": "densidade",
  "cmap": "YlOrRd"
}
```

## Dicas Rápidas

1. **Sempre filtre antes de agrupar** para melhor performance
2. **Use cálculos para criar métricas** como densidade, per capita, etc.
3. **Ordene e limite** para focar nos dados mais relevantes
4. **Combine múltiplos outputs** para análise completa
5. **Use configuração JSON** para operações complexas e reprodutíveis

## Ajuda

```bash
# Ver todas as opções
python3 geojson_processor.py --help

# Ver exemplos
ls examples/
cat examples/config_avancado.json
```

## Próximos Passos

- Leia `README.md` para documentação completa
- Veja `architecture.md` para entender a estrutura
- Explore `examples/` para mais casos de uso
- Customize os exemplos para seus dados
