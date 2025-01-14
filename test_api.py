import requests

url = "https://bot-padel.onrender.com/reserve/padel-factory"

payload = {
    "login_url": "https://padelfactory.gestion-sports.com/connexion.php",
    "username": "bernardadrien26@gmail.com",
    "password": "Espasers64_",
    "target_date": "2025-01-16",
    "target_time": "09:00"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Réponse :", response.json())
else:
    print(f"Erreur {response.status_code}: {response.text}")
