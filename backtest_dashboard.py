# Interface graphique complète pour l'analyse de backtest TradingView
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Configuration de la page
st.set_page_config(
    page_title="Analyse Backtest TradingView",
    layout="wide",
    page_icon="📊"
)

# Titre de l'application
st.title("📊 Dashboard d'Analyse de Backtest TradingView")

# Sidebar pour les paramètres
st.sidebar.header("📁 Sélection des fichiers")

# Fonction pour extraire le nom de l'actif du nom de fichier
def extract_asset_name(filename):
    """Extrait le nom de l'actif depuis le nom du fichier"""
    asset_name = "INCONNU"
    if "_" in filename:
        parts = filename.split("_")
        for part in parts:
            # Chercher le code actif (GBPJPY, EURUSD, etc.)
            if len(part) == 6 and part.isupper() and any(c.isalpha() for c in part):
                asset_name = part
                break
    return asset_name

# Fonction pour calculer le drawdown
def calculate_drawdown_analysis(trades_df):
    """Calcule l'analyse détaillée du drawdown"""
    try:
        df_sorted = trades_df.sort_values('Date and time').copy()
        df_sorted['Cumulative_PnL'] = df_sorted['Net P&L JPY'].cumsum()
        df_sorted['Running_Max'] = df_sorted['Cumulative_PnL'].expanding().max()
        df_sorted['Drawdown_Absolute'] = df_sorted['Cumulative_PnL'] - df_sorted['Running_Max']
        df_sorted['Drawdown_Percentage'] = (df_sorted['Drawdown_Absolute'] / df_sorted['Running_Max'].replace(0, np.nan)) * 100
        max_drawdown_abs = df_sorted['Drawdown_Absolute'].min()
        max_drawdown_pct = df_sorted['Drawdown_Percentage'].min()
        
        return {
            'drawdown_data': df_sorted,
            'max_drawdown_absolute': max_drawdown_abs,
            'max_drawdown_percentage': max_drawdown_pct,
            'current_drawdown': df_sorted['Drawdown_Absolute'].iloc[-1],
            'current_drawdown_pct': df_sorted['Drawdown_Percentage'].iloc[-1]
        }
    except Exception as e:
        return None

