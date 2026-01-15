import pandas as pd
import os

# Liste tous les fichiers XLSX
xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

print('Fichiers XLSX trouves:')
for f in xlsx_files:
    print(f'  - {f}')

if xlsx_files:
    first_file = xlsx_files[0]
    print(f'\\nAnalyse du fichier: {first_file}')
    
    xl = pd.ExcelFile(first_file)
    print(f'Feuilles: {xl.sheet_names}')
    
    for sheet in xl.sheet_names:
        print(f'\\n=== Feuille: {sheet} ===')
        df = pd.read_excel(first_file, sheet_name=sheet)
        print(f'Dimensions: {df.shape}')
        print('Colonnes:', list(df.columns))
        print('Premieres lignes:')
        print(df.head(3))
        break  # Juste la premiere feuille pour l'instant
