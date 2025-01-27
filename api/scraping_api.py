from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import urllib.parse

# Variables globales
session_cookies = None
csrf_token = None
pm_id_param = None

def login_and_get_csrf_token_and_cookies(login_url, username, password):
    """
    Se connecter au site et récupérer les cookies et le token CSRF.
    """
    session = requests.Session()

    # Étape 1 : Charger la page de connexion pour récupérer les cookies initiaux
    response = session.get(login_url)
    if response.status_code != 200:
        raise Exception("Impossible de charger la page de connexion.")

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Récupérer le token CSRF de la page de connexion
    csrf_token_field = soup.find("input", {"name": "token_csrf"})
    if not csrf_token_field:
        raise Exception("Impossible de trouver le token CSRF sur la page de connexion.")
    csrf_token = csrf_token_field["value"]

    # Étape 2 : Soumettre le formulaire d'email
    email_payload = {
        "email": username,
        "token_csrf": csrf_token,
    }
    email_response = session.post(login_url, data=email_payload)
    if email_response.status_code != 200:
        raise Exception("Erreur lors de l'envoi de l'email.")

    # Étape 3 : Soumettre le formulaire de mot de passe
    soup = BeautifulSoup(email_response.text, "html.parser")
    csrf_token_field = soup.find("input", {"name": "token_csrf"})
    if not csrf_token_field:
        raise Exception("Impossible de trouver le token CSRF après l'envoi de l'email.")
    csrf_token = csrf_token_field["value"]

    password_payload = {
        "pass": password,
        "token_csrf": csrf_token,
    }
    password_response = session.post(login_url, data=password_payload)
    if password_response.status_code != 200:
        raise Exception("Erreur lors de la soumission du mot de passe.")

    print("Connexion réussie. Cookies et CSRF token récupérés.")
    return session.cookies, csrf_token


def get_payment_method_id(session, target_url):
    """
    Navigue vers la page cible et extrait l'attribut data-id du bouton.
    """
    response = session.get(target_url)
    if response.status_code != 200:
        raise Exception("Impossible de charger la page des méthodes de paiement.")

    soup = BeautifulSoup(response.text, "html.parser")
    button = soup.find("button", {
        "type": "button",
        "class": "btn btn-outline-danger me-1 mb-1 ml-3 w-100 suppressPaymentMethod",
        "data-toggle": "modal",
        "data-target": "#modal_confirmation",
    })
    if not button:
        raise Exception("Bouton avec data-id introuvable.")

    data_id = button["data-id"]
    print("ID de méthode de paiement récupéré :", data_id)
    return data_id


