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

def send_push_notification(message, login_time):
    """Sendet eine Push-Nachricht mit der Login-Zeit."""
    full_message = f"{message} {login_time}"

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    data = urllib.parse.urlencode({
        "token": os.getenv('TOKEN'), 
        "user": os.getenv('USER'),  
        "title": "Anmeldung",
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

    # # Warte auf die Weiterleitung zur Zeiterfassung
    zeiterfassung_link = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//a[contains(@href, "index.php?cmd=kug")]'))
    )
    zeiterfassung_link.click()

    # Warte, bis der Button "Zeiterfassung öffnen" verfügbar ist
    zeiterfassung_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'showDialogButton'))
    )
    zeiterfassung_button.click()

    # Warte, bis der Button "Kommen" verfügbar ist und klicke ihn an

    try: 
        kommen_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'buttonKommen'))
        )
        kommen_button.click()

    except TimeoutException:
        print("⚠️ 'Kommen'-Button nicht gefunden, versuche das Dialogfenster zu schließen...")

        try:
            # Suche nach dem Schließen-Button im Dialog
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'ui-dialog-titlebar-close'))
            )
            print("✅ Dialog-Schließen-Button gefunden, klicke darauf...")
            close_button.click()
        except (TimeoutException):
            print("❌ Konnte weder den 'Kommen'-Button noch das Dialogfenster finden!")


    # Warte auf das Element mit der letzten Buchung
    time.sleep(2)

    try:
        buchung_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Ihre letzte Buchung')]"))
        )
        text_content = buchung_element.text
        print("📜 **Ausgelesener Buchungstext:**")
        print(text_content)
        # Regex zur Extraktion der Login-Zeit (Format HH:MM:SS)
        match = re.search(r"Kommen\s*-\s*\w+,\s*\d{2}\.\d{2}\.\d{4}\s*(\d{2}:\d{2}:\d{2})", text_content)

        if match:
            login_time = match.group(1)
            print(f"🕒 Login-Zeit gefunden: {login_time}")

            # Aktuelle Zeit im Format HH:MM:SS holen
            current_time = datetime.now().strftime("%H:%M:%S")

            if login_time != current_time:
                # Beispielaufruf der Funktion mit einer Nachricht
                send_push_notification("Erfolgreich um: ", login_time)
           
        else:
            print("⚠️ Keine Login-Zeit gefunden. Überprüfe das HTML-Format.")

    except Exception as e:
        print(f"❌ Fehler beim Extrahieren der Login-Zeit: {e}")

finally:
    # Schließe den Browser nach kurzer Wartezeit
    time.sleep(1)
    driver.quit()
