# Configuration du projet TradingView Analyzer

import os

# Chemins de base
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKTEST_DIR = os.path.join(BASE_DIR, 'backtest_a_analyser')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

# Configuration des colonnes
PnL_COLUMNS = ['Profit', 'PnL', 'P&L', 'Net Profit', 'Profit/Loss']
STATUS_COLUMNS = ['Status', 'Win/Loss', 'Result']
DIRECTION_COLUMNS = ['Type', 'Direction', 'Position']
TIME_COLUMNS = ['Entry Time', 'Exit Time', 'Entry', 'Exit']

# Parametres d'analyse
MIN_TRADES_FOR_ANALYSIS = 10
CONFIDENCE_LEVEL = 0.95