# Fonction d'analyse complète
def analyze_xlsx_file_complete(file_path):
    """Analyse complète d'un fichier XLSX"""
    try:
        trades_df = pd.read_excel(file_path, sheet_name='List of trades')
        exit_trades = trades_df[trades_df['Type'].str.contains('Exit')].copy()
        exit_trades['Date and time'] = pd.to_datetime(exit_trades['Date and time'])
        asset_name = extract_asset_name(os.path.basename(file_path))
        
        drawdown_info = calculate_drawdown_analysis(exit_trades)
        
        # ANALYSE SPÉCIFIQUE POUR OPTIMISATION PAR ACTIF/MOIS
        exit_trades['Year'] = exit_trades['Date and time'].dt.year
        exit_trades['Month'] = exit_trades['Date and time'].dt.month
        exit_trades['Month_Name'] = exit_trades['Date and time'].dt.month_name()
        exit_trades['Weekday'] = exit_trades['Date and time'].dt.day_name()
        exit_trades['Day_of_Week'] = exit_trades['Date and time'].dt.dayofweek
        
        optimal_daily_analysis = exit_trades.groupby(['Month_Name', 'Weekday']).agg({
            'Net P&L JPY': ['sum', 'mean', 'count', 'std'],
            'Net P&L %': ['sum', 'mean', 'std']
        }).reset_index()
        optimal_daily_analysis.columns = ['Mois', 'Jour_Semaine', 'Total_PnL_JPY', 'Moyenne_PnL_JPY', 'Nb_Trades', 'Std_PnL_JPY', 'Total_PnL_Pct', 'Moyenne_PnL_Pct', 'Std_PnL_Pct']
        
        exit_trades['Win'] = exit_trades['Net P&L JPY'] > 0
        winrate_analysis = exit_trades.groupby(['Month_Name', 'Weekday'])['Win'].apply(lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0).reset_index()
        winrate_analysis.columns = ['Mois', 'Jour_Semaine', 'Win_Rate']
        
        optimal_daily_analysis = pd.merge(optimal_daily_analysis, winrate_analysis, on=['Mois', 'Jour_Semaine'])
        best_day_per_month = None
        if not optimal_daily_analysis.empty:
            best_day_per_month = optimal_daily_analysis.loc[optimal_daily_analysis.groupby('Mois')['Total_PnL_JPY'].idxmax()]
        
        # ANALYSES STANDARD
        exit_trades['Date'] = exit_trades['Date and time'].dt.date
        daily_analysis = exit_trades.groupby('Date').agg({
            'Net P&L JPY': ['sum', 'mean', 'count'],
            'Net P&L %': ['sum', 'mean']
        }).reset_index()
        daily_analysis.columns = ['Date', 'Total_PnL_JPY', 'Avg_PnL_JPY', 'Trade_Count', 'Total_PnL_Pct', 'Avg_PnL_Pct']
        
        daily_winrate = exit_trades.groupby('Date')['Win'].apply(lambda x: x.sum() / len(x) * 100).reset_index()
        daily_winrate.columns = ['Date', 'Win_Rate']
        daily_analysis = pd.merge(daily_analysis, daily_winrate, on='Date')
        
        exit_trades['Month_Period'] = exit_trades['Date and time'].dt.to_period('M')
        monthly_analysis = exit_trades.groupby('Month_Period').agg({
            'Net P&L JPY': ['sum', 'mean', 'std', 'count'],
            'Net P&L %': ['sum', 'mean', 'std']
        }).reset_index()
        monthly_analysis.columns = ['Month', 'Total_PnL_JPY', 'Avg_PnL_JPY', 'Std_PnL_JPY', 'Trade_Count', 'Total_PnL_Pct', 'Avg_PnL_Pct', 'Std_PnL_Pct']
        
        monthly_winrate = exit_trades.groupby('Month_Period')['Win'].apply(lambda x: x.sum() / len(x) * 100).reset_index()
        monthly_winrate.columns = ['Month', 'Win_Rate']
        monthly_analysis = pd.merge(monthly_analysis, monthly_winrate, on='Month')
        
        long_trades = len(exit_trades[exit_trades['Type'].str.contains('long', case=False)])
        short_trades = len(exit_trades[exit_trades['Type'].str.contains('short', case=False)])
        total_trades = len(exit_trades)
        bias_stats = {
            'long_trades': long_trades,
            'short_trades': short_trades,
            'total_trades': total_trades,
            'long_percentage': (long_trades / total_trades * 100) if total_trades > 0 else 0,
            'short_percentage': (short_trades / total_trades * 100) if total_trades > 0 else 0,
            'asset_name': asset_name
        }
        bias_df = pd.DataFrame([bias_stats])
        
        weekly_analysis = exit_trades.groupby(['Month_Name', 'Weekday']).agg({
            'Net P&L JPY': ['mean', 'std', 'count'],
            'Net P&L %': ['mean', 'std']
        }).reset_index()
        weekly_analysis.columns = ['Month', 'Weekday', 'Avg_PnL_JPY', 'Std_PnL_JPY', 'Trade_Count', 'Avg_PnL_Pct', 'Std_PnL_Pct']
        
        weekly_winrate = exit_trades.groupby(['Month_Name', 'Weekday'])['Win'].apply(lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0).reset_index()
        weekly_winrate.columns = ['Month', 'Weekday', 'Win_Rate']
        weekly_analysis = pd.merge(weekly_analysis, weekly_winrate, on=['Month', 'Weekday'])
        
        return {
            'daily_analysis': daily_analysis,
            'monthly_analysis': monthly_analysis,
            'bias_analysis': bias_df,
            'weekly_analysis': weekly_analysis,
            'drawdown_info': drawdown_info,
            'optimal_daily_analysis': optimal_daily_analysis,
            'best_day_per_month': best_day_per_month,
            'asset_name': asset_name,
            'total_pnl': daily_analysis['Total_PnL_JPY'].sum() if not daily_analysis.empty else 0,
            'total_trades': total_trades,
            'win_rate_global': (exit_trades['Net P&L JPY'] > 0).sum() / total_trades * 100 if total_trades > 0 else 0
        }
    except Exception as e:
        st.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
        return None

