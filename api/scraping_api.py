from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time


def create_browser():
    """Créer et configurer un navigateur headless."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    service = Service()  # Crée le service pour le driver
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def login_and_scrape_rugby_park(login_url, username, password, target_date, target_time):
    driver = create_browser()
    try:
        driver.get(login_url)

        # Connexion
        driver.find_element(By.NAME, "email").send_keys(username)
        driver.find_element(By.CLASS_NAME, "contact100-form-btn").click()
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Attente pour charger
        time.sleep(5)

        # Accéder à la page de réservation
        driver.get("https://rugbypark64.gestion-sports.com/membre/reservation.html")
        Select(driver.find_element(By.ID, "sport")).select_by_value("360")

        # Sélection de la date
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        target_day = target_date_obj.day

        driver.find_element(By.CSS_SELECTOR, ".datepicker.form-control.hasDatepicker").click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".ui-state-default[data-date='{target_day}']"))
        ).click()

        # Sélection de l'heure
        Select(driver.find_element(By.ID, "heure")).select_by_value(target_time)

        # Vérification et clic sur le bouton de réservation
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{target_time}')]"))
        ).click()

        # Confirmer la réservation
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-target="#choix_paiement"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "textConfirmPartie"))
        ).click()

        return {"success": True, "message": "Réservation réussie au Rugby Park"}
    except Exception as e:
        return {"success": False, "message": f"Erreur : {e}"}
    finally:
        driver.quit()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time


def login_and_scrape_padel_factory(login_url, username, password, target_date, target_time):
    # Initialiser le navigateur (mode sans interface graphique)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Mode sans interface graphique
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    try:
        print("Démarrage du navigateur...")

        # Accéder à la page de connexion
        driver.get(login_url)
        print("Navigateur lancé et URL chargée.")

        # Remplir les champs de connexion
        driver.find_element(By.NAME, "email").send_keys(username)
        driver.find_element(By.CLASS_NAME, "contact100-form-btn").click()
        driver.find_element(By.NAME, "pass").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Connexion réussie.")

        # Attente pour le chargement de la page
        time.sleep(5)

        # Accéder à la page de réservation
        driver.get("https://padelfactory.gestion-sports.com/membre/reservation.html")
        print("Page de réservation chargée.")

        # Sélection de la date
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
        target_day = target_date_obj.day
        driver.find_element(By.CSS_SELECTOR, ".datepicker.form-control.hasDatepicker").click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f".ui-state-default[data-date='{target_day}']"))
        ).click()
        print(f"Date sélectionnée : {target_date}")

        # Sélection de l'heure
        Select(driver.find_element(By.ID, "heure")).select_by_value(target_time)
        print(f"Heure sélectionnée : {target_time}")

        # Clic sur le bouton correspondant à l'heure
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{target_time}')]"))
        ).click()
        print("Créneau sélectionné.")

        # Confirmation de la réservation
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-target="#choix_paiement"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "textConfirmPartie"))
        ).click()
        print("Réservation confirmée.")

        return {"success": True, "message": "Réservation réussie au Padel Factory"}

    except Exception as e:
        print(f"Erreur rencontrée : {e}")
        return {"success": False, "message": f"Erreur : {e}"}

    finally:
        # Fermer le navigateur
        driver.quit()
        print("Navigateur fermé.")
