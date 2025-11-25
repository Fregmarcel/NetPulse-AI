"""
Page Dashboard - Visualisation des KPIs et métriques en temps réel.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
from backend.analytics.kpi_calculator import get_latest_kpis, calculate_period_statistics
from backend.database.models import MesureKPI
from backend.database.connection import get_db_context
import config

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Vérifier l'authentification
if not st.session_state.get('authenticated', False):
    st.warning("⚠️ Veuillez vous connecter")
    st.stop()

st.title("📊 Dashboard - Supervision en Temps Réel")

# Récupérer la liaison sélectionnée
link_id = st.session_state.get('selected_link')

if not link_id:
    st.error("Aucune liaison sélectionnée")
    st.stop()

# Récupérer les dernières métriques
kpis = get_latest_kpis(link_id)

if not kpis:
    st.info("💡 Aucune donnée disponible pour cette liaison. Importez des mesures depuis la page Import.")
    st.stop()

# === SECTION 1 : Métriques principales ===
st.markdown("### 📈 Métriques en Temps Réel")

col1, col2, col3, col4, col5 = st.columns(5)

# État global
with col1:
    etat = kpis['etat_global']
    if etat == 'NORMAL':
        st.success(f"✅ **{etat}**")
    elif etat == 'DEGRADED':
        st.warning(f"⚠️ **{etat}**")
    else:
        st.error(f"🔴 **{etat}**")

with col2:
    delta_color = "normal" if kpis['rssi_dbm'] >= config.SEUILS_RSSI['ACCEPTABLE'] else "inverse"
    st.metric("RSSI", f"{kpis['rssi_dbm']:.1f} dBm", delta=None)

with col3:
    st.metric("SNR", f"{kpis['snr_db']:.1f} dB")

with col4:
    st.metric("BER", f"{kpis['ber']:.2e}")

with col5:
    st.metric("Modulation", kpis['acm_modulation'])

# Métriques secondaires
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Latence", f"{kpis.get('latency_ms', 0):.1f} ms")

with col2:
    st.metric("Perte paquets", f"{kpis.get('packet_loss', 0):.2f} %")

with col3:
    rainfall = kpis.get('rainfall_mm', 0)
    st.metric("Pluie", f"{rainfall:.1f} mm" + (" 🌧️" if rainfall > 5 else ""))

with col4:
    minutes_ago = (datetime.utcnow() - kpis['timestamp']).seconds // 60
    st.metric("Dernière mesure", f"Il y a {minutes_ago} min")

st.markdown("---")

# === SECTION 2 : Graphiques ===
st.markdown("### 📉 Graphiques de Tendance")

# Sélection de la période
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**Période d'analyse**")
with col2:
    period_options = ["6h", "12h", "24h", "48h", "72h", "7j", "30j", "Tout"]
    period_selected = st.selectbox("", period_options, index=5, label_visibility="collapsed", key="period_selector")

# Calculer date_from AVANT la requête en utilisant la valeur sélectionnée
if period_selected == "Tout":
    date_from = None
elif period_selected == "7j":
    date_from = datetime.utcnow() - timedelta(days=7)
elif period_selected == "30j":
    date_from = datetime.utcnow() - timedelta(days=30)
else:
    # Extraire les heures (6h, 12h, etc.)
    hours = int(period_selected.replace('h', ''))
    date_from = datetime.utcnow() - timedelta(hours=hours)

# Récupérer les données
with get_db_context() as db:
    query = db.query(MesureKPI).filter(MesureKPI.link_id == link_id)
    
    if date_from is not None:
        query = query.filter(MesureKPI.timestamp >= date_from)
    
    measures = query.order_by(MesureKPI.timestamp).all()
    
    # Conversion en dictionnaires DANS le contexte de la session
    measures_data = [{
        'timestamp': m.timestamp,
        'rssi_dbm': m.rssi_dbm,
        'snr_db': m.snr_db,
        'ber': m.ber,
        'rainfall_mm': m.rainfall_mm,
        'latency_ms': m.latency_ms,
        'packet_loss': m.packet_loss
    } for m in measures]

if len(measures_data) < 2:
    st.warning(f"⚠️ Aucune donnée disponible pour la période sélectionnée ({period_selected}). Essayez 'Tout' pour voir toutes les mesures.")
else:
    # Afficher info si données anciennes
    if measures_data:
        latest_measure = max(m['timestamp'] for m in measures_data)
        time_diff = datetime.utcnow() - latest_measure
        if time_diff > timedelta(hours=24):
            days_old = time_diff.days
            st.info(f"ℹ️ Les dernières données datent d'il y a {days_old} jour(s). Importez de nouvelles mesures pour mettre à jour.")
    
    # Conversion en DataFrame
    df = pd.DataFrame(measures_data)
    
    # Graphique RSSI
    fig_rssi = go.Figure()
    fig_rssi.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['rssi_dbm'],
        mode='lines+markers',
        name='RSSI',
        line=dict(color='#3B82F6', width=2),
        marker=dict(size=4)
    ))
    
    # Ajouter les seuils
    fig_rssi.add_hline(y=config.SEUILS_RSSI['ACCEPTABLE'], line_dash="dash",
                       line_color="orange", annotation_text="Seuil Acceptable")
    fig_rssi.add_hline(y=config.SEUILS_RSSI['DEGRADED'], line_dash="dash",
                       line_color="red", annotation_text="Seuil Dégradé")
    
    fig_rssi.update_layout(
        title="RSSI (Received Signal Strength Indicator)",
        xaxis_title="Temps",
        yaxis_title="RSSI (dBm)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_rssi, use_container_width=True)
    
    # Graphique SNR
    fig_snr = go.Figure()
    fig_snr.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['snr_db'],
        mode='lines+markers',
        name='SNR',
        line=dict(color='#10B981', width=2),
        marker=dict(size=4)
    ))
    
    fig_snr.add_hline(y=config.SEUILS_SNR['ACCEPTABLE'], line_dash="dash",
                      line_color="orange", annotation_text="Seuil Acceptable")
    fig_snr.add_hline(y=config.SEUILS_SNR['DEGRADED'], line_dash="dash",
                      line_color="red", annotation_text="Seuil Dégradé")
    
    fig_snr.update_layout(
        title="SNR (Signal-to-Noise Ratio)",
        xaxis_title="Temps",
        yaxis_title="SNR (dB)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_snr, use_container_width=True)
    
    # Graphique RSSI vs Pluie
    fig_rain = go.Figure()
    
    fig_rain.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['rssi_dbm'],
        mode='lines',
        name='RSSI',
        line=dict(color='#3B82F6', width=2),
        yaxis='y1'
    ))
    
    fig_rain.add_trace(go.Bar(
        x=df['timestamp'],
        y=df['rainfall_mm'],
        name='Pluie',
        marker_color='#60A5FA',
        opacity=0.6,
        yaxis='y2'
    ))
    
    fig_rain.update_layout(
        title="Corrélation RSSI vs Pluie",
        xaxis_title="Temps",
        yaxis=dict(title="RSSI (dBm)", side='left'),
        yaxis2=dict(title="Pluie (mm)", side='right', overlaying='y'),
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_rain, use_container_width=True)

# === SECTION 3 : Statistiques détaillées ===
st.markdown("---")
st.markdown("### 📊 Statistiques Détaillées")

# Calculer les heures pour les statistiques
if period_selected == "Tout":
    stats_hours = 24 * 365  # 1 an pour "Tout"
elif period_selected == "7j":
    stats_hours = 24 * 7
elif period_selected == "30j":
    stats_hours = 24 * 30
else:
    stats_hours = int(period_selected.replace('h', ''))

stats = calculate_period_statistics(link_id, hours=stats_hours)

if stats:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**RSSI (dBm)**")
        st.write(f"• Moyenne: {stats['rssi']['avg']:.2f}")
        st.write(f"• Min: {stats['rssi']['min']:.2f}")
        st.write(f"• Max: {stats['rssi']['max']:.2f}")
        st.write(f"• Écart-type: {stats['rssi']['std']:.2f}")
        
        st.markdown("**SNR (dB)**")
        st.write(f"• Moyenne: {stats['snr']['avg']:.2f}")
        st.write(f"• Min: {stats['snr']['min']:.2f}")
        st.write(f"• Max: {stats['snr']['max']:.2f}")
        st.write(f"• Écart-type: {stats['snr']['std']:.2f}")
    
    with col2:
        st.markdown("**Performance**")
        st.write(f"• Disponibilité: {stats['disponibilite']:.2f} %")
        st.write(f"• Nombre de mesures: {stats['nb_mesures']}")
        
        st.markdown("**Pluie**")
        st.write(f"• Moyenne: {stats['rainfall']['avg']:.2f} mm")
        st.write(f"• Maximum: {stats['rainfall']['max']:.2f} mm")
        
        st.markdown("**Latence**")
        st.write(f"• Moyenne: {stats['latency']['avg']:.2f} ms")
        st.write(f"• Maximum: {stats['latency']['max']:.2f} ms")

# Bouton d'actualisation
st.markdown("---")
if st.button("🔄 Actualiser les données", use_container_width=True):
    st.rerun()
