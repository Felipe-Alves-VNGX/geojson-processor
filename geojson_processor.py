#!/usr/bin/env python3
"""
GeoJSON Processor - Sistema sofisticado para processamento de arquivos GeoJSON.

Usa programação orientada a objetos com herança para criar um sistema modular
e extensível capaz de filtrar, agrupar, calcular e gerar planilhas, gráficos e mapas.

Autor: Sistema de Processamento GeoJSON
Versão: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
import geopandas as gpd

# Importa módulos do sistema
from processors import ProcessorPipeline
from generators import OutputFactory


class GeoJSONProcessor:
    """
    Classe principal que orquestra todo o processamento.
    Implementa o padrão Facade para simplificar a interface.
    """
    
    def __init__(self, geojson_path: str):
        """
        Inicializa o processador com um arquivo GeoJSON.
        
        Args:
            geojson_path: Caminho para o arquivo GeoJSON
        """
        self.geojson_path = geojson_path
        self.gdf = None
        self.processed_gdf = None
    
    def load(self):
        """Carrega o arquivo GeoJSON."""
        try:
            print(f"Carregando arquivo: {self.geojson_path}")
            self.gdf = gpd.read_file(self.geojson_path)
            print(f"✔ Arquivo carregado com sucesso!")
            print(f"  → Registros: {len(self.gdf)}")
            print(f"  → Colunas: {list(self.gdf.columns)}")
            print(f"  → CRS: {self.gdf.crs}")
            return self
        except Exception as e:
            print(f"✗ Erro ao carregar arquivo: {e}", file=sys.stderr)
            sys.exit(1)
    
    def process(self, operations: list):
        """
        Aplica operações de processamento ao GeoDataFrame.
        
        Args:
            operations: Lista de operações a serem aplicadas
        """
        if not operations:
            print("Nenhuma operação de processamento especificada.")
            self.processed_gdf = self.gdf.copy()
            return self
        
        try:
            print(f"\nAplicando {len(operations)} operação(ões) de processamento...")
            pipeline = ProcessorPipeline(operations)
            self.processed_gdf = pipeline.execute(self.gdf)
            print(f"✔ Processamento concluído!")
            print(f"  → Registros finais: {len(self.processed_gdf)}")
            return self
        except Exception as e:
            print(f"✗ Erro durante processamento: {e}", file=sys.stderr)
            sys.exit(1)
    
    def generate_outputs(self, outputs: list):
        """
        Gera outputs (planilhas, gráficos, mapas).
        
        Args:
            outputs: Lista de configurações de output
        """
        if not outputs:
            print("Nenhum output especificado.")
            return self
        
        print(f"\nGerando {len(outputs)} output(s)...")
        
        for i, output_config in enumerate(outputs, 1):
            try:
                output_type = output_config['type']
                output_path = output_config['path']
                
                print(f"\n[{i}/{len(outputs)}] Gerando {output_type}...")
                
                # Cria gerador usando Factory
                generator = OutputFactory.create_generator(output_type, output_config)
                
                # Gera output
                generator.generate(self.processed_gdf, output_path)
                
            except Exception as e:
                print(f"✗ Erro ao gerar output {i}: {e}", file=sys.stderr)
                continue
        
        print("\n✔ Todos os outputs foram processados!")
        return self


def load_config_file(config_path: str) -> dict:
    """
    Carrega arquivo de configuração JSON.
    
    Args:
        config_path: Caminho para o arquivo JSON
        
    Returns:
        Dicionário com configuração
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"✗ Erro ao carregar arquivo de configuração: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Função principal com interface de linha de comando."""
    
    parser = argparse.ArgumentParser(
        description="""
GeoJSON Processor - Sistema sofisticado para processamento de arquivos GeoJSON.

Capacidades:
  • Filtragem dinâmica com múltiplos operadores
  • Agrupamento com funções de agregação
  • Cálculo de novas colunas com expressões
  • Geração de planilhas Excel formatadas
  • Criação de gráficos (barras, pizza, linhas, dispersão)
  • Geração de mapas (simples, coropléticos, calor)

Modos de uso:
  1. Via arquivo de configuração JSON (recomendado)
  2. Via argumentos de linha de comando (simples)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Usando arquivo de configuração
  python geojson_processor.py dados.geojson --config config.json

  # Modo simples: apenas planilha
  python geojson_processor.py dados.geojson --spreadsheet relatorio.xlsx

  # Modo simples: planilha + gráfico de barras
  python geojson_processor.py dados.geojson \\
    --spreadsheet relatorio.xlsx \\
    --bar-chart grafico.png --bar-column tipo

  # Modo simples: mapa coroplético
  python geojson_processor.py dados.geojson \\
    --choropleth-map mapa.png --choropleth-column densidade

Para operações avançadas, use arquivo de configuração JSON.
Veja exemplos em: examples/
        """
    )
    
    # Argumentos obrigatórios
    parser.add_argument('geojson', 
                       help='Caminho para o arquivo GeoJSON de entrada')
    
    # Modo de configuração
    parser.add_argument('--config', '-c',
                       help='Caminho para arquivo de configuração JSON')
    
    # Outputs simples (modo simplificado)
    parser.add_argument('--spreadsheet',
                       help='Gera planilha Excel (caminho do arquivo)')
    
    parser.add_argument('--bar-chart',
                       help='Gera gráfico de barras (caminho do arquivo)')
    parser.add_argument('--bar-column',
                       help='Coluna para gráfico de barras')
    parser.add_argument('--bar-value',
                       help='Coluna de valores para gráfico de barras (opcional)')
    
    parser.add_argument('--pie-chart',
                       help='Gera gráfico de pizza (caminho do arquivo)')
    parser.add_argument('--pie-column',
                       help='Coluna para gráfico de pizza')
    
    parser.add_argument('--simple-map',
                       help='Gera mapa simples (caminho do arquivo)')
    
    parser.add_argument('--choropleth-map',
                       help='Gera mapa coroplético (caminho do arquivo)')
    parser.add_argument('--choropleth-column',
                       help='Coluna para mapa coroplético')
    
    # Opções gerais
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verboso (mais informações)')
    
    args = parser.parse_args()
    
    # Determina modo de operação
    if args.config:
        # Modo avançado: usa arquivo de configuração
        config = load_config_file(args.config)
        operations = config.get('operations', [])
        outputs = config.get('outputs', [])
    else:
        # Modo simples: usa argumentos de linha de comando
        operations = []
        outputs = []
        
        # Planilha
        if args.spreadsheet:
            outputs.append({
                'type': 'spreadsheet',
                'path': args.spreadsheet
            })
        
        # Gráfico de barras
        if args.bar_chart:
            if not args.bar_column:
                print("✗ Erro: --bar-column é obrigatório para gráfico de barras", 
                      file=sys.stderr)
                sys.exit(1)
            
            bar_config = {
                'type': 'bar_chart',
                'path': args.bar_chart,
                'x': args.bar_column
            }
            if args.bar_value:
                bar_config['y'] = args.bar_value
            
            outputs.append(bar_config)
        
        # Gráfico de pizza
        if args.pie_chart:
            if not args.pie_column:
                print("✗ Erro: --pie-column é obrigatório para gráfico de pizza", 
                      file=sys.stderr)
                sys.exit(1)
            
            outputs.append({
                'type': 'pie_chart',
                'path': args.pie_chart,
                'column': args.pie_column
            })
        
        # Mapa simples
        if args.simple_map:
            outputs.append({
                'type': 'simple_map',
                'path': args.simple_map
            })
        
        # Mapa coroplético
        if args.choropleth_map:
            if not args.choropleth_column:
                print("✗ Erro: --choropleth-column é obrigatório para mapa coroplético", 
                      file=sys.stderr)
                sys.exit(1)
            
            outputs.append({
                'type': 'choropleth_map',
                'path': args.choropleth_map,
                'column': args.choropleth_column
            })
        
        if not outputs:
            print("✗ Erro: Nenhum output especificado. Use --config ou argumentos de output.", 
                  file=sys.stderr)
            parser.print_help()
            sys.exit(1)
    
    # Executa processamento
    print("=" * 70)
    print("GeoJSON Processor v1.0.0")
    print("=" * 70)
    
    processor = GeoJSONProcessor(args.geojson)
    processor.load().process(operations).generate_outputs(outputs)
    
    print("\n" + "=" * 70)
    print("✔ Processamento concluído com sucesso!")
    print("=" * 70)


if __name__ == '__main__':
    main()
