import streamlit as st
import requests
import asyncio
from datetime import datetime, time

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Réservation Padel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation des variables de session
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "stop_bot" not in st.session_state:
    st.session_state.stop_bot = False

# API Endpoints
PADEL_GROUND_API_URL = "https://bot-padel.onrender.com/reserve/padel-ground"
PADEL_FACTORY_API_URL = "https://bot-padel.onrender.com/reserve/padel-factory"

# Fonction pour arrêter le bot
def stop_bot():
    st.session_state.stop_bot = True

# Titre principal
st.title("Réservation Automatique de Padel")

# Formulaire pour les identifiants
with st.form("login_form"):
    st.write("Veuillez entrer vos identifiants de connexion :")
    st.session_state.username = st.text_input("Adresse e-mail", value=st.session_state.username)
    st.session_state.password = st.text_input("Mot de passe", value=st.session_state.password, type="password")
    submitted = st.form_submit_button("Valider")
    if submitted:
        st.session_state.form_submitted = True

# Afficher les options de réservation uniquement après validation des identifiants
if st.session_state.form_submitted:
    st.write("Choisissez le(s) lieu(x), la date et l'heure pour la réservation.")
    
    # Sélection des lieux
    lieux = st.multiselect(
        "Lieu(x)",
        ["Padel Ground", "Padel Factory"],
        default=["Padel Ground", "Padel Factory"]
    )

    # Saisie de la date et de l'heure
    date = st.date_input("Date de réservation", min_value=datetime.now().date())
    time_slots = [
        str(time(hour, minute).strftime("%H:%M"))
        for hour in range(9, 23)  # Créneaux de 9h à 22h
        for minute in (0, 30)
    ]
    heure = st.selectbox("Heure de réservation", time_slots)

    # Boutons pour démarrer ou arrêter la réservation
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("Démarrer la réservation")
    with col2:
        stop_button = st.button("Annuler la réservation", on_click=stop_bot)

    # Fonction principale pour lancer la réservation via l'API
    async def main():
        st.session_state.stop_bot = False  # Réinitialiser l'état d'annulation

        while not st.session_state.stop_bot:
            success = False

            # Réservation au Padel Ground
            if "Padel Ground" in lieux:
                payload = {
                    "username": st.session_state.username,
                    "password": st.session_state.password,
                    "target_date": str(date),
                    "target_time": heure,
                }
                try:
                    response = requests.post(PADEL_GROUND_API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("Réservation réussie au Padel Ground !")
                        success = True
                    else:
                        st.warning("Échec de la réservation au Padel Ground : " + response.text)
                except Exception as e:
                    st.error(f"Erreur lors de la communication avec l'API Padel Ground : {e}")

            # Réservation au Padel Factory
            if "Padel Factory" in lieux:
                payload = {
                    "username": st.session_state.username,
                    "password": st.session_state.password,
                    "target_date": str(date),
                    "target_time": heure,
                }
                try:
                    response = requests.post(PADEL_FACTORY_API_URL, json=payload)
                    if response.status_code == 200:
                        st.success("Réservation réussie au Padel Factory !")
                        success = True
                    else:
                        st.warning("Échec de la réservation au Padel Factory : " + response.text)
                except Exception as e:
                    st.error(f"Erreur lors de la communication avec l'API Padel Factory : {e}")

            if success:
                return  # Arrêter après une réservation réussie

            st.info("Aucun créneau disponible, nouvelle tentative dans 10 secondes...")
            await asyncio.sleep(10)

        if st.session_state.stop_bot:
            st.warning("La réservation a été annulée.")

    # Lancer la réservation si le bouton "Démarrer" est cliqué
    if start_button:
        asyncio.run(main())
