import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def gerar_grafico_comparativo(resultados):
    """
    Gera gráfico comparativo do custo ao longo das iterações para todas as metaheurísticas
    """
    try:
        # Criar pasta se não existir
        os.makedirs('resultados', exist_ok=True)
        
        plt.figure(figsize=(12, 8))
        
        # Cores para cada método
        cores = {
            'Busca Tabu': 'blue',
            'ILS': 'red', 
            'Simulated Annealing': 'green'
        }
        
        # Marcadores para cada método
        marcadores = {
            'Busca Tabu': 'o',
            'ILS': 's', 
            'Simulated Annealing': '^'
        }
        
        # Plot para cada método
        for metodo, resultado in resultados.items():
            df = resultado['df']
            cor = cores.get(metodo, 'black')
            marcador = marcadores.get(metodo, 'o')
            
            # Plot linha principal
            plt.plot(df['Iteracao'], df['Custo_Total'], 
                    label=metodo, color=cor, linewidth=2, marker=marcador, 
                    markersize=4, markevery=max(1, len(df)//10))
        
        plt.xlabel('Iteração', fontsize=12)
        plt.ylabel('Custo Total', fontsize=12)
        plt.title('Comparação das Metaheurísticas - Evolução do Custo', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Caminho completo para salvar
        caminho_arquivo = os.path.join('resultados', 'comparativo_metaheuristicas.png')
        plt.savefig(caminho_arquivo, dpi=300, bbox_inches='tight')
        print(f"Gráfico salvo em: {caminho_arquivo}")
        plt.show()
        
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")