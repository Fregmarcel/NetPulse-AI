"""
NetPulse-AI - Application principale Streamlit.
Point d'entrée de la plateforme de supervision des liaisons micro-ondes FH.
"""
import streamlit as st
from backend.security.auth import authenticate_user
from backend.database.models import FHLink
from backend.database.connection import get_db_context
import config

# Configuration de la page (DOIT être la première commande Streamlit)
st.set_page_config(
    page_title="NetPulse-AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un style professionnel
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #3B82F6 0%, #1E3A8A 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: 600;
    }
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .status-normal {
        color: #10B981;
        font-weight: bold;
    }
    .status-degraded {
        color: #F59E0B;
        font-weight: bold;
    }
    .status-critique {
        color: #EF4444;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialise les variables de session."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'selected_link' not in st.session_state:
        st.session_state.selected_link = None


def get_available_links():
    """Récupère la liste des liaisons FH disponibles."""
    with get_db_context() as db:
        links = db.query(FHLink).filter(FHLink.actif == True).all()
        # Extraire les données pendant que la session est active
        links_data = []
        for link in links:
            links_data.append({
                'id': link.id,
                'nom': link.nom,
                'site_a': link.site_a,
                'site_b': link.site_b,
                'frequence_ghz': link.frequence_ghz,
                'distance_km': link.distance_km,
                'actif': link.actif
            })
        return links_data


def login_page():
    """Affiche la page de connexion."""
    st.markdown('<div class="main-header">📡 NetPulse-AI</div>', unsafe_allow_html=True)
    st.markdown("### Plateforme de Supervision Intelligente des Liaisons Micro-ondes FH")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 🔐 Connexion")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="admin@netpulse.ai")
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="Votre mot de passe")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("Se connecter", use_container_width=True)
            with col_btn2:
                if st.form_submit_button("Aide", use_container_width=True):
                    st.info("""
                    **Identifiants de test :**
                    
                    👨‍💼 Admin: `admin@netpulse.ai` / `admin123`
                    
                    👨‍🔧 Tech: `tech@netpulse.ai` / `tech123`
                    
                    👤 Guest: `guest@netpulse.ai` / `guest123`
                    """)
            
            if submit:
                if email and password:
                    user_data, success, message = authenticate_user(email, password, "127.0.0.1")
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Veuillez remplir tous les champs")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #6B7280;'>
            <small>NetPulse-AI v{config.APP_VERSION} | © 2025</small>
        </div>
        """, unsafe_allow_html=True)


def main_app():
    """Application principale après authentification."""
    user = st.session_state.user
    user_role = user['role'].value if hasattr(user['role'], 'value') else user['role']
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📡 NetPulse-AI")
        st.markdown(f"👤 **{user['nom_complet'] or user['email']}**")
        
        # Badge de rôle avec couleur
        role_badges = {
            'ADMIN': '🔴 **Administrateur**',
            'TECH': '🟡 **Technicien FH**',
            'GUEST': '🟢 **Invité**'
        }
        st.markdown(role_badges.get(user_role, f"*{user_role}*"))
        
        # Permissions selon le rôle
        if user_role == 'ADMIN':
            st.caption("✅ Accès complet + Gestion utilisateurs")
        elif user_role == 'TECH':
            st.caption("✅ Supervision + Analyse + Chatbot")
        else:
            st.caption("📖 Consultation uniquement")
        
        st.markdown("---")
        
        # Sélection de la liaison FH
        st.markdown("### 🔗 Liaison active")
        links = get_available_links()
        
        if links:
            link_names = [f"{link['nom']}" for link in links]
            link_ids = [link['id'] for link in links]
            
            # Initialiser la sélection
            if st.session_state.selected_link is None:
                st.session_state.selected_link = link_ids[0]
            
            selected_index = link_ids.index(st.session_state.selected_link) if st.session_state.selected_link in link_ids else 0
            
            selected_name = st.selectbox(
                "Sélectionnez une liaison",
                options=link_names,
                index=selected_index,
                label_visibility="collapsed",
                key="link_selector"
            )
            
            # Mettre à jour la liaison sélectionnée
            selected_idx = link_names.index(selected_name)
            new_link_id = link_ids[selected_idx]
            
            # Forcer le rechargement si la liaison change
            if st.session_state.selected_link != new_link_id:
                st.session_state.selected_link = new_link_id
                st.rerun()
            
            # Afficher les détails de la liaison
            selected_link = links[selected_idx]
            st.markdown(f"""
            **Sites:**
            - 📍 {selected_link['site_a']}
            - 📍 {selected_link['site_b']}
            
            **Caractéristiques:**
            - 📡 Fréquence: {selected_link['frequence_ghz']} GHz
            - 📏 Distance: {selected_link['distance_km']} km
            """)
        else:
            st.warning("Aucune liaison disponible")
        
        st.markdown("---")
        
        # Navigation
        st.markdown("### 📚 Navigation")
        st.page_link("app.py", label="🏠 Accueil", icon="🏠")
        st.page_link("pages/1_📊_Dashboard.py", label="📊 Dashboard", icon="📊")
        st.page_link("pages/2_🚨_Alertes.py", label="🚨 Alertes", icon="🚨")
        st.page_link("pages/3_💬_Chatbot.py", label="💬 Chatbot", icon="💬")
        
        # Vérifier le rôle pour afficher Import
        user_role = user['role'].value if hasattr(user['role'], 'value') else user['role']
        if user_role == 'ADMIN':
            st.page_link("pages/4_📤_Import.py", label="📤 Import", icon="📤")
        
        st.markdown("---")
        
        # Déconnexion
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.selected_link = None
            st.success("Déconnexion réussie")
            st.rerun()
    
    # Contenu principal
    st.markdown('<div class="main-header">📡 NetPulse-AI - Accueil</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📊 Dashboard
        
        Visualisez en temps réel les métriques de vos liaisons FH :
        - Graphiques RSSI, SNR, BER
        - Indicateurs de performance
        - Analyse de tendances
        
        [Accéder au Dashboard →](./1_📊_Dashboard)
        """)
    
    with col2:
        st.markdown("""
        ### 🚨 Alertes
        
        Surveillez et gérez les alertes système :
        - Alertes actives et historique
        - Filtrage par sévérité
        - Actions de résolution
        
        [Gérer les alertes →](./2_🚨_Alertes)
        """)
    
    with col3:
        st.markdown("""
        ### 💬 Chatbot IA
        
        Interrogez l'assistant intelligent :
        - État des liaisons
        - Recommandations
        - Prédictions
        
        [Ouvrir le chatbot →](./3_💬_Chatbot)
        """)
    
    st.markdown("---")
    
    # Statistiques rapides
    st.markdown("### 📈 Vue d'ensemble")
    
    from backend.analytics.kpi_calculator import get_latest_kpis
    from backend.alerts.alert_engine import get_active_alerts
    
    if st.session_state.selected_link:
        kpis = get_latest_kpis(st.session_state.selected_link)
        alerts = get_active_alerts(st.session_state.selected_link)
        
        if kpis:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                etat_class = f"status-{kpis['etat_global'].lower()}"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>État Global</h4>
                    <p class="{etat_class}">{kpis['etat_global']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.metric("RSSI", f"{kpis['rssi_dbm']:.1f} dBm")
            
            with col3:
                st.metric("SNR", f"{kpis['snr_db']:.1f} dB")
            
            with col4:
                st.metric("Alertes actives", len(alerts))
        else:
            st.info("💡 Aucune donnée disponible. Importez des mesures depuis la page Import.")
    
    st.markdown("---")
    
    # Informations système
    st.markdown("### ℹ️ À propos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        **Version:** {config.APP_VERSION}
        
        **Environnement:** {config.ENVIRONMENT}
        
        **Stack technique:**
        - Python / Streamlit
        - SQLAlchemy / SQLite
        - Scikit-learn (IA)
        - Plotly (Graphiques)
        """)
    
    with col2:
        st.markdown("""
        **Fonctionnalités:**
        - ✅ Supervision en temps réel
        - ✅ Alertes intelligentes
        - ✅ Prédictions IA
        - ✅ Analyse de tendances
        - ✅ Chatbot assistant
        - ✅ Import de données
        """)


def main():
    """Point d'entrée principal."""
    init_session_state()
    
    if st.session_state.authenticated:
        main_app()
    else:
        login_page()


if __name__ == "__main__":
    main()
