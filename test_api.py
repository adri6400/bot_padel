import requests

url = "https://bot-padel.onrender.com/reserve/padel-factory"

payload = {
    "username": "bernardadrien26@gmail.com",
    "password": "Espasers64_",
    "date": "2025-01-16",
    "time": "09:00"
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("Réponse :", response.json())
else:
    print(f"Erreur {response.status_code}: {response.text}")
