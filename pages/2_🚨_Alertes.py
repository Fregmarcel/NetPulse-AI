"""
Page Alertes - Gestion et visualisation des alertes système.
"""
import streamlit as st
from datetime import datetime, timedelta
from backend.alerts.alert_engine import get_active_alerts, resolve_alert, delete_alert, get_alerts_count_by_severity, check_and_create_alerts
from backend.database.models import Alerte
from backend.database.connection import get_db_context
from backend.security.auth import check_permission
import config

st.set_page_config(page_title="Alertes", page_icon="🚨", layout="wide")

# Vérifier l'authentification
if not st.session_state.get('authenticated', False):
    st.warning("⚠️ Veuillez vous connecter")
    st.stop()

# En-tête avec bouton de rafraîchissement
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🚨 Gestion des Alertes")
with col2:
    if st.button("🔄 Actualiser", use_container_width=True, type="secondary"):
        st.rerun()

user = st.session_state.user
link_id = st.session_state.get('selected_link')

if not link_id:
    st.error("Aucune liaison sélectionnée")
    st.stop()

# Afficher quelle liaison est active
from backend.database.models import FHLink
from backend.database.connection import get_db_context
with get_db_context() as db:
    active_link = db.query(FHLink).filter(FHLink.id == link_id).first()
    if active_link:
        st.info(f"📡 Liaison active : **{active_link.nom}** ({active_link.site_a} ↔ {active_link.site_b})")

# Vérification manuelle des alertes
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🔍 Vérifier Alertes", use_container_width=True):
        with st.spinner("Vérification en cours..."):
            new_alerts = check_and_create_alerts(link_id)
            if new_alerts:
                st.success(f"✅ {len(new_alerts)} nouvelle(s) alerte(s) créée(s)")
            else:
                st.info("Aucune nouvelle alerte")

# Statistiques
counts = get_alerts_count_by_severity(link_id)
total_actives = sum(counts.values())

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Actives", total_actives)
with col2:
    if counts.get('CRITIQUE', 0) > 0:
        st.error(f"🔴 **{counts.get('CRITIQUE', 0)}** Critiques")
    else:
        st.metric("Critiques", counts.get('CRITIQUE', 0))
with col3:
    st.metric("Majeures", counts.get('MAJEURE', 0))
with col4:
    st.metric("Mineures", counts.get('MINEURE', 0))
with col5:
    st.metric("Warnings", counts.get('WARNING', 0))

st.markdown("---")

# Filtres
st.markdown("### 🔎 Filtres")

col1, col2, col3 = st.columns(3)

with col1:
    filter_severity = st.multiselect(
        "Sévérité",
        options=list(config.ALERT_SEVERITIES.keys()),
        default=[]
    )

with col2:
    filter_status = st.selectbox(
        "Statut",
        options=["Toutes", "Actives", "Résolues"],
        index=1
    )

with col3:
    filter_period = st.selectbox(
        "Période",
        options=["Dernières 24h", "Derniers 7 jours", "Dernier mois", "Tout"],
        index=0
    )

# Récupérer les alertes
with get_db_context() as db:
    query = db.query(Alerte).filter(Alerte.link_id == link_id)
    
    # Filtre statut
    if filter_status == "Actives":
        query = query.filter(Alerte.resolved == False)
    elif filter_status == "Résolues":
        query = query.filter(Alerte.resolved == True)
    
    # Filtre sévérité
    if filter_severity:
        query = query.filter(Alerte.severite.in_(filter_severity))
    
    # Filtre période
    if filter_period != "Tout":
        if filter_period == "Dernières 24h":
            date_from = datetime.utcnow() - timedelta(hours=24)
        elif filter_period == "Derniers 7 jours":
            date_from = datetime.utcnow() - timedelta(days=7)
        else:  # Dernier mois
            date_from = datetime.utcnow() - timedelta(days=30)
        
        query = query.filter(Alerte.timestamp >= date_from)
    
    alert_objects = query.order_by(Alerte.timestamp.desc()).all()
    
    # Convertir en dictionnaires DANS le contexte de session
    alerts = []
    for alert in alert_objects:
        alerts.append({
            'id': alert.id,
            'link_id': alert.link_id,
            'timestamp': alert.timestamp,
            'type': alert.type,
            'severite': alert.severite,
            'message': alert.message,
            'recommandation': alert.recommandation,
            'resolved': alert.resolved,
            'valeur_mesuree': alert.valeur_mesuree,
            'seuil_declenche': alert.seuil_declenche,
            'ia_generated': alert.ia_generated,
            'resolved_at': alert.resolved_at,
            'resolved_by': alert.resolved_by
        })

