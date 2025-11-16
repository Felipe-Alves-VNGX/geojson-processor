"""
Módulo de processadores de dados para transformação de GeoDataFrames.
Usa herança e polimorfismo para criar um sistema extensível e modular.
"""

from abc import ABC, abstractmethod
import geopandas as gpd
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Union
import operator


class BaseProcessor(ABC):
    """
    Classe base abstrata para todos os processadores de dados.
    Define a interface comum que todos os processadores devem implementar.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o processador com configuração.
        
        Args:
            config: Dicionário com parâmetros de configuração
        """
        self.config = config
    
    @abstractmethod
    def process(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Processa o GeoDataFrame e retorna uma versão transformada.
        
        Args:
            gdf: GeoDataFrame de entrada
            
        Returns:
            GeoDataFrame processado
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.config})"


class FilterProcessor(BaseProcessor):
    """
    Processador para filtragem de dados com suporte a múltiplos operadores.
    Usa recursos nativos do pandas para máxima eficiência.
    """
    
    # Mapeamento de operadores string para funções Python
    OPERATORS = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '<': operator.lt,
        '>=': operator.ge,
        '<=': operator.le,
        'in': lambda x, y: x.isin(y) if isinstance(y, list) else x == y,
        'contains': lambda x, y: x.str.contains(y, na=False),
        'startswith': lambda x, y: x.str.startswith(y, na=False),
        'endswith': lambda x, y: x.str.endswith(y, na=False),
        'between': lambda x, y: x.between(y[0], y[1]) if isinstance(y, list) and len(y) == 2 else False,
        'isnull': lambda x, y: x.isnull() if y else x.notnull(),
    }
    
    def process(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Aplica filtros ao GeoDataFrame.
        
        Configuração esperada:
        {
            "column": "nome_da_coluna",
            "operator": "==", ">", "<", "in", "contains", etc.
            "value": valor_para_comparacao
        }
        
        Ou para múltiplos filtros:
        {
            "filters": [
                {"column": "col1", "operator": ">", "value": 10},
                {"column": "col2", "operator": "in", "value": ["A", "B"]}
            ],
            "logic": "and"  # ou "or"
        }
        """
        # Suporte a filtro único ou múltiplos filtros
        if 'filters' in self.config:
            return self._apply_multiple_filters(gdf)
        else:
            return self._apply_single_filter(gdf)
    
    def _apply_single_filter(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Aplica um único filtro."""
        column = self.config['column']
        op = self.config['operator']
        value = self.config['value']
        
        if column not in gdf.columns:
            raise ValueError(f"Coluna '{column}' não encontrada no GeoDataFrame")
        
        if op not in self.OPERATORS:
            raise ValueError(f"Operador '{op}' não suportado. Use: {list(self.OPERATORS.keys())}")
        
        # Aplica o operador
        mask = self.OPERATORS[op](gdf[column], value)
        return gdf[mask].copy()
    
    def _apply_multiple_filters(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Aplica múltiplos filtros com lógica AND ou OR."""
        filters = self.config['filters']
        logic = self.config.get('logic', 'and').lower()
        
        masks = []
        for filter_config in filters:
            temp_processor = FilterProcessor(filter_config)
            # Cria máscara booleana para cada filtro
            column = filter_config['column']
            op = filter_config['operator']
            value = filter_config['value']
            
            if column not in gdf.columns:
                raise ValueError(f"Coluna '{column}' não encontrada no GeoDataFrame")
            
            mask = self.OPERATORS[op](gdf[column], value)
            masks.append(mask)
        
        # Combina máscaras com AND ou OR
        if logic == 'and':
            combined_mask = pd.Series([True] * len(gdf), index=gdf.index)
            for mask in masks:
                combined_mask &= mask
        else:  # or
            combined_mask = pd.Series([False] * len(gdf), index=gdf.index)
            for mask in masks:
                combined_mask |= mask
        
        return gdf[combined_mask].copy()


class GroupByProcessor(BaseProcessor):
    """
    Processador para agrupamento de dados com agregações.
    Usa groupby nativo do pandas/geopandas para máxima eficiência.
    """
    
    # Funções de agregação disponíveis
    AGGREGATIONS = {
        'sum': 'sum',
        'mean': 'mean',
        'median': 'median',
        'count': 'count',
        'min': 'min',
        'max': 'max',
        'std': 'std',
        'var': 'var',
        'first': 'first',
        'last': 'last',
        'nunique': 'nunique',
    }
    
    def process(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Agrupa dados e aplica funções de agregação.
        
        Configuração esperada:
        {
            "columns": ["col1", "col2"],  # Colunas para agrupar
            "aggregations": {
                "col_numerica": "sum",
                "outra_col": "mean"
            },
            "keep_geometry": False  # Se True, mantém a primeira geometria de cada grupo
        }
        """
        group_columns = self.config['columns']
        aggregations = self.config['aggregations']
        keep_geometry = self.config.get('keep_geometry', False)
        
        # Valida colunas
        for col in group_columns:
            if col not in gdf.columns:
                raise ValueError(f"Coluna de agrupamento '{col}' não encontrada")
        
        for col in aggregations.keys():
            if col not in gdf.columns:
                raise ValueError(f"Coluna de agregação '{col}' não encontrada")
        
        # Valida funções de agregação
        for agg_func in aggregations.values():
            if agg_func not in self.AGGREGATIONS:
                raise ValueError(f"Função de agregação '{agg_func}' não suportada. Use: {list(self.AGGREGATIONS.keys())}")
        
        # Realiza o agrupamento
        if keep_geometry:
            # Mantém a geometria do primeiro elemento de cada grupo
            result = gdf.groupby(group_columns, as_index=False).agg({
                **aggregations,
                'geometry': 'first'
            })
            # Converte de volta para GeoDataFrame
            result = gpd.GeoDataFrame(result, geometry='geometry', crs=gdf.crs)
        else:
            # Sem geometria, retorna DataFrame comum
            result = gdf.drop(columns='geometry').groupby(group_columns, as_index=False).agg(aggregations)
            # Cria GeoDataFrame vazio (sem geometrias)
            result = gpd.GeoDataFrame(result)
        
        return result


class CalculateProcessor(BaseProcessor):
    """
    Processador para criar novas colunas calculadas.
    Usa eval() do pandas para expressões seguras e eficientes.
    """
    
    def process(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Cria novas colunas baseadas em expressões.
        
        Configuração esperada:
        {
            "new_column": "nome_nova_coluna",
            "expression": "coluna1 + coluna2 * 2"
        }
        
        Ou para múltiplos cálculos:
        {
            "calculations": [
                {"new_column": "densidade", "expression": "populacao / area"},
                {"new_column": "log_pop", "expression": "log(populacao)"}
            ]
        }
        """
        result = gdf.copy()
        
        # Suporte a cálculo único ou múltiplos
        if 'calculations' in self.config:
            calculations = self.config['calculations']
        else:
            calculations = [{"new_column": self.config['new_column'], 
                           "expression": self.config['expression']}]
        
        for calc in calculations:
            new_column = calc['new_column']
            expression = calc['expression']
            
            try:
                # Usa eval do pandas para expressões seguras
                # Disponibiliza funções matemáticas comuns
                result[new_column] = result.eval(expression)
            except Exception as e:
                # Se eval falhar, tenta com numpy
                try:
                    # Cria namespace com colunas e funções numpy
                    namespace = {col: result[col] for col in result.columns if col != 'geometry'}
                    namespace.update({
                        'log': np.log,
                        'log10': np.log10,
                        'sqrt': np.sqrt,
                        'abs': np.abs,
                        'exp': np.exp,
                        'sin': np.sin,
                        'cos': np.cos,
                        'tan': np.tan,
                    })
                    result[new_column] = eval(expression, {"__builtins__": {}}, namespace)
                except Exception as e2:
                    raise ValueError(f"Erro ao calcular '{new_column}' com expressão '{expression}': {e2}")
        
        return result


class SortProcessor(BaseProcessor):
    """
    Processador para ordenação de dados.
    Usa sort_values nativo do pandas.
    """
    
    def process(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Ordena o GeoDataFrame.
        
        Configuração esperada:
        {
            "columns": ["col1", "col2"],
            "ascending": [True, False]  # ou apenas True/False
        }
        """
        columns = self.config['columns']
        ascending = self.config.get('ascending', True)
        
        # Valida colunas
        for col in columns if isinstance(columns, list) else [columns]:
            if col not in gdf.columns:
                raise ValueError(f"Coluna '{col}' não encontrada")
        
        return gdf.sort_values(by=columns, ascending=ascending).copy()


class LimitProcessor(BaseProcessor):
    """
    Processador para limitar número de registros.
    """
    
    def process(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Limita o número de registros.
        
        Configuração esperada:
        {
            "n": 100,  # Número de registros
            "method": "head"  # ou "tail" ou "sample"
        }
        """
        n = self.config['n']
        method = self.config.get('method', 'head')
        
        if method == 'head':
            return gdf.head(n).copy()
        elif method == 'tail':
            return gdf.tail(n).copy()
        elif method == 'sample':
            return gdf.sample(n=min(n, len(gdf)), random_state=self.config.get('random_state', None)).copy()
        else:
            raise ValueError(f"Método '{method}' não suportado. Use: head, tail, sample")


class ProcessorPipeline:
    """
    Pipeline para executar múltiplos processadores em sequência.
    Implementa o padrão Chain of Responsibility.
    """
    
    # Mapeamento de tipos para classes
    PROCESSOR_TYPES = {
        'filter': FilterProcessor,
        'groupby': GroupByProcessor,
        'calculate': CalculateProcessor,
        'sort': SortProcessor,
        'limit': LimitProcessor,
    }
    
    def __init__(self, operations: List[Dict[str, Any]]):
        """
        Inicializa o pipeline com uma lista de operações.
        
        Args:
            operations: Lista de dicionários de configuração
        """
        self.processors = []
        for op_config in operations:
            op_type = op_config.get('type')
            if op_type not in self.PROCESSOR_TYPES:
                raise ValueError(f"Tipo de operação '{op_type}' não suportado. Use: {list(self.PROCESSOR_TYPES.keys())}")
            
            processor_class = self.PROCESSOR_TYPES[op_type]
            processor = processor_class(op_config)
            self.processors.append(processor)
    
    def execute(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Executa todos os processadores em sequência.
        
        Args:
            gdf: GeoDataFrame de entrada
            
        Returns:
            GeoDataFrame processado
        """
        result = gdf.copy()
        for processor in self.processors:
            print(f"Executando: {processor}")
            result = processor.process(result)
            print(f"  → Registros: {len(result)}")
        return result
    
    def __repr__(self):
        return f"ProcessorPipeline({len(self.processors)} operações)"
