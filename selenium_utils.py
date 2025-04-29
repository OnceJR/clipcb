from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def get_m3u8_url(page_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(page_url)
        time.sleep(5)  # Esperar que cargue

        # Captura tráfico de red para encontrar .m3u8
        performance_entries = driver.execute_script(
            "return window.performance.getEntries();"
        )

        for entry in performance_entries:
            if ".m3u8" in entry["name"]:
                return entry["name"]
    finally:
        driver.quit()

    return None
