"""
Módulo de geradores de output para criar planilhas, gráficos e mapas.
Usa herança e aproveita recursos nativos do pandas, matplotlib e geopandas.
"""

from abc import ABC, abstractmethod
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from typing import Any, Dict, Optional
import warnings


class OutputGenerator(ABC):
    """
    Classe base abstrata para todos os geradores de output.
    Define a interface comum que todos os geradores devem implementar.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerador com configuração.
        
        Args:
            config: Dicionário com parâmetros de configuração
        """
        self.config = config
    
    @abstractmethod
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera o output a partir do GeoDataFrame.
        
        Args:
            gdf: GeoDataFrame de entrada
            output_path: Caminho para salvar o output
            
        Returns:
            Caminho do arquivo gerado
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.config})"


class SpreadsheetGenerator(OutputGenerator):
    """
    Gerador de planilhas Excel com formatação avançada.
    Usa pandas e openpyxl nativamente.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera planilha Excel.
        
        Configuração esperada:
        {
            "include_geometry": False,  # Se True, inclui coluna WKT da geometria
            "sheet_name": "Dados",
            "freeze_panes": True,  # Congela primeira linha
            "auto_filter": True,  # Adiciona filtros automáticos
            "columns": ["col1", "col2"]  # Colunas específicas (opcional)
        }
        """
        include_geometry = self.config.get('include_geometry', False)
        sheet_name = self.config.get('sheet_name', 'Dados')
        freeze_panes = self.config.get('freeze_panes', True)
        auto_filter = self.config.get('auto_filter', True)
        columns = self.config.get('columns', None)
        
        # Prepara DataFrame
        if include_geometry and 'geometry' in gdf.columns:
            df = gdf.copy()
            # Converte geometria para WKT (Well-Known Text)
            df['geometry_wkt'] = df['geometry'].apply(lambda x: x.wkt if x is not None else None)
            df = df.drop(columns=['geometry'])
        else:
            df = gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf.copy()
        
        # Seleciona colunas específicas se fornecidas
        if columns:
            df = df[columns]
        
        # Salva para Excel
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Aplica formatação
            worksheet = writer.sheets[sheet_name]
            
            if freeze_panes:
                # Congela primeira linha (cabeçalho)
                worksheet.freeze_panes = 'A2'
            
            if auto_filter:
                # Adiciona filtros automáticos
                worksheet.auto_filter.ref = worksheet.dimensions
            
            # Ajusta largura das colunas
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✔ Planilha gerada: {output_path}")
        return output_path


class ChartGenerator(OutputGenerator):
    """
    Classe base para geradores de gráficos.
    Usa matplotlib e seaborn nativamente.
    """
    
    def _setup_figure(self):
        """Configura figura com parâmetros comuns."""
        figsize = self.config.get('figsize', (10, 6))
        dpi = self.config.get('dpi', 100)
        style = self.config.get('style', 'seaborn-v0_8-darkgrid')
        
        # Tenta aplicar estilo
        try:
            plt.style.use(style)
        except:
            warnings.warn(f"Estilo '{style}' não disponível, usando padrão")
        
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        return fig, ax
    
    def _apply_labels(self, ax):
        """Aplica títulos e rótulos."""
        title = self.config.get('title', '')
        xlabel = self.config.get('xlabel', '')
        ylabel = self.config.get('ylabel', '')
        
        if title:
            ax.set_title(title, fontsize=self.config.get('title_fontsize', 14), 
                        fontweight='bold')
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=self.config.get('label_fontsize', 11))
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=self.config.get('label_fontsize', 11))
    
    def _save_figure(self, fig, output_path):
        """Salva a figura com configurações."""
        bbox_inches = self.config.get('bbox_inches', 'tight')
        transparent = self.config.get('transparent', False)
        
        plt.tight_layout()
        fig.savefig(output_path, bbox_inches=bbox_inches, transparent=transparent)
        plt.close(fig)


class BarChartGenerator(ChartGenerator):
    """
    Gerador de gráficos de barras.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera gráfico de barras.
        
        Configuração esperada:
        {
            "x": "coluna_x",
            "y": "coluna_y",  # Opcional, se não fornecido usa contagem
            "orientation": "vertical",  # ou "horizontal"
            "color": "skyblue",
            "sort": True,  # Ordena por valor
            "top_n": 10  # Mostra apenas top N
        }
        """
        x_col = self.config['x']
        y_col = self.config.get('y', None)
        orientation = self.config.get('orientation', 'vertical')
        color = self.config.get('color', 'skyblue')
        sort_values = self.config.get('sort', False)
        top_n = self.config.get('top_n', None)
        
        # Prepara dados
        df = gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf.copy()
        
        if y_col:
            # Usa valores de y
            data = df.groupby(x_col)[y_col].sum()
        else:
            # Usa contagem
            data = df[x_col].value_counts()
        
        if sort_values:
            data = data.sort_values(ascending=False)
        
        if top_n:
            data = data.head(top_n)
        
        # Cria gráfico
        fig, ax = self._setup_figure()
        
        if orientation == 'horizontal':
            data.plot(kind='barh', ax=ax, color=color)
        else:
            data.plot(kind='bar', ax=ax, color=color)
            plt.xticks(rotation=self.config.get('rotation', 45), ha='right')
        
        self._apply_labels(ax)
        
        # Grid
        if self.config.get('grid', True):
            ax.grid(axis='y' if orientation == 'vertical' else 'x', alpha=0.3)
        
        self._save_figure(fig, output_path)
        print(f"✔ Gráfico de barras gerado: {output_path}")
        return output_path


