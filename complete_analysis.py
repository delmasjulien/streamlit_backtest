# Analyse complete des backtests TradingView
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Creation du dossier reports si necessaire
if not os.path.exists('reports'):
    os.makedirs('reports')

print('Chargement du fichier XLSX...')
xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

if not xlsx_files:
    print('Aucun fichier XLSX trouve dans le dossier')
    exit()

file_path = xlsx_files[0]
base_name = os.path.splitext(os.path.basename(file_path))[0]
print(f'Analyse du fichier: {file_path}')

# Lire les donnees
trades_df = pd.read_excel(file_path, sheet_name='List of trades')
print(f'Nombre total d_entrees: {len(trades_df)}')

# Filtrer uniquement les sorties (exits) pour l_analyse
exit_trades = trades_df[trades_df['Type'].str.contains('Exit')].copy()
exit_trades['Date and time'] = pd.to_datetime(exit_trades['Date and time'])
print(f'Nombre de trades analysables: {len(exit_trades)}')

# ANALYSE QUOTIDIENNE
print('Calcul des performances quotidiennes...')
exit_trades['Date'] = exit_trades['Date and time'].dt.date
daily_analysis = exit_trades.groupby('Date').agg({
    'Net P&L JPY': ['sum', 'mean', 'count'],
    'Net P&L %': ['sum', 'mean']
}).reset_index()
daily_analysis.columns = ['Date', 'Total_PnL_JPY', 'Avg_PnL_JPY', 'Trade_Count', 'Total_PnL_Pct', 'Avg_PnL_Pct']

# Calcul du winrate quotidien
exit_trades['Win'] = exit_trades['Net P&L JPY'] > 0
daily_winrate = exit_trades.groupby('Date')['Win'].apply(lambda x: x.sum() / len(x) * 100).reset_index()
daily_winrate.columns = ['Date', 'Win_Rate']
daily_analysis = pd.merge(daily_analysis, daily_winrate, on='Date')

# ANALYSE MENSUELLE
print('Calcul des performances mensuelles...')
exit_trades['Month'] = exit_trades['Date and time'].dt.to_period('M')
monthly_analysis = exit_trades.groupby('Month').agg({
    'Net P&L JPY': ['sum', 'mean', 'std', 'count'],
    'Net P&L %': ['sum', 'mean', 'std']
}).reset_index()
monthly_analysis.columns = ['Month', 'Total_PnL_JPY', 'Avg_PnL_JPY', 'Std_PnL_JPY', 'Trade_Count', 'Total_PnL_Pct', 'Avg_PnL_Pct', 'Std_PnL_Pct']

# Calcul du winrate mensuel
monthly_winrate = exit_trades.groupby('Month')['Win'].apply(lambda x: x.sum() / len(x) * 100).reset_index()
monthly_winrate.columns = ['Month', 'Win_Rate']
monthly_analysis = pd.merge(monthly_analysis, monthly_winrate, on='Month')

# ANALYSE DU BIAS (Long/Short)
print('Calcul du biais Long/Short...')
long_trades = len(exit_trades[exit_trades['Type'].str.contains('long', case=False)])
short_trades = len(exit_trades[exit_trades['Type'].str.contains('short', case=False)])
total_trades = len(exit_trades)
bias_stats = {
    'long_trades': long_trades,
    'short_trades': short_trades,
    'total_trades': total_trades,
    'long_percentage': (long_trades / total_trades * 100) if total_trades > 0 else 0,
    'short_percentage': (short_trades / total_trades * 100) if total_trades > 0 else 0
}

# ANALYSE HEBDOMADAIRE AVANCEE
print('Calcul de l_analyse hebdomadaire avancee...')
exit_trades['Weekday'] = exit_trades['Date and time'].dt.day_name()
exit_trades['Month_Name'] = exit_trades['Date and time'].dt.month_name()
weekly_analysis = exit_trades.groupby(['Month_Name', 'Weekday']).agg({
    'Net P&L JPY': ['mean', 'std', 'count'],
    'Net P&L %': ['mean', 'std']
}).reset_index()
weekly_analysis.columns = ['Month', 'Weekday', 'Avg_PnL_JPY', 'Std_PnL_JPY', 'Trade_Count', 'Avg_PnL_Pct', 'Std_PnL_Pct']

# Calcul du winrate hebdomadaire
weekly_winrate = exit_trades.groupby(['Month_Name', 'Weekday'])['Win'].apply(lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0).reset_index()
weekly_winrate.columns = ['Month', 'Weekday', 'Win_Rate']
weekly_analysis = pd.merge(weekly_analysis, weekly_winrate, on=['Month', 'Weekday'])

# SAUVEGARDE DES RAPPORTS
print('Generation des rapports...')
daily_analysis.to_csv(f'reports/{base_name}_daily_analysis.csv', index=False)
monthly_analysis.to_csv(f'reports/{base_name}_monthly_analysis.csv', index=False)
pd.DataFrame([bias_stats]).to_csv(f'reports/{base_name}_bias_analysis.csv', index=False)
weekly_analysis.to_csv(f'reports/{base_name}_weekly_analysis.csv', index=False)

# AFFICHAGE DES RESULTATS
print('\n=== RESUME DE L_ANALYSE ===')
print(f'Nombre de trades: {total_trades}')
total_pl = exit_trades['Net P&L JPY'].sum()
print(f'P and L total: {total_pl:,.2f} JPY')
win_rate = (exit_trades['Net P&L JPY'] > 0).sum() / len(exit_trades) * 100
print(f'Win rate: {win_rate:.2f}%')
print(f'Biais Long: {bias_stats["long_percentage"]:.2f}% ({long_trades} trades)')
print(f'Biais Short: {bias_stats["short_percentage"]:.2f}% ({short_trades} trades)')
print('\nRapports generes dans le dossier reports/')
print('Fichiers generes:')
print(f'  - {base_name}_daily_analysis.csv')
print(f'  - {base_name}_monthly_analysis.csv')
print(f'  - {base_name}_bias_analysis.csv')
print(f'  - {base_name}_weekly_analysis.csv')
