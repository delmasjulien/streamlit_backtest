# Script de test pour verifier le fonctionnement avec vos fichiers

import os
import pandas as pd
from data_extractor import TradingViewDataExtractor

def test_files_in_directory():
    '''Teste tous les fichiers XLSX dans le repertoire courant'''
    
    # On est deja dans le bon dossier
    current_dir = '.'
    
    # Trouver tous les fichiers XLSX
    xlsx_files = [f for f in os.listdir(current_dir) if f.endswith('.xlsx')]
    
    if not xlsx_files:
        print('Aucun fichier XLSX trouve dans le dossier')
        return
    
    print(f'Trouve {len(xlsx_files)} fichiers XLSX:')
    for file in xlsx_files:
        print(f'  - {file}')
    
    # Tester le premier fichier
    if xlsx_files:
        first_file = xlsx_files[0]
        print(f'\\nTest du fichier: {first_file}')
        
        extractor = TradingViewDataExtractor(first_file)
        sheets = extractor.load_data()
        
        if sheets:
            print('Feuilles disponibles:')
            for sheet_name in sheets.keys():
                print(f'  - {sheet_name}')
                
            # Afficher un apercu de la premiere feuille
            first_sheet = list(sheets.keys())[0]
            print(f'\\nApercu de la feuille ''{first_sheet}'':')
            print(sheets[first_sheet].head())

if __name__ == '__main__':
    test_files_in_directory()