class PieChartGenerator(ChartGenerator):
    """
    Gerador de gráficos de pizza.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera gráfico de pizza.
        
        Configuração esperada:
        {
            "column": "coluna_categoria",
            "values": "coluna_valores",  # Opcional
            "autopct": "%1.1f%%",
            "top_n": 10,
            "explode_max": True  # Destaca maior fatia
        }
        """
        column = self.config['column']
        values_col = self.config.get('values', None)
        autopct = self.config.get('autopct', '%1.1f%%')
        top_n = self.config.get('top_n', None)
        explode_max = self.config.get('explode_max', False)
        
        # Prepara dados
        df = gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf.copy()
        
        if values_col:
            data = df.groupby(column)[values_col].sum()
        else:
            data = df[column].value_counts()
        
        if top_n:
            data = data.head(top_n)
        
        # Cria gráfico
        fig, ax = self._setup_figure()
        
        # Explode (destaque)
        explode = None
        if explode_max:
            explode = [0.1 if i == 0 else 0 for i in range(len(data))]
        
        data.plot(kind='pie', ax=ax, autopct=autopct, explode=explode,
                 startangle=self.config.get('startangle', 90))
        
        ax.set_ylabel('')  # Remove label do eixo Y
        
        if self.config.get('title'):
            ax.set_title(self.config['title'], fontsize=14, fontweight='bold')
        
        self._save_figure(fig, output_path)
        print(f"✔ Gráfico de pizza gerado: {output_path}")
        return output_path


class LineChartGenerator(ChartGenerator):
    """
    Gerador de gráficos de linhas.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera gráfico de linhas.
        
        Configuração esperada:
        {
            "x": "coluna_x",
            "y": "coluna_y",  # ou lista de colunas
            "marker": "o",
            "linestyle": "-"
        }
        """
        x_col = self.config['x']
        y_cols = self.config['y']
        marker = self.config.get('marker', 'o')
        linestyle = self.config.get('linestyle', '-')
        
        # Prepara dados
        df = gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf.copy()
        
        # Cria gráfico
        fig, ax = self._setup_figure()
        
        if isinstance(y_cols, list):
            for y_col in y_cols:
                ax.plot(df[x_col], df[y_col], marker=marker, linestyle=linestyle, label=y_col)
            ax.legend()
        else:
            ax.plot(df[x_col], df[y_cols], marker=marker, linestyle=linestyle)
        
        self._apply_labels(ax)
        
        if self.config.get('grid', True):
            ax.grid(alpha=0.3)
        
        self._save_figure(fig, output_path)
        print(f"✔ Gráfico de linhas gerado: {output_path}")
        return output_path


class ScatterChartGenerator(ChartGenerator):
    """
    Gerador de gráficos de dispersão.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera gráfico de dispersão.
        
        Configuração esperada:
        {
            "x": "coluna_x",
            "y": "coluna_y",
            "size": "coluna_tamanho",  # Opcional
            "color": "coluna_cor",  # Opcional
            "alpha": 0.6
        }
        """
        x_col = self.config['x']
        y_col = self.config['y']
        size_col = self.config.get('size', None)
        color_col = self.config.get('color', None)
        alpha = self.config.get('alpha', 0.6)
        
        # Prepara dados
        df = gdf.drop(columns='geometry') if 'geometry' in gdf.columns else gdf.copy()
        
        # Cria gráfico
        fig, ax = self._setup_figure()
        
        # Determina tamanho dos pontos
        sizes = df[size_col] if size_col else 50
        
        # Determina cores
        if color_col:
            scatter = ax.scatter(df[x_col], df[y_col], s=sizes, c=df[color_col], 
                               alpha=alpha, cmap=self.config.get('cmap', 'viridis'))
            plt.colorbar(scatter, ax=ax, label=color_col)
        else:
            ax.scatter(df[x_col], df[y_col], s=sizes, alpha=alpha, 
                      color=self.config.get('point_color', 'blue'))
        
        self._apply_labels(ax)
        
        if self.config.get('grid', True):
            ax.grid(alpha=0.3)
        
        self._save_figure(fig, output_path)
        print(f"✔ Gráfico de dispersão gerado: {output_path}")
        return output_path


class MapGenerator(OutputGenerator):
    """
    Classe base para geradores de mapas.
    Usa geopandas.plot() nativamente.
    """
    
    def _setup_figure(self):
        """Configura figura para mapas."""
        figsize = self.config.get('figsize', (12, 12))
        dpi = self.config.get('dpi', 100)
        
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        return fig, ax
    
    def _apply_title(self, ax):
        """Aplica título ao mapa."""
        title = self.config.get('title', '')
        if title:
            ax.set_title(title, fontsize=self.config.get('title_fontsize', 14), 
                        fontweight='bold')


