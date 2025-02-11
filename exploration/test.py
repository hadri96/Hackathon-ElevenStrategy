from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.global-industrie.com/liste-des-exposants"

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

# Wait a bit for the initial JS to load
time.sleep(3)

# Repeatedly click the "Charger plus" (Load more) button until it's gone
while True:
    try:
        load_more_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Charger plus')]"))
        )
        load_more_button.click()
        time.sleep(2)  # Wait for new content to load
    except:
        print("No more 'Charger plus' button found. Moving on...")
        break

# Final HTML with everything loaded
html = driver.page_source
driver.quit()

# Parse with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")

# Extract exhibitor names
exhibitor_spans = soup.find_all("span", class_="sc-esYiGF sc-gkRewV cBbmeX dENBXG")
exhibitor_names = [span.get_text(strip=True) for span in exhibitor_spans]

# Convert to a DataFrame
df = pd.DataFrame(exhibitor_names, columns=["Exhibitor Name"])

# Save to an Excel file
df.to_excel("liste_exposants.xlsx", index=False)

print(f"Saved {len(exhibitor_names)} exhibitors to exhibitors.xlsx")
