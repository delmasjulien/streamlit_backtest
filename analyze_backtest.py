# Script d'analyse des backtests TradingView

import pandas as pd
import numpy as np
from data_extractor import TradingViewDataExtractor
import os
from datetime import datetime

def analyze_tradingview_backtest(file_path):
    '''Analyse complete d'un backtest TradingView'''
    print(f'Analyse du fichier: {file_path}')
    
    # Créer le dossier de rapports
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # Extraire les données
    extractor = TradingViewDataExtractor(file_path)
    sheets = extractor.load_data()
    
    if not sheets:
        print('Erreur: Impossible de charger les donnees')
        return
    
    # Analyser la liste des trades
    trades_df = extractor.parse_trades_list()
    
    if trades_df.empty:
        print('Erreur: Aucune donnee de trade trouvee')
        return
    
    # Identifier les colonnes importantes
    columns = trades_df.columns.tolist()
    print(f'Colonnes trouvees: {columns}')
    
    # Afficher quelques statistiques de base
    print(f'\\nNombre total de trades: {len(trades_df)}')
    
    # Sauvegarder un rapport basique
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    report_file = f'reports/{base_name}_analysis.csv'
    trades_df.to_csv(report_file, index=False)
    print(f'Rapport sauvegarde dans: {report_file}')

if __name__ == '__main__':
    # Trouver le fichier XLSX
    xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if not xlsx_files:
        print('Aucun fichier XLSX trouve dans le dossier')
        exit(1)
    
    # Analyser le premier fichier trouve
    file_to_analyze = xlsx_files[0]
    analyze_tradingview_backtest(file_to_analyze)
