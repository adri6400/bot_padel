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
    else:
        print("Erreur lors de la confirmation :", response.status_code, response.text)


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
        book_slot_2(
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
def main(username, password, date, start_hour):
    """
    Point d'entrée principal pour le script.
    
    :param username: Nom d'utilisateur pour la connexion.
    :param password: Mot de passe pour la connexion.
    :param date: Date pour la réservation (format YYYY-MM-DD).
    :param start_hour: Heure de début pour la réservation (format HH:MM).
    """
    token = login_and_get_token(username, password)
    if token:
        user_id, name = get_user_id(token)
        if user_id:
            book_and_confirm_slot(token, user_id, date, start_hour, name)

# if __name__ == "__main__":
#     # Exemple d'utilisation
#     username = "bernardadrien26@gmail.com"
#     password = "Espasers64_"
#     date = "2025-01-22"
#     start_hour = "15:30"
    
#     # Appel de la fonction principale
#     main(username, password, date, start_hour)