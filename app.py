import asyncio
from datetime import datetime, time
from playwright.async_api import async_playwright
import streamlit as st 

import os
import subprocess
st.set_page_config(
    page_title="Réservation Padel",  # Titre de l'onglet
    page_icon="images/favicon.png",  # Emoji ou chemin vers une image
    layout="wide",  # Optionnel : pour un layout large
    initial_sidebar_state="expanded"  # Optionnel : pour un menu latéral déplié
)

# Vérifier si les navigateurs Playwright sont installés
browsers_path = "/home/appuser/.cache/ms-playwright"
if not os.path.exists(browsers_path):
    print("Installing Playwright browsers...")
    subprocess.run(["playwright", "install", "chromium", "firefox", "webkit"], check=True)
    subprocess.run(["playwright", "install-deps"], check=True)

# Initialiser l'état de session
if "username" not in st.session_state:
    st.session_state.username = ""
if "password" not in st.session_state:
    st.session_state.password = ""
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "stop_bot" not in st.session_state:
    st.session_state.stop_bot = False
    
# Fonction pour arrêter le bot
def stop_bot():
    st.session_state.stop_bot = True

# Fonction pour la réservation au Rugby Park
async def login_and_scrape_rugby_park(login_url, username, password, target_date, target_time):
    async with async_playwright() as p:
        while True:  # Boucle pour recommencer si une erreur se produit
            try:
                # Lancer le navigateur
                browser = await p.firefox.launch(headless=True)
                page = await browser.new_page()

                # Aller à l'URL de la page de connexion
                await page.goto(login_url)

                # Entrer l'adresse e-mail et mot de passe
                await page.fill('input[name="email"]', username)
                await page.click('.contact100-form-btn')
                await page.fill('input[name="pass"]', password)
                await page.wait_for_selector('button[type="submit"]')
                await page.click('button[type="submit"]')

                # Attendre que la page se charge après la soumission
                await asyncio.sleep(5)

                # Naviguer vers la page de réservation
                await page.goto('https://rugbypark64.gestion-sports.com/membre/reservation.html')
                await page.wait_for_selector('#sport')
                await page.select_option('#sport', '360')

                # Convertir la date cible en objet datetime
                target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
                target_day = target_date_obj.day

                # Naviguer directement vers la date cible
                await page.wait_for_selector('.datepicker.form-control.hasDatepicker')
                await page.click('.datepicker.form-control.hasDatepicker')
                await asyncio.sleep(2)
                await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
                await page.click(f'.ui-state-default[data-date="{target_day}"]')

                # Sélectionner l'heure cible
                await page.wait_for_selector('#heure')
                await page.select_option('#heure', target_time)
                await asyncio.sleep(2)

                # Chercher le bouton correspondant à l'heure
                await page.wait_for_selector(f'//button[contains(text(), "{target_time}")]', timeout=5000)
                print(f"Trouvé: {target_time}")

                # Cliquer sur le bouton trouvé
                await asyncio.sleep(1)
                await page.click(f'//button[contains(text(), "{target_time}")]')

                # Cliquer sur le bouton pour confirmer la réservation
                boutons = await page.query_selector_all('button[data-target="#choix_paiement"]')
                for bouton in boutons:
                    if await bouton.is_visible():
                        await asyncio.sleep(2)
                        await bouton.click()
                        print("BOUTON CLIQUÉ")
                        await page.wait_for_selector('.textConfirmPartie')
                        await asyncio.sleep(1)
                        await page.click('.textConfirmPartie')
                        print("Réservation réussie au Rugby Park.")
                        await browser.close()
                        return True
                await browser.close()
                return False
            except Exception as e:
                print(f"Erreur rencontrée : {e}")
                # Fermer le navigateur en cas d'erreur
                if 'browser' in locals():
                    await browser.close()
                print("Reprise de la tentative...")
                await asyncio.sleep(5)  # Attendre avant de recommencer

