"""
Page Import - Import de données CSV/Excel (ADMIN uniquement).
"""
import streamlit as st
import pandas as pd
from backend.ingestion.csv_parser import parse_uploaded_file, get_file_info
from backend.ingestion.data_validator import validate_complete, get_data_quality_score
from backend.ingestion.data_loader import load_measures_to_db
from backend.security.auth import check_permission

st.set_page_config(page_title="Import", page_icon="📤", layout="wide")

# Vérifier l'authentification
if not st.session_state.get('authenticated', False):
    st.warning("⚠️ Veuillez vous connecter")
    st.stop()

user = st.session_state.user

# Vérifier les permissions ADMIN
if not check_permission(user, ['all']):
    st.error("🚫 Accès refusé - Réservé aux administrateurs")
    st.stop()

st.title("📤 Import de Données FH")

st.markdown("""
Cette page permet d'importer des mesures de liaisons micro-ondes depuis des fichiers CSV ou Excel.

**Colonnes requises :**
- `timestamp` : Date et heure de la mesure
- `link_name` : Nom de la liaison
- `rssi_dbm` : RSSI en dBm
- `snr_db` : SNR en dB
- `ber` : Bit Error Rate
- `acm_modulation` : Modulation ACM
- `latency_ms` : Latence en ms
- `packet_loss` : Perte de paquets en %
- `rainfall_mm` : Pluviométrie en mm
""")

st.markdown("---")

# Upload de fichier
st.markdown("### 📁 Sélectionner un fichier")

uploaded_file = st.file_uploader(
    "Choisissez un fichier CSV ou Excel",
    type=['csv', 'xlsx', 'xls'],
    help="Formats supportés : CSV, Excel (.xlsx, .xls)"
)

if uploaded_file is not None:
    st.success(f"✅ Fichier chargé : {uploaded_file.name}")
    
    # Parser le fichier
    with st.spinner("Parsing du fichier..."):
        df, success, message = parse_uploaded_file(uploaded_file)
    
    if not success:
        st.error(f"❌ {message}")
        st.stop()
    
    st.success(message)
    
    # Afficher les infos du fichier
    st.markdown("### 📊 Informations du fichier")
    
    file_info = get_file_info(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Lignes", file_info['nb_lignes'])
    with col2:
        st.metric("Colonnes", file_info['nb_colonnes'])
    with col3:
        st.metric("Taille", f"{file_info['memoire_mb']:.2f} MB")
    
    # Validation des données
    st.markdown("### ✅ Validation des données")
    
    with st.spinner("Validation en cours..."):
        is_valid, report = validate_complete(df)
        quality_score = get_data_quality_score(df)
    
    # Score de qualité
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.progress(quality_score / 100, text=f"Score de qualité : {quality_score:.1f}/100")
    
    with col2:
        if is_valid:
            st.success("✅ Données valides")
        else:
            st.error("❌ Erreurs détectées")
    
    with col3:
        if st.button("🔄 Revalider", use_container_width=True):
            st.rerun()
    
    # Afficher les erreurs/warnings
    if report['errors']:
        st.error("**Erreurs critiques :**")
        for error in report['errors']:
            st.write(f"• {error}")
    
    if report['warnings']:
        st.warning("**Avertissements :**")
        for warning in report['warnings']:
            st.write(f"• {warning}")
    
    # Prévisualisation
    st.markdown("### 👁️ Prévisualisation")
    
    st.dataframe(df.head(20), use_container_width=True)
    
    # Statistiques
    with st.expander("📈 Statistiques détaillées"):
        st.write(df.describe())
    
    st.markdown("---")
    
    # Import
    st.markdown("### 💾 Import dans la base de données")
    
    if not is_valid:
        st.error("⚠️ Impossible d'importer : des erreurs critiques ont été détectées")
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.info(f"📦 Prêt à importer {len(df)} ligne(s)")
        
        with col2:
            if st.button("📤 Importer", use_container_width=True, type="primary"):
                # Afficher les informations de la liaison cible
                link_name = df['link_name'].iloc[0] if 'link_name' in df.columns else None
                if link_name:
                    st.info(f"📡 Import pour la liaison: **{link_name}**")
                
                with st.spinner("Import en cours..."):
                    # Import des données
                    success, stats = load_measures_to_db(df)
                
                if success:
                    st.success("✅ Import réussi !")
                    
                    # Trouver l'ID de la liaison importée et la sélectionner
                    from backend.database.models import FHLink
                    from backend.database.connection import get_db_context
                    
                    if link_name:
                        with get_db_context() as db:
                            link = db.query(FHLink).filter(FHLink.nom == link_name).first()
                            if link:
                                # Mettre à jour la liaison sélectionnée
                                old_link = st.session_state.get('selected_link')
                                st.session_state.selected_link = link.id
                                
                                if old_link != link.id:
                                    st.info(f"🔄 Liaison active changée vers: **{link.nom}**")
                    
                    # Afficher les statistiques
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("Total", stats['total'])
                    with col2:
                        st.metric("Importées", stats['imported'])
                    with col3:
                        st.metric("Ignorées", stats['skipped'])
                    with col4:
                        st.metric("Erreurs", stats['errors'])
                    with col5:
                        st.metric("Alertes", stats.get('alerts_generated', 0))
                    
                    if stats['duplicates'] > 0:
                        st.warning(f"⚠️ {stats['duplicates']} doublon(s) ignoré(s)")
                    
                    if stats.get('alerts_generated', 0) > 0:
                        st.info(f"🚨 {stats['alerts_generated']} alerte(s) générée(s) automatiquement. Consultez la page Alertes.")
                    
                    # Message pour aller voir le Dashboard
                    st.success("✅ **Données importées !** Allez sur le 📊 Dashboard pour visualiser les nouvelles données.")
                    
                    st.balloons()
                    
                    # Forcer le rechargement de la page après 2 secondes
                    import time
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'import")
                    st.write(f"Statistiques : {stats}")

else:
    st.info("💡 Uploadez un fichier CSV ou Excel pour commencer")
    
    # Afficher un exemple de format
    st.markdown("### 📋 Exemple de format CSV")
    
    example_data = {
        'timestamp': ['2025-11-20 10:00:00', '2025-11-20 10:15:00'],
        'link_name': ['Liaison A', 'Liaison A'],
        'rssi_dbm': [-50.2, -51.3],
        'snr_db': [32.5, 31.8],
        'ber': [1.2e-9, 1.5e-9],
        'acm_modulation': ['256QAM', '256QAM'],
        'latency_ms': [2.3, 2.5],
        'packet_loss': [0.01, 0.02],
        'rainfall_mm': [0.0, 0.5]
    }
    
    example_df = pd.DataFrame(example_data)
    st.dataframe(example_df, use_container_width=True)
    
    # Bouton pour télécharger le fichier exemple
    st.markdown("### 📥 Fichier exemple")
    st.markdown("Un fichier exemple avec 100 lignes est disponible : `data/sample_fh_data.csv`")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280;'>
    <small>
    📤 L'import de données est réservé aux administrateurs.<br>
    Les données sont validées avant import pour garantir la cohérence de la base de données.
    </small>
</div>
""", unsafe_allow_html=True)