class SimpleMapGenerator(MapGenerator):
    """
    Gerador de mapas simples.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera mapa simples.
        
        Configuração esperada:
        {
            "color": "blue",
            "edgecolor": "black",
            "alpha": 0.7,
            "markersize": 50  # Para pontos
        }
        """
        color = self.config.get('color', 'blue')
        edgecolor = self.config.get('edgecolor', 'black')
        alpha = self.config.get('alpha', 0.7)
        markersize = self.config.get('markersize', 50)
        
        # Cria mapa
        fig, ax = self._setup_figure()
        
        gdf.plot(ax=ax, color=color, edgecolor=edgecolor, alpha=alpha, 
                markersize=markersize)
        
        self._apply_title(ax)
        
        # Remove eixos se solicitado
        if self.config.get('axis_off', False):
            ax.axis('off')
        else:
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
        
        plt.tight_layout()
        fig.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        print(f"✔ Mapa simples gerado: {output_path}")
        return output_path


class ChoroplethMapGenerator(MapGenerator):
    """
    Gerador de mapas coropléticos (com cores baseadas em valores).
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera mapa coroplético.
        
        Configuração esperada:
        {
            "column": "coluna_valores",
            "cmap": "YlOrRd",
            "legend": True,
            "scheme": "quantiles",  # ou "equal_interval", "fisher_jenks"
            "k": 5  # Número de classes
        }
        """
        column = self.config['column']
        cmap = self.config.get('cmap', 'YlOrRd')
        legend = self.config.get('legend', True)
        scheme = self.config.get('scheme', None)
        k = self.config.get('k', 5)
        edgecolor = self.config.get('edgecolor', 'black')
        linewidth = self.config.get('linewidth', 0.5)
        
        if column not in gdf.columns:
            raise ValueError(f"Coluna '{column}' não encontrada no GeoDataFrame")
        
        # Cria mapa
        fig, ax = self._setup_figure()
        
        # Plot coroplético
        if scheme:
            gdf.plot(column=column, ax=ax, cmap=cmap, legend=legend,
                    edgecolor=edgecolor, linewidth=linewidth,
                    scheme=scheme, k=k)
        else:
            gdf.plot(column=column, ax=ax, cmap=cmap, legend=legend,
                    edgecolor=edgecolor, linewidth=linewidth)
        
        self._apply_title(ax)
        
        if self.config.get('axis_off', False):
            ax.axis('off')
        
        plt.tight_layout()
        fig.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        print(f"✔ Mapa coroplético gerado: {output_path}")
        return output_path


class HeatMapGenerator(MapGenerator):
    """
    Gerador de mapas de calor para dados pontuais.
    """
    
    def generate(self, gdf: gpd.GeoDataFrame, output_path: str) -> str:
        """
        Gera mapa de calor.
        
        Configuração esperada:
        {
            "column": "coluna_intensidade",  # Opcional
            "markersize": 100,
            "alpha": 0.5,
            "cmap": "hot"
        }
        """
        column = self.config.get('column', None)
        markersize = self.config.get('markersize', 100)
        alpha = self.config.get('alpha', 0.5)
        cmap = self.config.get('cmap', 'hot')
        
        # Cria mapa
        fig, ax = self._setup_figure()
        
        if column and column in gdf.columns:
            # Usa valores da coluna para intensidade
            gdf.plot(ax=ax, column=column, cmap=cmap, markersize=markersize,
                    alpha=alpha, legend=True)
        else:
            # Mapa de calor simples baseado em densidade
            gdf.plot(ax=ax, color='red', markersize=markersize, alpha=alpha)
        
        self._apply_title(ax)
        
        if self.config.get('axis_off', False):
            ax.axis('off')
        
        plt.tight_layout()
        fig.savefig(output_path, bbox_inches='tight')
        plt.close(fig)
        
        print(f"✔ Mapa de calor gerado: {output_path}")
        return output_path


class OutputFactory:
    """
    Factory para criar geradores de output baseado em tipo.
    Implementa o padrão Factory Method.
    """
    
    GENERATOR_TYPES = {
        'spreadsheet': SpreadsheetGenerator,
        'bar_chart': BarChartGenerator,
        'pie_chart': PieChartGenerator,
        'line_chart': LineChartGenerator,
        'scatter_chart': ScatterChartGenerator,
        'simple_map': SimpleMapGenerator,
        'choropleth_map': ChoroplethMapGenerator,
        'heat_map': HeatMapGenerator,
    }
    
    @classmethod
    def create_generator(cls, output_type: str, config: Dict[str, Any]) -> OutputGenerator:
        """
        Cria um gerador baseado no tipo.
        
        Args:
            output_type: Tipo do gerador
            config: Configuração do gerador
            
        Returns:
            Instância do gerador apropriado
        """
        if output_type not in cls.GENERATOR_TYPES:
            raise ValueError(f"Tipo de output '{output_type}' não suportado. Use: {list(cls.GENERATOR_TYPES.keys())}")
        
        generator_class = cls.GENERATOR_TYPES[output_type]
        return generator_class(config)