# Fonction pour la réservation au Padel Factory
async def login_and_scrape_padel_factory(login_url, username, password, target_date, target_time):
    async with async_playwright() as p:
        while True:  # Boucle pour recommencer si une erreur se produit
            try:
                # Lancer le navigateur
                browser = await p.firefox.launch(headless=True)
                page = await browser.new_page()

                # Aller à l'URL de la page de connexion
                await page.goto(login_url)

                # Entrer l'adresse e-mail et mot de passe
                await page.fill('input[name="email"]', username)
                await page.click('.contact100-form-btn')
                await page.fill('input[name="pass"]', password)
                await page.wait_for_selector('button[type="submit"]')
                await page.click('button[type="submit"]')

                # Attendre que la page se charge après la soumission
                await asyncio.sleep(5)

                # Naviguer vers la page de réservation
                await page.goto('https://padelfactory.gestion-sports.com/membre/reservation.html')

                # Convertir la date cible en objet datetime
                target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
                target_day = target_date_obj.day

                # Naviguer directement vers la date cible
                await page.wait_for_selector('.datepicker.form-control.hasDatepicker')
                await page.click('.datepicker.form-control.hasDatepicker')
                await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
                await page.click(f'.ui-state-default[data-date="{target_day}"]')

                # Sélectionner l'heure cible
                await page.wait_for_selector('#heure')
                await page.select_option('#heure', target_time)

                # Chercher le bouton correspondant à l'heure
                await page.wait_for_selector(f'//button[contains(text(), "{target_time}")]', timeout=5000)
                print(f"Trouvé: {target_time}")

                # Trouver le bouton
                button = await page.query_selector(f'//button[contains(text(), "{target_time}")]')

                if button:
                    # Extraire la valeur de l'attribut data-target
                    data_target_value = await button.get_attribute('data-target')
                    print(f'Valeur de data-target : {data_target_value}')
                    await button.click()

                    # Cliquer sur la durée (90 min par exemple)
                    await page.get_by_role("list").get_by_text("90 min").click()

                    # Cliquer sur le bouton pour confirmer la réservation
                    boutons = await page.query_selector_all('button[data-target="#choix_paiement"]')
                    for bouton in boutons:
                        if await bouton.is_visible():
                            await bouton.click()
                            print("BOUTON CLIQUÉ")
                            await asyncio.sleep(1)
                            await page.locator("#btn_paiement_free_resa").click()
                            await page.get_by_text("Confirmer ma réservation").click()
                            print("Réservation réussie.")
                            # Fermer le navigateur en cas de succès
                            await browser.close()
                            return True
                    await browser.close()
                    return False

                else:
                    print("PAS DE CRENEAUX DISPONIBLES")
                    await browser.close()
                    return False



            except Exception as e:
                print(f"Erreur rencontrée : {e}")
                # Fermer le navigateur en cas d'erreur
                if 'browser' in locals():
                    await browser.close()
                print("Reprise de la tentative...")
                await asyncio.sleep(5)  # Attendre avant de recommencer

# Streamlit UI
st.title("Réservation Automatique")

# Formulaire pour les identifiants
with st.form("login_form"):
    st.write("Veuillez entrer vos identifiants de connexion :")
    st.session_state.username = st.text_input("Adresse e-mail", value=st.session_state.username, type="default")
    st.session_state.password = st.text_input("Mot de passe", value=st.session_state.password, type="password")
    submitted = st.form_submit_button("Valider")
    if submitted:
        st.session_state.form_submitted = True

# Afficher les options de réservation uniquement après validation des identifiants
if st.session_state.form_submitted:
    st.write("Choisissez le(s) lieu(x), la date et l'heure pour la réservation.")
    
    # Permet de sélectionner un ou plusieurs lieux
    lieux = st.multiselect(
        "Lieu(x)",
        ["Rugby Park", "Padel Factory"],
        default=["Rugby Park", "Padel Factory"]  # Par défaut, sélectionne les deux
    )
    date = st.date_input("Date de réservation")
    time_slots = [
        time(hour, minute).strftime("%H:%M")
        for hour in range(9, 23)  # De 9h à 22h inclus
        for minute in (0, 30)    # Créneaux à 00 et 30
    ]

# Ajouter un selectbox pour choisir parmi les créneaux disponibles
    heure = st.selectbox("Heure de réservation", time_slots)

        # Boutons pour démarrer ou arrêter la réservation
    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button("Démarrer la réservation")
    with col2:
        stop_button = st.button("Annuler la réservation", on_click=stop_bot)
    async def main():
        login_url_rugby_park = 'https://rugbypark64.gestion-sports.com/connexion.php?'
        login_url_factory = 'https://padelfactory.gestion-sports.com/connexion.php?'
        target_date = date
        target_time = heure

        while not st.session_state.stop_bot:
            success = False
            if "Rugby Park" in lieux:
                success = await login_and_scrape_rugby_park(
                    login_url_rugby_park,
                    st.session_state.username,
                    st.session_state.password,
                    target_date,
                    target_time
                )
            if "Padel Factory" in lieux:
                success = success or await login_and_scrape_padel_factory(
                    login_url_factory,
                    st.session_state.username,
                    st.session_state.password,
                    target_date,
                    target_time
                )

            if success:
                st.success("Réservation effectuée avec succès!")
                return
            else:
                st.write("Aucun créneau disponible pour le moment. Nouvelle tentative dans 10 secondes...")
                await asyncio.sleep(10)

        if st.session_state.stop_bot:
            st.warning("La réservation a été annulée.")
            return

    # Lancer la réservation si le bouton "Démarrer" est cliqué
    if start_button:
        st.session_state.stop_bot = False  # Réinitialiser l'état d'annulation
        asyncio.run(main())