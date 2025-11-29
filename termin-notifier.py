from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import os

import requests


TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=payload)


URL = "https://stuttgart.konsentas.de/form/7/?signup_new=1"


def wait_for_no_overlay(driver):
    """Wait until overlays are hidden."""
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.ID, "formpage_save"))
        )
    except:
        pass


def check_termin_availability():
    print("Starting Selenium...")

    chrome_options = Options()

    chrome_options.add_argument("--headless=new")

    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    wait = WebDriverWait(driver, 15)

    print("Opening page...")
    driver.get(URL)

    # Give the page a moment to render
    time.sleep(2)

    print("Waiting for 'Ausländerbehörde – Servicepoint' button...")

    wait_for_no_overlay(driver)

    servicepoint = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='#department-12']"))
    )

    print("Scrolling servicepoint into view...")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", servicepoint)
    time.sleep(1)

    print("Clicking servicepoint...")
    servicepoint.click()
    time.sleep(1)

    print("Waiting for service label (check_12_67)...")
    label = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='check_12_67']"))
    )

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", label)
    time.sleep(1)
    label.click()
    print("✓ Checkbox clicked")


    # Step 3: First Weiter
    print("Waiting for first Weiter...")
    weiter1 = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_formcontroll_next"))
    )

    print("Scrolling first Weiter into view...")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", weiter1)
    time.sleep(1)

    print("Clicking first Weiter...")
    weiter1.click()
    time.sleep(2)

    # Step 4: Second Weiter
    print("Waiting for second Weiter...")
    weiter2 = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn_formcontroll_next"))
    )

    print("Scrolling second Weiter into view...")
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", weiter2)
    time.sleep(1)

    print("Clicking second Weiter...")
    weiter2.click()
    time.sleep(2)

    # Step 5: Check for red alert
    print("Checking for 'Keine verfügbaren Termine' message...")
    time.sleep(2)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    try:
        alert = driver.find_element(By.CSS_SELECTOR, "div.alert.alert-danger")
        if "Keine verfügbaren Termine" in alert.text:
            print("❌ No Auslaenderbehoerde appointments available.")
            send_telegram_message("❌ No Auslaenderbehoerde appointments available time checked: " + timestamp)
            driver.quit()
            return False
    except:
        print("No red alert detected.")

    print("✅ POSSIBLE appointments available!")
    send_telegram_message("✅ POSSIBLE Auslaenderbehoerde appointments available! Time checked: " + timestamp)
    
    
    driver.quit()
    return True


if __name__ == "__main__":
    check_termin_availability()
