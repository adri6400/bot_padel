import streamlit as st
import requests
from datetime import datetime, time
import random
import string
def generate_unique_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))  # Génère un ID aléatoire de 8 caractères

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
# Fonction pour arrêter l'API
def stop_api(username):
    try:
        payload = {"username": username}
        response = requests.post(STOP_API_URL, json=payload)
        if response.status_code == 200:
            st.success(f"API arrêtée avec succès pour '{username}'.")
        else:
            st.error(f"Erreur lors de l'arrêt de l'API : {response.json().get('message')}")
    except Exception as e:
        st.error(f"Erreur lors de la communication avec l'API : {e}")


# Titre principal
st.title("Réservation Automatique de Padel")
# Ajouter un dictionnaire pour les raccourcis
SHORTCUTS = {
    "adri": {
        "username": "bernardadrien26@gmail.com",
        "password": "Espasers64_"
    }
}

# Formulaire pour les identifiants
with st.form("login_form"):
    st.write("Veuillez entrer vos identifiants de connexion :")
    shortcut = st.text_input("Raccourci ou adresse e-mail", value="")  # Champ pour le raccourci ou l'email
    password_input = st.text_input("Mot de passe", value="", type="password")

    # Si un raccourci est détecté, remplir automatiquement les champs
    if shortcut in SHORTCUTS:
        st.session_state.username = SHORTCUTS[shortcut]["username"]
        st.session_state.password = SHORTCUTS[shortcut]["password"]
        st.success("Raccourci détecté ! Identifiants remplis automatiquement.")
    else:
        st.session_state.username = shortcut  # Sinon, prendre l'email saisi
        st.session_state.password = password_input

    submitted = st.form_submit_button("Valider")
    if submitted:
        st.session_state.form_submitted = True
# Formulaire pour les identifiants


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
                # Générer un ID unique pour cette réservation
                reservation_id = generate_unique_id()

                # Préparer les données (sans changer le payload d'origine)
                payload = {
                    "username": st.session_state.username,
                    "password": st.session_state.password,
                    "target_date": str(date),
                    "target_time": heure,
                }

                # Appeler l'API correspondante
                try:
                    if lieu == "Padel Ground":
                        response = requests.post(PADEL_GROUND_API_URL, json=payload, timeout=3)
                        status = "Succès" if response.status_code == 200 else f"Erreur : {response.json().get('message')}"
                        st.session_state.api_calls.append({
                            "ID Réservation": reservation_id,  # L'ID unique est géré localement
                            "Lieu": lieu,
                            "Date": str(date),
                            "Heure": heure,
                            "Statut": status
                        })
                    elif lieu == "Padel Factory":
                        response = requests.post(PADEL_FACTORY_API_URL, json=payload, timeout=3)
                        status = "Succès" if response.status_code == 200 else f"Erreur : {response.json().get('message')}"
                        st.session_state.api_calls.append({
                            "ID Réservation": reservation_id,  # L'ID unique est géré localement
                            "Lieu": lieu,
                            "Date": str(date),
                            "Heure": heure,
                            "Statut": status
                        })
                except Exception as e:
                    st.session_state.api_calls.append({
                        "ID Réservation": reservation_id,  # L'ID unique est géré localement
                        "Lieu": lieu,
                        "Date": str(date),
                        "Heure": heure,
                        "Statut": f"Erreur : {e}"
                    })


    with col2:
        if st.button("Arrêter l'API"):
            stop_api(st.session_state.username)




        # Afficher les recherches en cours
    st.write("### Recherches en cours")
    response = requests.get("https://botpadel-production.up.railway.app/searches")
    searches = response.json()

    if searches:
        for index, search in enumerate(searches):  # Utiliser un index pour générer des clés uniques
            if search["username"] == st.session_state.username:
                st.write(f"**{search['lieu']}** - {search['date']} à {search['heure']}")
                # Ajouter un paramètre `key` unique pour chaque bouton
                if st.button(f"Arrêter la recherche ({search['lieu']}, {search['date']}, {search['heure']})", key=f"stop_{index}"):
                    payload = {"username": st.session_state.username, "search_id": search["id"]}
                    stop_response = requests.post("https://botpadel-production.up.railway.app/stop", json=payload)
                    if stop_response.status_code == 200:
                        st.success("Recherche arrêtée avec succès.")
                    else:
                        st.error(f"Erreur : {stop_response.json().get('message')}")
    else:
        st.write("Aucune recherche active.")