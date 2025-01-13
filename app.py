import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import streamlit as st

import os
import subprocess
st.set_page_config(
    page_title="Réservation Padel",  # Titre de l'onglet
    page_icon="./favicon.jpeg",  # Emoji ou chemin vers une image
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

# Fonction pour la réservation au Rugby Park
async def login_and_scrape_rugby_park(login_url, username, password, target_date, target_time):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(login_url)
        await page.fill('input[name="email"]', username)
        await page.click('.contact100-form-btn')
        await page.fill('input[name="pass"]', password)
        await page.wait_for_selector('button[type="submit"]')
        await page.click('button[type="submit"]')
        await asyncio.sleep(5)
        await page.goto('https://rugbypark64.gestion-sports.com/membre/reservation.html')
        await page.wait_for_selector('#sport')
        await page.select_option('#sport', '360')
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        target_day = target_date_obj.day
        await page.wait_for_selector('.datepicker.form-control.hasDatepicker')
        await page.click('.datepicker.form-control.hasDatepicker')
        await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
        await page.click(f'.ui-state-default[data-date="{target_day}"]')
        await page.wait_for_selector('#heure')
        await page.select_option('#heure', target_time)
        await asyncio.sleep(10)
        try:
            await page.wait_for_selector(f'//button[contains(text(), "{target_time}")]', timeout=5000)
            button = await page.query_selector(f'//button[contains(text(), "{target_time}")]')
            if button:
                await button.click()
                print("Réservation réussie au Rugby Park.")
                await browser.close()
                return True
        except Exception as e:
            print(f"Aucun créneau disponible au Rugby Park : {e}")
        await browser.close()
        return False

# Fonction pour la réservation au Padel Factory
async def login_and_scrape_padel_factory(login_url, username, password, target_date, target_time):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(login_url)
        await page.fill('input[name="email"]', username)
        await page.click('.contact100-form-btn')
        await page.fill('input[name="pass"]', password)
        await page.wait_for_selector('button[type="submit"]')
        await page.click('button[type="submit"]')
        await asyncio.sleep(5)
        await page.goto('https://padelfactory.gestion-sports.com/membre/reservation.html')
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        target_day = target_date_obj.day
        await page.wait_for_selector('.datepicker.form-control.hasDatepicker')
        await page.click('.datepicker.form-control.hasDatepicker')
        await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
        await page.click(f'.ui-state-default[data-date="{target_day}"]')
        await page.wait_for_selector('#heure')
        await page.select_option('#heure', target_time)
        await asyncio.sleep(10)
        try:
            await page.wait_for_selector(f'//button[contains(text(), "{target_time}")]', timeout=5000)
            button = await page.query_selector(f'//button[contains(text(), "{target_time}")]')
            if button:
                await button.click()
                print("Réservation réussie au Padel Factory.")
                await browser.close()
                return True
        except Exception as e:
            print(f"Aucun créneau disponible au Padel Factory : {e}")
        await browser.close()
        return False

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
    st.write("Choisissez le lieu, la date et l'heure pour la réservation.")
    lieu = st.selectbox("Lieu", ["Rugby Park", "Padel Factory", "Les deux"])
    date = st.date_input("Date de réservation")
    heure = st.time_input("Heure de réservation")

    # Bouton pour démarrer la réservation
    if st.button("Démarrer la réservation"):
        st.write("Recherche de créneaux en cours...")

        # Fonction principale pour gérer les réservations
        async def main():
            success = False  # Déclarer la variable localement
            login_url_rugby_park = 'https://rugbypark64.gestion-sports.com/connexion.php?'
            login_url_factory = 'https://padelfactory.gestion-sports.com/connexion.php?'
            target_date = date.strftime("%Y-%m-%d")
            target_time = heure.strftime("%H:%M") 

            while not success:
                if lieu == "Rugby Park" or lieu == "Les deux":
                    success = await login_and_scrape_rugby_park(login_url_rugby_park, st.session_state.username, st.session_state.password, target_date, target_time)
                if lieu == "Padel Factory" or lieu == "Les deux":
                    success = success or await login_and_scrape_padel_factory(login_url_factory, st.session_state.username, st.session_state.password, target_date, target_time)

                if not success:
                    st.write("Aucun créneau disponible pour le moment. Nouvelle tentative dans 10 secondes...")
                    await asyncio.sleep(10)

            return success

        success = asyncio.run(main())
        if success:
            st.success("Réservation effectuée avec succès!")
