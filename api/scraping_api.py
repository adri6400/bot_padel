import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

async def login_and_scrape_rugby_park(login_url, username, password, target_date, target_time):
    # Fonction de scraping pour Rugby Park
    async with async_playwright() as p:
        while True:
            try:
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
                await asyncio.sleep(2)
                await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
                await page.click(f'.ui-state-default[data-date="{target_day}"]')

                await page.wait_for_selector('#heure')
                await page.select_option('#heure', target_time)
                await asyncio.sleep(2)

                button = await page.query_selector(f'//button[contains(text(), "{target_time}")]')
                if button:
                    await button.click()
                    await asyncio.sleep(1)
                    await browser.close()
                    return {"success": True, "message": "Réservation réussie au Rugby Park"}
                else:
                    await browser.close()
                    return {"success": False, "message": "Aucun créneau disponible"}
            except Exception as e:
                return {"success": False, "message": f"Erreur : {e}"}


async def login_and_scrape_padel_factory(login_url, username, password, target_date, target_time):
    # Fonction de scraping pour Padel Factory
    async with async_playwright() as p:
        while True:
            try:
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
                await asyncio.sleep(2)
                await page.wait_for_selector(f'.ui-state-default[data-date="{target_day}"]')
                await page.click(f'.ui-state-default[data-date="{target_day}"]')

                await page.wait_for_selector('#heure')
                await page.select_option('#heure', target_time)
                await asyncio.sleep(2)

                button = await page.query_selector(f'//button[contains(text(), "{target_time}")]')
                if button:
                    await button.click()
                    await asyncio.sleep(1)
                    await browser.close()
                    return {"success": True, "message": "Réservation réussie au Padel Factory"}
                else:
                    await browser.close()
                    return {"success": False, "message": "Aucun créneau disponible"}
            except Exception as e:
                return {"success": False, "message": f"Erreur : {e}"}
