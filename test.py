import asyncio
from datetime import datetime, timedelta
from playwright.async_api import async_playwright

async def login_and_scrape(login_url, username, password):
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

        # Obtenir la date actuelle
        current_date = datetime.now() + timedelta(days=1)

        match_found = False
        i = 0

        while not match_found and i < 8:
            # Calculer la date à sélectionner
            target_date = current_date + timedelta(days=i)
            target_day = target_date.day

            await page.wait_for_selector('.datepicker.form-control.hasDatepicker')

            # Sélectionner une date
            await page.click('.datepicker.form-control.hasDatepicker')
            await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
            await page.click(f'.ui-state-default[data-date="{target_day}"]')

            # Sélectionner l'heure "16:00"
            await page.wait_for_selector('#heure')
            await page.select_option('#heure', '15:00')

            # Attendre la présence du bouton avec le texte "15:00"
            try:
                await page.wait_for_selector('//button[contains(text(), "15:00")]', timeout=5000)
                print("Trouvé: 15:00")

                # Cliquer sur le bouton trouvé
                await page.click('//button[contains(text(), "15:00")]')

                # Le bouton a été trouvé et cliqué, on arrête la boucle
                await asyncio.sleep(2)  # Attendre un peu pour que le DOM se stabilise

                # Attendre et cliquer sur le bouton avec data-target="#choix_paiement"
                boutons = await page.query_selector_all('button[data-target="#choix_paiement"]')
                for bouton in boutons:
                    if await bouton.is_visible():
                        await bouton.click()
                        print("BOUTON CLIQUÉ")
                        await page.wait_for_selector('btn.btn-text-primary.btn-block.addresa')
                        await page.click('btn.btn-text-primary.btn-block.addresa')
                        break

                match_found = True

                # Attendre quelques secondes pour voir le résultat
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Bouton avec le texte '15:00' non trouvé: {e}")

            # Attendre quelques secondes avant de passer à la prochaine itération si aucun bouton n'a été trouvé
            await asyncio.sleep(10)
            i += 1

        # Fermer le navigateur
        await browser.close()

login_url = 'https://rugbypark64.gestion-sports.com/connexion.php?'
username = 'bernardadrien26@gmail.com'
password = ''

async def main():
    await login_and_scrape(login_url, username, password)

asyncio.run(main())