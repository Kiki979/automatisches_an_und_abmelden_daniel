from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import http.client
import urllib
import time
import re
from datetime import datetime
import os
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

def send_push_notification(message, logout_time):
    full_message = f"{message} {logout_time}"

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    data = urllib.parse.urlencode({
        "token": os.getenv('TOKEN'), 
        "user": os.getenv('USER'),  
        "title": "Abmeldung",
        "message": full_message,
        "priority": "1",  
        "sound": "magic"  
    })
    headers = { "Content-type": "application/x-www-form-urlencoded" }
    
    conn.request("POST", "/1/messages.json", data, headers)
    response = conn.getresponse()

    if response.status == 200:
        print("Push-Nachricht erfolgreich gesendet!")
    else:
        print(f"Fehler beim Senden der Push-Nachricht: {response.status}")
        print("Antwort:", response.read().decode())

# Automatische Verwaltung von ChromeDriver
chrome_options = Options()
chrome_options.add_argument("--headless") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Öffne die Webseite
    driver.get(os.getenv('PLATTFORM'))

    # Warte, bis die Seite geladen ist
    time.sleep(2)

    # Benutzername eingeben
    username_field = driver.find_element(By.ID, 'login_username')
    username_field.send_keys(os.getenv('USERMAIL'))

    # Passwort eingeben
    password_field = driver.find_element(By.ID, 'login_passwort')
    password_field.send_keys(os.getenv('PASSWORD'))

    # Login-Button klicken
    login_button = driver.find_element(By.XPATH, '//input[@value="Einloggen"]')
    login_button.click()

    # Warte
    time.sleep(2)
    # Warte auf die Weiterleitung zur Zeiterfassung
    zeiterfassung_link = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, '//a[@href="https://portal.cc-student.com/index.php?cmd=kug"]'))
    )
    zeiterfassung_link.click()

    # Warte, bis der Button "Zeiterfassung öffnen" verfügbar ist
    zeiterfassung_button = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.NAME, 'showDialogButton'))
    )
    zeiterfassung_button.click()

    try:
        # Warte, bis der "Gehen"-Button sichtbar und klickbar ist
        gehen_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@value="Gehen"]'))
        )
        if gehen_button:
            print("Der 'Gehen'-Button ist vorhanden und klickbar.")
            driver.execute_script("arguments[0].scrollIntoView(true);", gehen_button)  # Scrolle zum Button
            driver.execute_script("arguments[0].click();", gehen_button)  # Klick per JavaScript
        else:
            print("Der 'Gehen'-Button wurde nicht gefunden.")
    except TimeoutException:
        print("Der 'Gehen'-Button konnte nicht innerhalb der Wartezeit gefunden werden.")



    time.sleep(2)
    # Warte auf den Text "Ihre letzte Buchung"
    try:
        buchung_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Ihre letzte Buchung')]"))
        )
        text_content = buchung_element.text
        print("📜 **Ausgelesener Buchungstext:**")
        print(text_content)

        # Regex zur Extraktion der Logout-Zeit (Format HH:MM:SS)
        match = re.search(r"Gehen\s*-\s*\w+,\s*\d{2}\.\d{2}\.\d{4}\s*(\d{2}:\d{2}:\d{2})", text_content)

        if match:
            logout_time = match.group(1)
            print(f"🕒 Logout-Zeit gefunden: {logout_time}")

            # Beispielaufruf der Funktion mit einer Nachricht
            send_push_notification("Erfolgreich um: ", logout_time)   
        else:
            print("Keine Logout-Zeit gefunden.")

    except TimeoutException:
        print("Fehler: Logout-Zeit nicht gefunden.")

finally:
    # Browser nach kurzer Wartezeit schließen
    time.sleep(1)
    driver.quit()