# Fonction pour analyse du tableau de vérité
def analyze_single_file_truth(file_path):
    """Analyse pour le tableau de vérité"""
    try:
        trades_df = pd.read_excel(file_path, sheet_name='List of trades')
        exit_trades = trades_df[trades_df['Type'].str.contains('Exit')].copy()
        exit_trades['Date and time'] = pd.to_datetime(exit_trades['Date and time'])
        asset_name = extract_asset_name(os.path.basename(file_path))
        
        exit_trades['Weekday'] = exit_trades['Date and time'].dt.day_name()
        weekday_analysis = exit_trades.groupby('Weekday').agg({
            'Net P&L JPY': ['sum', 'mean', 'count'],
            'Net P&L %': ['sum', 'mean']
        }).reset_index()
        weekday_analysis.columns = ['Jour_Semaine', 'Total_PnL_JPY', 'Moyenne_PnL_JPY', 'Nb_Trades', 'Total_PnL_Pct', 'Moyenne_PnL_Pct']
        
        exit_trades['Win'] = exit_trades['Net P&L JPY'] > 0
        winrate_analysis = exit_trades.groupby('Weekday')['Win'].apply(lambda x: x.sum() / len(x) * 100 if len(x) > 0 else 0).reset_index()
        winrate_analysis.columns = ['Jour_Semaine', 'Win_Rate']
        
        weekday_analysis = pd.merge(weekday_analysis, winrate_analysis, on='Jour_Semaine')
        weekday_analysis['Est_Rentable'] = weekday_analysis['Total_PnL_JPY'] > 0
        weekday_analysis['Qualite_Signal'] = weekday_analysis['Win_Rate'] > 50
        
        long_analysis = exit_trades.groupby('Weekday')['Type'].apply(
            lambda x: (x.str.contains('long', case=False)).sum() / len(x) * 100 if len(x) > 0 else 0
        ).reset_index()
        long_analysis.columns = ['Jour_Semaine', 'Pourcentage_Long']
        weekday_analysis = pd.merge(weekday_analysis, long_analysis, on='Jour_Semaine')
        
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_analysis['Day_Order'] = weekday_analysis['Jour_Semaine'].apply(
            lambda x: days_order.index(x) if x in days_order else 7
        )
        weekday_analysis = weekday_analysis.sort_values('Day_Order')
        weekday_analysis = weekday_analysis.drop('Day_Order', axis=1)
        
        return {
            'asset_name': asset_name,
            'weekday_analysis': weekday_analysis,
            'total_pnl': exit_trades['Net P&L JPY'].sum(),
            'total_trades': len(exit_trades),
            'win_rate_global': (exit_trades['Net P&L JPY'] > 0).sum() / len(exit_trades) * 100 if len(exit_trades) > 0 else 0
        }
    except Exception as e:
        st.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
        return None

# Rechercher les fichiers XLSX disponibles
xlsx_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]

if xlsx_files:
    st.sidebar.write("Sélectionnez les fichiers à analyser:")
    selected_files = st.sidebar.multiselect(
        'Choisissez un ou plusieurs fichiers:',
        xlsx_files,
        default=xlsx_files[:3] if len(xlsx_files) > 0 else []
    )
    
    if selected_files:
        st.sidebar.write(f"### Fichiers sélectionnés ({len(selected_files)}):")
        for file in selected_files[:3]:
            try:
                file_mtime = os.path.getmtime(file)
                file_date = datetime.fromtimestamp(file_mtime)
                st.sidebar.info(f"{os.path.basename(file)}\n({file_date.strftime('%d/%m/%Y')})")
            except:
                st.sidebar.info(f"{os.path.basename(file)}")
        if len(selected_files) > 3:
            st.sidebar.info(f"... et {len(selected_files) - 3} autres")
    
    analyze_button = st.sidebar.button('🔍 Analyser les fichiers sélectionnés', type="primary")
    
    if analyze_button:
        if selected_files:
            with st.spinner(f'Analyse de {len(selected_files)} fichiers en cours...'):
                complete_analyses = []
                truth_analyses = []
                
                progress_bar = st.progress(0)
                for i, file in enumerate(selected_files):
                    complete_analysis = analyze_xlsx_file_complete(file)
                    if complete_analysis:
                        complete_analyses.append(complete_analysis)
                    
                    truth_analysis = analyze_single_file_truth(file)
                    if truth_analysis:
                        truth_analyses.append(truth_analysis)
                    
                    progress_bar.progress((i + 1) / len(selected_files))
                
                if complete_analyses:
                    st.session_state['complete_analysis_complete'] = True
                    st.session_state['complete_analyses'] = complete_analyses
                    st.session_state['truth_analyses'] = truth_analyses
                    st.success(f"Analyse de {len(complete_analyses)} actifs terminée!")
                else:
                    st.error("Impossible d'analyser les fichiers - vérifiez que les fichiers sont valides")
        else:
            st.warning("Veuillez sélectionner au moins un fichier")
