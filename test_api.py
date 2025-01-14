import requests

# URL de l'API
url = "https://bot-padel.onrender.com/reserve/padel-factory"

# Données pour la requête
payload = {
    "username": "bernardadrien26@gmail.com",
    "password": "Espasers64_",
    "date": "2025-01-16",
    "time": "09:00"
}

# Envoyer la requête POST
response = requests.post(url, json=payload)

# Vérifier la réponse
if response.status_code == 200:
    print("Réponse de l'API :", response.json())
else:
    print(f"Erreur {response.status_code}: {response.text}")