st.markdown(f"### 📋 Alertes ({len(alerts)})")

# Affichage des alertes
if not alerts:
    st.info("✅ Aucune alerte correspondant aux critères")
else:
    for alert in alerts:
        severity_info = config.ALERT_SEVERITIES.get(alert.get('severite'), {})
        icon = severity_info.get('icon', '⚠️')
        color = severity_info.get('color', '#FFA500')
        
        # Carte d'alerte
        with st.container():
            col_icon, col_content, col_actions = st.columns([1, 8, 2])
            
            with col_icon:
                st.markdown(f"<h1 style='text-align: center; font-size: 3em;'>{icon}</h1>", 
                           unsafe_allow_html=True)
            
            with col_content:
                # En-tête
                status_badge = "🟢 RÉSOLUE" if alert.get('resolved') else "🔴 ACTIVE"
                st.markdown(f"**{status_badge}** | {alert.get('severite')} | {alert.get('type')}")
                
                # Message
                st.markdown(f"📝 {alert.get('message')}")
                
                # Détails
                details_text = f"📅 {alert.get('timestamp').strftime('%Y-%m-%d %H:%M:%S')}"
                if alert.get('valeur_mesuree'):
                    details_text += f" | 📊 Valeur: {alert.get('valeur_mesuree'):.2f}"
                if alert.get('seuil_declenche'):
                    details_text += f" | ⚠️ Seuil: {alert.get('seuil_declenche'):.2f}"
                if alert.get('ia_generated'):
                    details_text += " | 🤖 IA"
                
                st.markdown(f"<small>{details_text}</small>", unsafe_allow_html=True)
                
                # Recommandation
                if alert.get('recommandation'):
                    with st.expander("💡 Recommandation"):
                        st.write(alert.get('recommandation'))
                
                # Info résolution
                if alert.get('resolved'):
                    st.markdown(f"<small>✅ Résolue par {alert.get('resolved_by')} le {alert.get('resolved_at').strftime('%Y-%m-%d %H:%M')}</small>",
                               unsafe_allow_html=True)
            
            with col_actions:
                if not alert.get('resolved'):
                    # Bouton résoudre (ADMIN/TECH)
                    if check_permission(user, ['view', 'resolve_alerts']):
                        if st.button("✅ Résoudre", key=f"resolve_{alert.get('id')}", use_container_width=True):
                            success, message = resolve_alert(alert.get('id'), user.email)
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                
                # Bouton supprimer (ADMIN uniquement)
                if check_permission(user, ['all']):
                    if st.button("🗑️ Supprimer", key=f"delete_{alert.get('id')}", 
                                use_container_width=True, type="secondary"):
                        success, message = delete_alert(alert.get('id'))
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            st.markdown("---")

# Statistiques des alertes
if alerts:
    st.markdown("### 📈 Statistiques")
    
    # Répartition par sévérité
    import plotly.express as px
    import pandas as pd
    
    severity_counts = {}
    for alert in alerts:
        severite = alert.get('severite')
        severity_counts[severite] = severity_counts.get(severite, 0) + 1
    
    df_severity = pd.DataFrame({
        'Sévérité': list(severity_counts.keys()),
        'Nombre': list(severity_counts.values())
    })
    
    fig = px.pie(df_severity, values='Nombre', names='Sévérité',
                 title="Répartition par sévérité",
                 color='Sévérité',
                 color_discrete_map={
                     'CRITIQUE': '#DC143C',
                     'MAJEURE': '#FF4500',
                     'MINEURE': '#FFA500',
                     'WARNING': '#FFD700',
                     'INFO': '#1E90FF',
                     'PREDICTIVE': '#9370DB',
                     'SECURITY': '#8B0000'
                 })
    
    st.plotly_chart(fig, use_container_width=True)