else:
    st.warning('Aucun fichier XLSX trouvé dans le dossier')

# Afficher les résultats si l'analyse est lancée
if 'complete_analysis_complete' in st.session_state and st.session_state['complete_analysis_complete']:
    complete_analyses = st.session_state['complete_analyses']
    truth_analyses = st.session_state['truth_analyses']
    
    st.header("📊 Dashboard d'Analyse de Backtest TradingView")
    
    # Choix du type d'analyse
    analysis_type = st.radio(
        "Choisissez le type d'analyse:",
        ["📋 Tableau de Vérité (NOUVEAU)", "🎯 Optimisation par Actif/Mois", "📈 Analyse Détaillée", "📉 Visualisations Graphiques"],
        horizontal=True
    )
    
    if analysis_type == "📋 Tableau de Vérité (NOUVEAU)":
        st.subheader("📋 TABLEAU DE VÉRITÉ - Validation des Hypothèses")
        
        if truth_analyses:
            # Créer le tableau de vérité
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            assets_list = [analysis['asset_name'] for analysis in truth_analyses]
            
            truth_matrix = pd.DataFrame(index=days_order, columns=assets_list)
            details_matrix = {}
            
            for analysis in truth_analyses:
                asset_name = analysis['asset_name']
                weekday_df = analysis['weekday_analysis']
                details_matrix[asset_name] = weekday_df.set_index('Jour_Semaine')
                
                for day in days_order:
                    if day in weekday_df['Jour_Semaine'].values:
                        day_data = weekday_df[weekday_df['Jour_Semaine'] == day].iloc[0]
                        is_profitable = day_data['Est_Rentable']
                        is_good_quality = day_data['Qualite_Signal']
                        
                        if is_profitable and is_good_quality:
                            truth_matrix.loc[day, asset_name] = "✅ OUI"
                        elif is_profitable:
                            truth_matrix.loc[day, asset_name] = "⚠️ P&L+"
                        elif is_good_quality:
                            truth_matrix.loc[day, asset_name] = "⚠️ WR+"
                        else:
                            truth_matrix.loc[day, asset_name] = "❌ NON"
                    else:
                        truth_matrix.loc[day, asset_name] = "➖ N/A"
            
            st.write("### 🔍 TABLEAU DE VÉRITÉ : Jour VS Actif")
            st.write("*✅ OUI = Rentable + Bon Win Rate | ⚠️ P&L+ = Seulement rentable | ⚠️ WR+ = Bon Win Rate seulement | ❌ NON = Ni l'un ni l'autre*")
            st.dataframe(truth_matrix, use_container_width=True)
            
            # Détails par actif
            st.write("### 📋 DÉTAILS PAR ACTIF")
            for analysis in truth_analyses:
                asset_name = analysis['asset_name']
                weekday_df = analysis['weekday_analysis']
                
                with st.expander(f"📋 {asset_name} - Détails (P&L: {analysis['total_pnl']:.0f} JPY)", expanded=False):
                    display_df = weekday_df.copy()
                    display_df['Performance'] = display_df.apply(
                        lambda row: "✅" if row['Est_Rentable'] and row['Qualite_Signal'] 
                                   else "⚠️" if row['Est_Rentable'] or row['Qualite_Signal']
                                   else "❌", axis=1
                    )
                    st.dataframe(display_df[['Jour_Semaine', 'Total_PnL_JPY', 'Win_Rate', 'Nb_Trades', 'Performance']], use_container_width=True)
        else:
            st.warning("Aucune analyse disponible")
    
    elif analysis_type == "🎯 Optimisation par Actif/Mois":
        st.subheader("🎯 Analyse d'Optimisation par Actif/Mois")
        
        if complete_analyses:
            asset_names = [analysis['asset_name'] for analysis in complete_analyses]
            selected_asset = st.selectbox("Choisissez un actif à analyser:", asset_names)
            
            selected_analysis = None
            for analysis in complete_analyses:
                if analysis['asset_name'] == selected_asset:
                    selected_analysis = analysis
                    break
            
            if selected_analysis:
                daily_data = selected_analysis['daily_analysis']
                monthly_data = selected_analysis['monthly_analysis']
                bias_data = selected_analysis['bias_analysis'].iloc[0]
                weekly_data = selected_analysis['weekly_analysis']
                drawdown_info = selected_analysis['drawdown_info']
                optimal_daily = selected_analysis['optimal_daily_analysis']
                best_day_per_month = selected_analysis['best_day_per_month']
                asset_name = selected_analysis['asset_name']
                
                # Métriques principales
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Nombre de Trades", f"{int(bias_data['total_trades'])}")
                with col2:
                    st.metric("P&L Total", f"{selected_analysis['total_pnl']:.0f} JPY")
                with col3:
                    st.metric("Win Rate Global", f"{selected_analysis['win_rate_global']:.1f}%")
                with col4:
                    if drawdown_info and 'max_drawdown_percentage' in drawdown_info:
                        st.metric("Drawdown Max", f"{drawdown_info['max_drawdown_percentage']:.1f}%")
                
                # Tabs pour différentes analyses
                tab1, tab2, tab3 = st.tabs(["📅 Meilleur Jour/Mois", "📊 Heatmap Jour/Mois", "📋 Données Brutes"])
                
                with tab1:
                    st.write("### 📅 Meilleur Jour de Trading par Mois")
                    if best_day_per_month is not None and not best_day_per_month.empty:
                        st.dataframe(best_day_per_month[['Mois', 'Jour_Semaine', 'Total_PnL_JPY', 'Win_Rate', 'Nb_Trades']].sort_values('Mois'))
                        
                        # Recommandations
                        st.write("### 💡 Recommandations")
                        profitable_configs = best_day_per_month[
                            (best_day_per_month['Total_PnL_JPY'] > 0) & 
                            (best_day_per_month['Win_Rate'] > 50) &
                            (best_day_per_month['Nb_Trades'] >= 5)
                        ]
                        if not profitable_configs.empty:
                            st.success("Configurations recommandées:")
                            for _, config in profitable_configs.iterrows():
                                st.write(f"- {config['Mois']}: Trader le {config['Jour_Semaine']} "
                                       f"(P&L: {config['Total_PnL_JPY']:.0f} JPY, "
                                       f"Win Rate: {config['Win_Rate']:.1f}%)")
                        else:
                            st.info("Pas de configurations fortement rentables identifiées")
                    else:
                        st.info("Pas de données optimisées disponibles")
                
                with tab2:
                    st.write("### 🌡️ Heatmap des Performances")
                    if optimal_daily is not None and not optimal_daily.empty:
                        # Créer une heatmap
                        pivot_heatmap = optimal_daily.pivot_table(
                            values='Total_PnL_JPY', 
                            index='Jour_Semaine', 
                            columns='Mois', 
                            aggfunc='sum', 
                            fill_value=0
                        )
                        
                        # Réordonner les jours
                        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        pivot_heatmap = pivot_heatmap.reindex(
                            index=[day for day in days_order if day in pivot_heatmap.index],
                            columns=[col for col in pivot_heatmap.columns if col in pivot_heatmap.columns]
                        )
                        
                        if not pivot_heatmap.empty:
                            fig_heatmap = go.Figure(data=go.Heatmap(
                                z=pivot_heatmap.values,
                                x=pivot_heatmap.columns,
                                y=pivot_heatmap.index,
                                colorscale='RdYlGn',
                                colorbar=dict(title="P&L (JPY)"),
                                zmid=0
                            ))
                            
                            fig_heatmap.update_layout(
                                title=f"Heatmap des Performances - {asset_name}",
                                xaxis_title="Mois",
                                yaxis_title="Jour de la Semaine"
                            )
                            
                            st.plotly_chart(fig_heatmap, use_container_width=True)
                    else:
                        st.info("Pas de données pour la heatmap")
                
                with tab3:
                    st.write("### 📋 Données Brutes Complètes")
                    if optimal_daily is not None and not optimal_daily.empty:
                        st.dataframe(optimal_daily, use_container_width=True)
                    else:
                        st.info("Pas de données brutes disponibles")
        else:
            st.warning("Aucune analyse disponible")
    
    elif analysis_type == "📈 Analyse Détaillée":
        st.subheader("📈 Analyse Détaillée des Performances")
        
        if complete_analyses:
            asset_names = [analysis['asset_name'] for analysis in complete_analyses]
            selected_asset = st.selectbox("Sélectionnez un actif:", asset_names, key="detail_asset")
            
            selected_analysis = None
            for analysis in complete_analyses:
                if analysis['asset_name'] == selected_asset:
                    selected_analysis = analysis
                    break
            
            if selected_analysis:
                daily_data = selected_analysis['daily_analysis']
                monthly_data = selected_analysis['monthly_analysis']
                bias_data = selected_analysis['bias_analysis'].iloc[0]
                weekly_data = selected_analysis['weekly_analysis']
                
                # Afficher les métriques
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("P&L Total", f"{selected_analysis['total_pnl']:.0f} JPY")
                with col2:
                    st.metric("Nb Trades", f"{selected_analysis['total_trades']}")
                with col3:
                    st.metric("Win Rate", f"{selected_analysis['win_rate_global']:.1f}%")
                with col4:
                    st.metric("Biais Long", f"{bias_data['long_percentage']:.1f}%")
                
                # Tabs pour différentes visualisations
                detail_tab1, detail_tab2, detail_tab3 = st.tabs(["📈 Courbe Equity", "📊 Performance Mensuelle", "🗓️ Performance Hebdomadaire"])
                
                with detail_tab1:
                    st.write("### 📈 Courbe d'Equity")
                    if daily_data is not None and not daily_data.empty:
                        daily_sorted = daily_data.sort_values('Date')
                        daily_sorted['Cumulative_PnL'] = daily_sorted['Total_PnL_JPY'].cumsum()
                        
                        fig_equity = go.Figure()
                        fig_equity.add_trace(go.Scatter(
                            x=daily_sorted['Date'],
                            y=daily_sorted['Cumulative_PnL'],
                            mode='lines',
                            name='Equity',
                            line=dict(color='blue', width=2)
                        ))
                        
                        fig_equity.update_layout(
                            title="Courbe d'Equity",
                            xaxis_title="Date",
                            yaxis_title="P&L Cumulatif (JPY)"
                        )
                        
                        st.plotly_chart(fig_equity, use_container_width=True)
                    else:
                        st.info("Pas de données pour la courbe d'équity")
                
                with detail_tab2:
                    st.write("### 📊 Performance Mensuelle")
                    if monthly_data is not None and not monthly_data.empty:
                        # Graphique mensuel
                        monthly_sorted = monthly_data.sort_values('Month')
                        colors = ['green' if x > 0 else 'red' for x in monthly_sorted['Total_PnL_JPY']]
                        
                        fig_monthly = go.Figure()
                        fig_monthly.add_trace(go.Bar(
                            x=monthly_sorted['Month'].astype(str),
                            y=monthly_sorted['Total_PnL_JPY'],
                            marker_color=colors,
                            name='P&L Mensuel'
                        ))
                        
                        fig_monthly.update_layout(
                            title="Performance Mensuelle",
                            xaxis_title="Mois",
                            yaxis_title="P&L (JPY)",
                            xaxis_tickangle=-45
                        )
                        
                        st.plotly_chart(fig_monthly, use_container_width=True)
                        
                        # Tableau des données
                        st.dataframe(monthly_data, use_container_width=True)
                    else:
                        st.info("Pas de données mensuelles disponibles")
                
                with detail_tab3:
                    st.write("### 🗓️ Performance Hebdomadaire")
                    if weekly_data is not None and not weekly_data.empty:
                        # Heatmap hebdomadaire
                        pivot_weekly = weekly_data.pivot_table(
                            values='Avg_PnL_JPY', 
                            index='Weekday', 
                            columns='Month', 
                            aggfunc='mean', 
                            fill_value=0
                        )
                        
                        if not pivot_weekly.empty:
                            fig_weekly = go.Figure(data=go.Heatmap(
                                z=pivot_weekly.values,
                                x=pivot_weekly.columns,
                                y=pivot_weekly.index,
                                colorscale='RdYlGn',
                                colorbar=dict(title="P&L Moyen"),
                                zmid=0
                            ))
                            
                            fig_weekly.update_layout(
                                title="Heatmap des Performances Hebdomadaires",
                                xaxis_title="Mois",
                                yaxis_title="Jour de la Semaine"
                            )
                            
                            st.plotly_chart(fig_weekly, use_container_width=True)
                        
                        # Tableau détaillé
                        st.dataframe(weekly_data, use_container_width=True)
                    else:
                        st.info("Pas de données hebdomadaires disponibles")
        else:
            st.warning("Aucune analyse disponible")
    
    elif analysis_type == "📉 Visualisations Graphiques":
        st.subheader("📉 Visualisations Graphiques Complètes")
        
        if complete_analyses:
            asset_names = [analysis['asset_name'] for analysis in complete_analyses]
            selected_asset = st.selectbox("Sélectionnez un actif pour visualisation:", asset_names, key="viz_asset")
            
            selected_analysis = None
            for analysis in complete_analyses:
                if analysis['asset_name'] == selected_asset:
                    selected_analysis = analysis
                    break
            
            if selected_analysis:
                daily_data = selected_analysis['daily_analysis']
                monthly_data = selected_analysis['monthly_analysis']
                drawdown_info = selected_analysis['drawdown_info']
                
                # Graphiques dans des colonnes
                col1, col2 = st.columns(2)
                
                with col1:
                    # Courbe d'équity
                    st.write("### 📈 Courbe d'Equity")
                    if daily_data is not None and not daily_data.empty:
                        daily_sorted = daily_data.sort_values('Date')
                        daily_sorted['Cumulative_PnL'] = daily_sorted['Total_PnL_JPY'].cumsum()
                        
                        fig_equity = go.Figure()
                        fig_equity.add_trace(go.Scatter(
                            x=daily_sorted['Date'],
                            y=daily_sorted['Cumulative_PnL'],
                            mode='lines',
                            name='Equity',
                            line=dict(color='blue', width=2),
                            fill='tonexty',
                            fillcolor='rgba(0, 100, 255, 0.2)'
                        ))
                        
                        fig_equity.update_layout(
                            title="Courbe d'Equity Cumulative",
                            xaxis_title="Date",
                            yaxis_title="P&L Cumulatif (JPY)"
                        )
                        
                        st.plotly_chart(fig_equity, use_container_width=True)
                
                with col2:
                    # Histogramme des P&L quotidiens
                    st.write("### 📊 Distribution des P&L")
                    if daily_data is not None and not daily_data.empty:
                        fig_hist = go.Figure()
                        fig_hist.add_trace(go.Histogram(
                            x=daily_data['Total_PnL_JPY'],
                            nbinsx=30,
                            name='Distribution des P&L',
                            marker_color='lightblue',
                            opacity=0.7
                        ))
                        
                        fig_hist.update_layout(
                            title="Distribution des P&L Quotidiens",
                            xaxis_title="P&L (JPY)",
                            yaxis_title="Fréquence"
                        )
                        
                        st.plotly_chart(fig_hist, use_container_width=True)
                
                # Drawdown
                st.write("### 📉 Analyse du Drawdown")
                if drawdown_info and 'drawdown_data' in drawdown_info:
                    drawdown_data = drawdown_info['drawdown_data']
                    fig_drawdown = go.Figure()
                    fig_drawdown.add_trace(go.Scatter(
                        x=drawdown_data['Date and time'],
                        y=drawdown_data['Drawdown_Percentage'],
                        mode='lines',
                        name='Drawdown %',
                        line=dict(color='red', width=2),
                        fill='tonexty',
                        fillcolor='rgba(255, 0, 0, 0.3)'
                    ))
                    
                    fig_drawdown.update_layout(
                        title="Evolution du Drawdown (%)",
                        xaxis_title="Date",
                        yaxis_title="Drawdown (%)"
                    )
                    
                    st.plotly_chart(fig_drawdown, use_container_width=True)
                
                # Performance mensuelle
                st.write("### 📆 Performance Mensuelle")
                if monthly_data is not None and not monthly_data.empty:
                    monthly_sorted = monthly_data.sort_values('Month')
                    colors = ['green' if x > 0 else 'red' for x in monthly_sorted['Total_PnL_JPY']]
                    
                    fig_monthly = go.Figure()
                    fig_monthly.add_trace(go.Bar(
                        x=monthly_sorted['Month'].astype(str),
                        y=monthly_sorted['Total_PnL_JPY'],
                        marker_color=colors,
                        name='P&L Mensuel'
                    ))
                    
                    fig_monthly.update_layout(
                        title="Performance Mensuelle",
                        xaxis_title="Mois",
                        yaxis_title="P&L (JPY)",
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig_monthly, use_container_width=True)
        else:
            st.warning("Aucune analyse disponible")

# Pied de page
st.markdown("---")
st.caption("Dashboard d'analyse de backtest TradingView - Toutes les fonctionnalités")
