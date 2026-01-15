# Analyse avancee des backtests TradingView

import pandas as pd
import numpy as np
from datetime import datetime
import os

def load_trades_data(file_path):
    '''Charge les donnees de trades'''
    try:
        trades_df = pd.read_excel(file_path, sheet_name='List of trades')
        return trades_df
    except Exception as e:
        print(f'Erreur lors du chargement: {e}')
        return None

def prepare_trade_data(trades_df):
    '''Prepare les donnees pour l'analyse'''
    # Identifier les colonnes importantes
    print('Colonnes disponibles:', trades_df.columns.tolist())
    
    # Chercher les colonnes de date
    time_cols = [col for col in trades_df.columns if 'Time' in col or 'time' in col]
    print(f'Colonnes de temps trouvees: {time_cols}')
    
    # Chercher les colonnes de profit
    profit_cols = [col for col in trades_df.columns if 'Profit' in col or 'P&L' in col or 'PnL' in col]
    print(f'Colonnes de profit trouvees: {profit_cols}')
    
    return trades_df

def main():
    # Trouver le fichier XLSX
    xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
    
    if not xlsx_files:
        print('Aucun fichier XLSX trouve')
        return
    
    file_path = xlsx_files[0]
    print(f'Analyse du fichier: {file_path}')
    
    # Charger les donnees
    trades_df = load_trades_data(file_path)
    if trades_df is None:
        return
    
    # Preparer les donnees
    prepared_df = prepare_trade_data(trades_df)
    
    # Afficher un apercu
    print('\\nApercu des donnees:')
    print(prepared_df.head())

if __name__ == '__main__':
    main()