def validate_session(session, test_url):
    """
    Valide les cookies et le CSRF token en envoyant une requête test.
    """
    headers = {
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    try:
        response = session.get(test_url, headers=headers)
        if response.status_code == 200 and "reservation" in response.text:
            print("Session valide.")
            return True
        else:
            print("Session invalide.")
            return False
    except Exception as e:
        print(f"Erreur lors de la validation de la session : {e}")
        return False


def reserver_padel(session, csrf_token, pm_id_param, date, hour, terrain_id):
    """
    Tente de réserver un terrain.
    """
    reservation_url = "https://padelfactory.gestion-sports.com/membre/reservation.html"
    headers = {
        "x-requested-with": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "referer": "https://padelfactory.gestion-sports.com/membre/reservation.html",
    }

    reservation_data = {
        "ajax": "addResa",
        "token_csrf": csrf_token,
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

    try:
        response = session.post(reservation_url, headers=headers, data=reservation_data)
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("success"):
                print(f"Réservation réussie pour le terrain {terrain_id} :", response_json)
                return True
            else:
                print(f"Échec de la réservation pour le terrain {terrain_id} :", response_json)
        else:
            print(f"Erreur HTTP {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"Erreur lors de la requête : {e}")

    return False

def main_padel_factory(login_url, target_url, username, password, terrains, date, hour):
    """
    Optimisation pour réserver au Padel Factory.
    """
    global session_cookies, csrf_token, pm_id_param

    while True:
        # Valider ou renouveler la session
        if session_cookies is None or csrf_token is None or not validate_session(session_cookies, csrf_token):
            print("Récupération des nouveaux cookies et token...")
            driver, session_cookies, csrf_token = login_and_get_csrf_token_and_cookies(login_url, username, password)
            pm_id_param = get_payment_method_id(driver, target_url)
            driver.quit()

        # Parcourir les terrains pour réserver
        for terrain_id in terrains:
            if reserver_padel(csrf_token, session_cookies, pm_id_param, date, hour, terrain_id):
                print("Réservation réussie !")
                return True

        # Attendre un moment avant de réessayer
        print("Aucune réservation possible. Réessai dans 30 secondes...")
        


import requests
from datetime import datetime, timedelta


def login_and_get_token(username, password):
    """Authentifie l'utilisateur et retourne le token."""
    login_url = "https://api-v3.doinsport.club/client_login_check"
    login_data = {
        "username": username,
        "password": password,
        "club": "/clubs/9a3f194d-15c8-4fe5-b83c-51ebf3a388ce",
        "clubWhiteLabel": "/clubs/white-labels/88f2cac0-0b00-4fad-9ef0-95fdc13ee63b",
        "origin": "white_label_app"
    }
    headers = {
        "sec-ch-ua-platform": "\"Linux\"",
        "referer": "https://padelground.doinsport.club/",
        "sec-ch-ua": "\"Chromium\";v=\"129\", \"Not=A?Brand\";v=\"8\"",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "x-locale": "en"
    }

    response = requests.post(login_url, json=login_data, headers=headers)
    if response.status_code == 200:
        token = response.json().get("token")
        print("Token récupéré :", token)
        return token
    else:
        print("Erreur de connexion :", response.status_code, response.text)
        return None




def get_user_id(token):
    """Récupère l'id de l'utilisateur après connexion."""
    user_url = "https://api-v3.doinsport.club/me"
    headers = {
        "authorization": f"Bearer {token}",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua-platform": "\"Linux\"",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "x-locale": "en"
    }

    response = requests.get(user_url, headers=headers)
    print(response.json())
    if response.status_code == 200:
        user_info = response.json()
        user_id = user_info.get("id")
        name = user_info.get("lastName")
        print("User ID récupéré :", user_id)
        return user_id, name
    else:
        print("Erreur lors de la récupération de l'utilisateur :", response.status_code, response.text)
        return None


def find_slot(token, date, start_hour):
    """Cherche un créneau disponible pour une date et heure spécifiques."""
    planning_url = f"https://api-v3.doinsport.club/clubs/playgrounds/plannings/{date}"
    params = {
        "club.id": "9a3f194d-15c8-4fe5-b83c-51ebf3a388ce",
        "from": f"{start_hour}:00",
        "to": "23:59:00",
        "activities.id": "ce8c306e-224a-4f24-aa9d-6500580924dc",
        "bookingType": "unique"
    }
    headers = {
        "sec-ch-ua-platform": "\"Linux\"",
        "authorization": f"Bearer {token}",
        "referer": "https://padelground.doinsport.club/",
        "sec-ch-ua": "\"Chromium\";v=\"129\", \"Not=A?Brand\";v=\"8\"",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "accept": "application/json, text/plain, */*",
        "x-locale": "en"
    }

    response = requests.get(planning_url, headers=headers, params=params)
    if response.status_code == 200:
        planning_info = response.json()
        print("Planning récupéré.")
        for playground in planning_info.get("hydra:member", []):
            for activity in playground.get("activities", []):
                for slot in activity.get("slots", []):
                    for price in slot.get("prices", []):
                        if price["bookable"] and price["duration"] == 5400 and slot['startAt'] == start_hour :
                            return {
                                "playground_id": playground["id"],
                                "timetable_block_id": price["id"],
                                "rest_to_pay": price["pricePerParticipant"],
                                "start_time": f"{date} {slot['startAt']}:00",
                                "end_time": (
                                    datetime.strptime(f"{date} {slot['startAt']}:00", "%Y-%m-%d %H:%M:%S")
                                    + timedelta(seconds=5400)
                                ).strftime("%Y-%m-%d %H:%M:%S"),
                            }
        print("Aucun créneau disponible.")
        return None
    else:
        print("Erreur lors de la récupération du planning :", response.status_code, response.text)
        return None


def book_slot(token, user_id, playground_id, timetable_block_id, start_time, end_time, rest_to_pay, name):
    """Réserve un créneau disponible."""
    booking_url = "https://api-v3.doinsport.club/clubs/bookings"
    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua-platform": "\"Linux\"",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "x-locale": "en"
    }
    booking_data = {
        "timetableBlockPrice": f"/clubs/playgrounds/timetables/blocks/prices/{timetable_block_id}",
        "activity": "/activities/ce8c306e-224a-4f24-aa9d-6500580924dc",
        "canceled": False,
        "club": "/clubs/9a3f194d-15c8-4fe5-b83c-51ebf3a388ce",
        "startAt": start_time,
        "payments": [],
        "endAt": end_time,
        "name": name,
        "playgroundOptions": [],
        "playgrounds": [f"/clubs/playgrounds/{playground_id}"],
        "maxParticipantsCountLimit": 4,
        "userClient": f"/user-clients/{user_id}",
        "participants": [
            {
                "user": f"/user-clients/{user_id}",
                "restToPay": rest_to_pay,
                "bookingOwner": True
            }
        ],
        "pricePerParticipant": rest_to_pay,
        "paymentMethod": "on_the_spot",
        "creationOrigin": "white_label_app"
    }
    print(f"JSON {booking_data}")
    response = requests.post(booking_url, json=booking_data, headers=headers)
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        print("Erreur lors de la réservation :", response.status_code, response.text)


def book_slot_2(token, user_id, playground_id, timetable_block_id, start_time, end_time, rest_to_pay, booking_id, name):
    """Confirme la réservation existante."""
    booking_url = f"https://api-v3.doinsport.club/clubs/bookings/{booking_id}"
    headers = {
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "accept": "application/json, text/plain, */*",
        "sec-ch-ua-platform": "\"Linux\"",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "x-locale": "en"
    }
    booking_data = {
        "confirmed": True,
        "timetableBlockPrice": f"/clubs/playgrounds/timetables/blocks/prices/{timetable_block_id}",
        "activity": "/activities/ce8c306e-224a-4f24-aa9d-6500580924dc",
        "canceled": False,
        "club": "/clubs/9a3f194d-15c8-4fe5-b83c-51ebf3a388ce",
        "startAt": start_time,
        "payments": [],
        "id": booking_id,
        "endAt": end_time,
        "name": name,
        "playgroundOptions": [],
        "playgrounds": [f"/clubs/playgrounds/{playground_id}"],
        "maxParticipantsCountLimit": 4,
        "userClient": f"/user-clients/{user_id}",
        "participants": [
            {
                "user": f"/user-clients/{user_id}",
                "restToPay": rest_to_pay,
                "bookingOwner": True
            }
        ],
        "pricePerParticipant": rest_to_pay,
        "paymentMethod": "on_the_spot",
        "creationOrigin": "white_label_app"
    }

    response = requests.put(booking_url, json=booking_data, headers=headers)
    if response.status_code == 201 or response.status_code == 200:
        print("Réservation confirmée :", response.json())
        return True
    else:
        print("Erreur lors de la confirmation :", response.status_code, response.text)
        return False


def book_and_confirm_slot(token, user_id, date, start_hour, name):
    """Réserve et confirme un créneau disponible."""
    slot = find_slot(token, date, start_hour)
    if not slot:
        print("Aucun créneau disponible à réserver.")
        return

    booking_data = book_slot(
        token,
        user_id,
        slot["playground_id"],
        slot["timetable_block_id"],
        (datetime.strptime(slot["start_time"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
        (datetime.strptime(slot["end_time"], "%Y-%m-%d %H:%M:%S") - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
        slot["rest_to_pay"],
        name,
    )
    print(f"SLOT : {slot['end_time']}")
  
        
    if booking_data and booking_data.get("id"):
        booking_id = booking_data["id"]
        print("Créneau réservé. Confirmation en cours...")
        res = book_slot_2(
            token,
            user_id,
            slot["playground_id"],
            slot["timetable_block_id"],
            slot["start_time"],
            slot["end_time"],
            slot["rest_to_pay"],
            booking_id,
            name,
        )
        return res
    else : 
        return False
        
def main_padel_ground(username, password, date, start_hour):
    """
    Point d'entrée principal pour le script.
    
    :param username: Nom d'utilisateur pour la connexion.
    :param password: Mot de passe pour la connexion.
    :param date: Date pour la réservation (format YYYY-MM-DD).
    :param start_hour: Heure de début pour la réservation (format HH:MM).
    """
    token = login_and_get_token(username, password)
    res = False
    if token:
        user_id, name = get_user_id(token)
        if user_id:
            res = book_and_confirm_slot(token, user_id, date, start_hour, name)
    return res