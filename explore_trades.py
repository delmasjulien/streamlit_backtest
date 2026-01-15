# Exploration de la feuille 'List of trades'
import pandas as pd

# Lire le fichier XLSX
file_name = 'v3_STRATEGY_BOA_avec_fonction_test_+_param_fonctionnel_+moyenne_session_1__VANTAGE_GBPJPY_2026-01-14_c678a.xlsx'

# Explorer la feuille 'List of trades'
trades_df = pd.read_excel(file_name, sheet_name='List of trades')
print('=== Feuille List of trades ===')
print(f'Dimensions: {trades_df.shape}')
print('Colonnes:', list(trades_df.columns))
print('\\nPremières lignes:')
print(trades_df.head(10))

print('\\nInformations sur les colonnes:')
print(trades_df.info())

print('\\nStatistiques descriptives:')
print(trades_df.describe())
