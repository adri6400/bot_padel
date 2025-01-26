import streamlit as st
import requests
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
if "api_calls" not in st.session_state:
    st.session_state.api_calls = []  # Liste pour suivre les appels API

# API Endpoints
PADEL_GROUND_API_URL = "https://botpadel-production.up.railway.app/reserve/padel-ground"
PADEL_FACTORY_API_URL = "https://botpadel-production.up.railway.app/reserve/padel-factory"
STOP_API_URL = "https://botpadel-production.up.railway.app/stop"

# Fonction pour arrêter l'API
def stop_api():
    try:
        response = requests.post(STOP_API_URL)
        if response.status_code == 200:
            st.success("API arrêtée avec succès.")
        else:
            st.error(f"Erreur lors de l'arrêt de l'API : {response.text}")
    except Exception as e:
        st.error(f"Erreur lors de la communication avec l'API : {e}")

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

    # Boutons pour soumettre la demande de réservation et arrêter l'API
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Lancer la réservation"):
            for lieu in lieux:
                # Préparer les données
                payload = {
                    "username": st.session_state.username,
                    "password": st.session_state.password,
                    "target_date": str(date),
                    "target_time": heure,
                }

                # Appeler l'API correspondante
                try:
                    if lieu == "Padel Ground":
                        response = requests.post(PADEL_GROUND_API_URL, json=payload)
                        status = "Succès" if response.status_code == 200 else f"Erreur : {response.json().get('message')}"
                        st.session_state.api_calls.append({
                            "Lieu": lieu,
                            "Date": str(date),
                            "Heure": heure,
                            "Statut": status
                        })
                    elif lieu == "Padel Factory":
                        response = requests.post(PADEL_FACTORY_API_URL, json=payload)
                        status = "Succès" if response.status_code == 200 else f"Erreur : {response.json().get('message')}"
                        st.session_state.api_calls.append({
                            "Lieu": lieu,
                            "Date": str(date),
                            "Heure": heure,
                            "Statut": status
                        })
                except Exception as e:
                    st.session_state.api_calls.append({
                        "Lieu": lieu,
                        "Date": str(date),
                        "Heure": heure,
                        "Statut": f"Erreur : {e}"
                    })

    with col2:
        if st.button("Arrêter l'API"):
            stop_api()

    # Afficher les détails des appels API
    if st.session_state.api_calls:
        st.write("### Historique des appels API")
        st.table(st.session_state.api_calls)  # Afficher le tableau des appels
