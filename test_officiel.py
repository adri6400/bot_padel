import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import time

async def login_and_scrape_rugby_park(login_url, username, password, target_date, target_time):
    async with async_playwright() as p:
        # Lancer le navigateur
        browser = await p.firefox.launch(headless=False)
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
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
        target_day = target_date.day

        # Naviguer directement vers la date cible
        await page.wait_for_selector('.datepicker.form-control.hasDatepicker')
        await page.click('.datepicker.form-control.hasDatepicker')
        await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
        await page.click(f'.ui-state-default[data-date="{target_day}"]')

        # Sélectionner l'heure cible
        await page.wait_for_selector('#heure')
        await page.select_option('#heure', target_time)

        # Chercher le bouton correspondant à l'heure
        try:
            await page.wait_for_selector(f'//button[contains(text(), "{target_time}")]', timeout=50000)
            print(f"Trouvé: {target_time}")

            # Cliquer sur le bouton trouvé
            await page.click(f'//button[contains(text(), "{target_time}")]')

            # Cliquer sur le bouton pour confirmer la réservation
            boutons = await page.query_selector_all('button[data-target="#choix_paiement"]')
            for bouton in boutons:
                if await bouton.is_visible():
                    await bouton.click()
                    print("BOUTON CLIQUÉ")
                    await page.wait_for_selector('.textConfirmPartie')
                    await page.click('.textConfirmPartie')
                    break

            print("Réservation réussie.")
        except Exception as e:
            print(f"Bouton pour l'heure '{target_time}' non trouvé: {e}")

        # Fermer le navigateur
        await browser.close()
        
        
        
        
async def login_and_scrape_padel_factory(login_url, username, password, target_date, target_time):
    async with async_playwright() as p:
        # Lancer le navigateur
        browser = await p.firefox.launch(headless=False)
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
        #await page.wait_for_selector('#sport')
        #await page.select_option('#sport', '360')

        # Convertir la date cible en objet datetime
        target_date = datetime.strptime(target_date, "%Y-%m-%d")
        target_day = target_date.day

        # Naviguer directement vers la date cible
        await page.wait_for_selector('.datepicker.form-control.hasDatepicker')
        await page.click('.datepicker.form-control.hasDatepicker')
        await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
        await page.click(f'.ui-state-default[data-date="{target_day}"]')

        # Sélectionner l'heure cible
        await page.wait_for_selector('#heure')
        await page.select_option('#heure', target_time)

        # Chercher le bouton correspondant à l'heure
        try:
            await page.wait_for_selector(f'//button[contains(text(), "{target_time}")]', timeout=100000000)
            print(f"Trouvé: {target_time}")

                    # Trouver le bouton
            button = await page.query_selector(f'//button[contains(text(), "{target_time}")]')

            if button:
                # Extraire la valeur de l'attribut data-target
                data_target_value = await button.get_attribute('data-target')
                print(f'Valeur de data-target : {data_target_value}')
                await button.click()
                await page.get_by_role("list").get_by_text("90 min").click()
                boutons = await page.query_selector_all('button[data-target="#choix_paiement"]')
                for bouton in boutons:
                    if await bouton.is_visible():
                        await bouton.click()
                        print("BOUTON CLIQUÉ")
                        await page.locator("#btn_paiement_free_resa").click()
                        await page.get_by_text("Confirmer ma réservation").click()
                        print("Réservation réussie.")
                        break              
            else : 
                print("PAS DE CRENEAUX DISPONIBLES")

        except Exception as e:
            print(f"Bouton pour l'heure '{target_time}' non trouvé: {e}")

        # Fermer le navigateur
        await browser.close()

login_url_rugby_park = 'https://rugbypark64.gestion-sports.com/connexion.php?'
login_url_factory = 'https://padelfactory.gestion-sports.com/connexion.php?'
#FAIRE POUR LES BRUYERES ET ON EST BON 
username = 'bernardadrien26@gmail.com'
password = ''

async def main():
    # Appeler la fonction avec une date et une heure spécifiques

    
    await login_and_scrape_padel_factory(   
        login_url_factory, 
        username, 
        password, 
        target_date="2025-01-15", 
        target_time="09:00"
    )

asyncio.run(main())
