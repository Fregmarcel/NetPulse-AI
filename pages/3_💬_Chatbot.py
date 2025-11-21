"""
Page Chatbot - Assistant intelligent pour la supervision.
"""
import streamlit as st
from backend.chatbot.intent_recognizer import recognize_intent
from backend.chatbot.response_generator import generate_response
import config

st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")

# CSS personnalisé pour le style du chat
st.markdown("""
<style>
    /* Style des bulles de chat */
    .stChatMessage {
        padding: 1rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Conteneur du chat */
    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }
    
    /* Messages utilisateur - aligné à droite */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse;
        justify-content: flex-start;
        background-color: #dcf8c6;
        margin-left: auto;
        margin-right: 0;
        max-width: 70%;
        border-radius: 18px 18px 0 18px;
        padding: 0.75rem 1rem;
    }
    
    /* Messages assistant - aligné à gauche */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        flex-direction: row;
        justify-content: flex-start;
        background-color: #f0f0f0;
        margin-right: auto;
        margin-left: 0;
        max-width: 70%;
        border-radius: 18px 18px 18px 0;
        padding: 0.75rem 1rem;
    }
    
    /* Avatar utilisateur */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="chatAvatarIcon-user"] {
        order: 2;
    }
    
    /* Masquer les suggestions après le premier message */
    .suggestions-hidden {
        display: none;
    }
    
    /* Boutons de suggestions */
    .stButton button {
        border-radius: 20px;
        border: 1px solid #e5e7eb;
        background-color: white;
        color: #374151;
        font-size: 0.875rem;
        padding: 0.5rem 1rem;
        transition: all 0.2s;
    }
    
    .stButton button:hover {
        background-color: #f3f4f6;
        border-color: #d1d5db;
        transform: translateY(-2px);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Input du chat */
    .stChatInput {
        border-radius: 24px;
    }
</style>
""", unsafe_allow_html=True)

# Vérifier l'authentification
if not st.session_state.get('authenticated', False):
    st.warning("⚠️ Veuillez vous connecter")
    st.stop()

link_id = st.session_state.get('selected_link')

if not link_id:
    st.error("Aucune liaison sélectionnée")
    st.stop()

# En-tête du chat
st.markdown("""
<div style='text-align: center; padding: 1rem 0 2rem 0;'>
    <h1 style='margin: 0; font-size: 2rem;'>💬 Assistant NetPulse-AI</h1>
    <p style='color: #6B7280; margin-top: 0.5rem;'>
        Posez vos questions sur l'état de vos liaisons FH
    </p>
</div>
""", unsafe_allow_html=True)

# Initialiser l'historique du chat
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    # Message de bienvenue
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': """👋 **Bonjour !** Je suis l'assistant IA de NetPulse.

Je peux vous aider à :
- 📊 Surveiller l'état de vos liaisons FH
- 🚨 Analyser les alertes et incidents
- 📈 Consulter les métriques et KPIs
- 💡 Obtenir des recommandations XAI
- 🔮 Anticiper les dégradations

**Comment puis-je vous aider aujourd'hui ?**"""
    })

# Vérifier si l'utilisateur a commencé à interagir
user_has_interacted = len([msg for msg in st.session_state.chat_history if msg['role'] == 'user']) > 0

# Afficher les suggestions uniquement si l'utilisateur n'a pas encore interagi
if not user_has_interacted:
    st.markdown("### 💡 Questions suggérées")
    
    col1, col2, col3 = st.columns(3)
    
    suggestions = [
        ("📊 État de la liaison", "Quel est l'état de la liaison ?"),
        ("🚨 Alertes actives", "Affiche les alertes actives"),
        ("💡 Recommandations", "Quelles sont les recommandations ?"),
        ("📈 Métriques", "Donne les métriques actuelles"),
        ("🔮 Prédictions", "Prévisions pour les 2 prochaines heures"),
        ("❓ Capacités", "Qu'est-ce que tu sais faire ?")
    ]
    
    for idx, (label, message) in enumerate(suggestions):
        col = [col1, col2, col3][idx % 3]
        with col:
            if st.button(label, key=f"btn_{idx}", use_container_width=True):
                # Ajouter le message utilisateur
                st.session_state.chat_history.append({'role': 'user', 'content': message})
                
                # Traiter la question
                intent_data = recognize_intent(message)
                response = generate_response(intent_data['intent'], intent_data['entities'], link_id)
                
                st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                st.rerun()
    
    st.markdown("---")

# Conteneur pour l'historique avec scroll
if user_has_interacted:
    chat_container = st.container(height=500)
else:
    chat_container = st.container()

with chat_container:
    # Afficher l'historique
    for idx, message in enumerate(st.session_state.chat_history):
        if message['role'] == 'user':
            with st.chat_message("user", avatar="👤"):
                st.markdown(message['content'])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message['content'])
    
    # Auto-scroll vers le dernier message
    if len(st.session_state.chat_history) > 1:
        st.markdown('<div id="scroll-target"></div>', unsafe_allow_html=True)
        st.markdown("""
        <script>
            window.parent.document.querySelector('[data-testid="stVerticalBlock"]').scrollTop = 0;
        </script>
        """, unsafe_allow_html=True)

# Champ de saisie pour nouvelle question
user_input = st.chat_input("💭 Tapez votre question ici...")

if user_input:
    # Ajouter le message utilisateur
    st.session_state.chat_history.append({'role': 'user', 'content': user_input})
    
    # Reconnaître l'intention
    intent_data = recognize_intent(user_input)
    
    # Générer la réponse
    response = generate_response(intent_data['intent'], intent_data['entities'], link_id)
    
    # Ajouter la réponse
    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
    
    # Recharger pour afficher les nouveaux messages (scroll automatique vers le haut)
    st.rerun()

# Bouton pour effacer l'historique
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("🗑️ Nouvelle conversation", use_container_width=True, type="secondary"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #9CA3AF; padding: 1rem;'>
    <small>
        🤖 <strong>NetPulse-AI Assistant</strong> | Propulsé par l'Intelligence Artificielle Explicable (XAI)<br>
        💡 Toutes les analyses sont transparentes et justifiées
    </small>
</div>
""", unsafe_allow_html=True)
