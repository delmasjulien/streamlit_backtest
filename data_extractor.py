import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class TradingViewDataExtractor:
    '''Classe pour extraire les donnees des fichiers XLSX de TradingView'''
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data_sheets = {}
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        '''Charge toutes les feuilles du fichier XLSX'''
        try:
            excel_file = pd.ExcelFile(self.file_path)
            
            for sheet_name in excel_file.sheet_names:
                self.data_sheets[sheet_name] = pd.read_excel(
                    self.file_path,
                    sheet_name=sheet_name
                )
                
            print(f'Fichier charge avec {len(self.data_sheets)} feuilles')
            return self.data_sheets
            
        except Exception as e:
            print(f'Erreur lors du chargement du fichier: {e}')
            return {}
    
    def parse_trades_list(self) -> pd.DataFrame:
        '''Parse la feuille 'List of trades' pour extraire les informations pertinentes'''
        if 'List of trades' not in self.data_sheets:
            print('Feuille ''List of trades'' non trouvee')
            return pd.DataFrame()
        
        df = self.data_sheets['List of trades']
        
        # Afficher les premières lignes pour inspection
        print('Structure de la feuille List of trades:')
        print(df.head())
        
        return df
    
    def get_performance_summary(self) -> pd.DataFrame:
        '''Recupere le resume des performances'''
        if 'Performance' in self.data_sheets:
            return self.data_sheets['Performance']
        return pd.DataFrame()
