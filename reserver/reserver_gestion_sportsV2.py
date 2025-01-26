from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import urllib.parse

def login_and_get_csrf_token_and_cookies(login_url, username, password):
    """Connexion avec Selenium pour récupérer le token CSRF et les cookies."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        # Charger la page de connexion
        driver.get(login_url)
        print("Page de connexion chargée.")

        # Remplir le formulaire de connexion
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(username)
        driver.find_element(By.CLASS_NAME, "contact100-form-btn").click()
        time.sleep(2)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "pass"))).send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Connexion réussie.")

        # Attendre que la page soit complètement chargée
        time.sleep(5)

        # Récupérer les cookies de session
        cookies = driver.get_cookies()
        session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}
        return driver, session_cookies

    except Exception as e:
        print(f"Erreur : {e}")
        driver.quit()
        raise

def get_payment_method_id(driver, target_url):
    """Navigue vers la page cible et extrait l'attribut data-id du bouton."""
    try:
        # Aller à l'URL cible
        driver.get(target_url)
        time.sleep(5)  # Assurez-vous que la page est chargée

        # Extraire le HTML de la page avec BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Rechercher le bouton cible
        button = soup.find("button", {
            "type": "button",
            "class": "btn btn-outline-danger me-1 mb-1 ml-3 w-100 suppressPaymentMethod",
            "data-toggle": "modal",
            "data-target": "#modal_confirmation"
        })

        if button:
            data_id = button.get("data-id")
            print("Valeur data-id trouvée :", data_id)
            return data_id
        else:
            print("Bouton introuvable.")
            return None

    except Exception as e:
        print(f"Erreur : {e}")
        raise

def reserver_padel(token_csrf, session_cookies, pm_id_param, date, hour, terrains):
    """Effectuer une réservation avec Requests pour tous les terrains disponibles."""
    reservation_url = "https://padelfactory.gestion-sports.com/membre/reservation.html"
    headers = {
        "sec-ch-ua-platform": "\"Linux\"",
        "referer": "https://padelfactory.gestion-sports.com/membre/reservation.html",
        "sec-ch-ua": "\"Not?A_Brand\";v=\"99\", \"Chromium\";v=\"130\"",
        "sec-ch-ua-mobile": "?0",
        "x-requested-with": "XMLHttpRequest",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    for terrain_id in terrains:
        reservation_data = {
            "ajax": "addResa",
            "token_csrf": token_csrf,
            "date": date,
            "hour": hour,
            "duration": "90",
            "partners": "",
            "paiement": "inactif",
            "idSport": "265",
            "creaPartie": "false",
            "idCourt": str(terrain_id),
            "pay": "false",
            "token": "false",
            "saveCard": "0",
            "pmIdParam": pm_id_param,
            "foodNumber": "0",
        }

        # Encoder les données de formulaire
        encoded_data = urllib.parse.urlencode(reservation_data)

        # Effectuer la requête POST
        session = requests.Session()
        session.cookies.update(session_cookies)
        response = session.post(reservation_url, headers=headers, data=encoded_data)

        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("success"):
                print(f"Réservation réussie pour le terrain {terrain_id} :", response_json)
                return True
            else:
                print(f"Échec de la réservation pour le terrain {terrain_id} :", response_json)
        else:
            print(f"Échec de la réservation pour le terrain {terrain_id} :",
                  response.status_code, response.text)

    print("Aucune réservation n'a pu être effectuée pour les terrains disponibles.")
    return False

def main(login_url, target_url, username, password, terrains, date, hour):
    """
    Fonction principale pour gérer tout le processus de réservation de padel.
    
    Args:
        login_url (str): URL de connexion.
        target_url (str): URL pour récupérer l'ID de méthode de paiement.
        username (str): Nom d'utilisateur pour la connexion.
        password (str): Mot de passe pour la connexion.
        terrains (list): Liste des ID des terrains à tester pour la réservation.
        date (str): Date de la réservation (format : JJ/MM/AAAA).
        hour (str): Heure de la réservation (format : HH:MM).
    """
    driver = None  # Initialiser la variable driver pour garantir sa fermeture en cas d'erreur
    try:
        # Étape 1 : Connexion et récupération des cookies
        driver, cookies = login_and_get_csrf_token_and_cookies(login_url, username, password)

        # Étape 2 : Récupérer l'ID de méthode de paiement
        pm_id_param = get_payment_method_id(driver, target_url)
        if not pm_id_param:
            print("Impossible de trouver le paramètre pmIdParam.")
            return  # Terminer l'exécution si pmIdParam est introuvable

        print("ID Méthode de paiement :", pm_id_param)

        # Étape 3 : Récupérer le token CSRF
        token_csrf = driver.find_element(By.NAME, "token_csrf").get_attribute("value")
        print("Token CSRF :", token_csrf)

        # Étape 4 : Parcourir les terrains pour réserver
        success = reserver_padel(token_csrf, cookies, pm_id_param, date, hour, terrains)
        if not success:
            print("Aucune réservation n'a pu être effectuée.")

    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        # Fermer le navigateur
        if driver:
            driver.quit()


# # Définir les paramètres ici
# if __name__ == "__main__":
#     login_url = "https://padelfactory.gestion-sports.com/connexion.php"
#     target_url = "https://padelfactory.gestion-sports.com/membre/compte/moyens-paiements.html"
#     username = "bernardadrien26@gmail.com"
#     password = "Espasers64_"
#     terrains = [2519, 2520, 2521, 2522, 755, 756, 757, 758]
#     date = "28/01/2025"
#     hour = "18:00"

#     # Appeler la fonction main avec les paramètres
#     main(login_url, target_url, username, password, terrains, date, hour)
