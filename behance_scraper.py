# behance_scraper.py
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

# Function to initialize the WebDriver for Edge
# def init_driver():
#     edge_driver_path = r'C:\Users\Anant_Jain\OneDrive\Desktop\Infosys Springboard\Tasks\msedgedriver.exe' # path to driver
#     edge_service = Service(edge_driver_path)
#     edge_options = Options()
#     # edge_options.add_argument("--headless=new")  # optional, for no GUI
#     edge_options.add_argument("--disable-gpu")
#     return webdriver.Edge(service=edge_service, options=edge_options)

# Function to initialize the WebDriver for Chrome
def init_driver():
    """
    Initialize a headless Chrome/Chromium webdriver suitable for Streamlit Cloud.

    This function checks common Chromium binary & Chromedriver paths that Streamlit Cloud
    typically provides. If it cannot find valid binaries, it raises a RuntimeError
    with helpful instructions that will show in Streamlit logs.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Common binary and driver paths on different hosts / Streamlit images
    possible_binaries = [
        "/usr/bin/chromium-browser",  # common
        "/usr/bin/chromium",          # alternative
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome"
    ]
    possible_drivers = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        "/usr/bin/chrome-driver"
    ]

    chrome_binary = None
    for p in possible_binaries:
        if p and os.path.exists(p):
            chrome_binary = p
            break

    driver_path = None
    for d in possible_drivers:
        if d and os.path.exists(d):
            driver_path = d
            break

    # If either missing, raise a clear error (Streamlit will show this in logs)
    if not chrome_binary or not driver_path:
        missing = []
        if not chrome_binary:
            missing.append("Chromium/Chrome binary (tried: {})".format(", ".join(possible_binaries)))
        if not driver_path:
            missing.append("chromedriver binary (tried: {})".format(", ".join(possible_drivers)))

        hint = (
            "Selenium cannot find the browser/driver in the container.\n"
            "- Streamlit Cloud usually provides Chromium at /usr/bin/chromium-browser and "
            "chromedriver at /usr/bin/chromedriver.\n"
            "- If you're running locally, ensure Chrome/Chromium is installed and chromedriver "
            "matches its version, or install webdriver-manager for local testing.\n\n"
            "Missing items: " + "; ".join(missing)
        )
        raise RuntimeError(hint)

    # Set binary and driver explicitly
    chrome_options.binary_location = chrome_binary
    service = Service(driver_path)

    # Create the driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


# Function to get section URLs from the navigation menu
def get_section_urls(driver):
    driver.get("https://www.behance.net")
    wait = WebDriverWait(driver, 10)
    
    try:
        menu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".PrimaryNav-strip-Xyi .PrimaryNav-hamburgerButton-AQr")))
        menu_button.click()
        
        assets_link = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/assets')]")))
        jobs_link = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/joblist')]")))

        assets_url = assets_link.get_attribute("href")
        jobs_url = jobs_link.get_attribute("href")
        return assets_url, jobs_url
    except Exception as e:
        print("Error locating menu or links:", e)
        return None, None

# Function to scrape assets or jobs from Behance
def scrape_behance(driver, section_url, record_limit=10):
    driver.get(section_url)

    items = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    while len(items) < record_limit:
        item_elements = driver.find_elements(By.CSS_SELECTOR, '.ProjectCover-root-X6u') if 'assets' in section_url else driver.find_elements(By.CLASS_NAME, 'JobCard-jobCard-mzZ')

        for element in item_elements:
            try:
                if 'assets' in section_url:
                    title = element.find_element(By.CSS_SELECTOR, '.Title-title-lpJ').text
                    creator = element.find_element(By.CSS_SELECTOR, '.Owners-owner-EEG').text
                    link = element.find_element(By.CSS_SELECTOR, 'a.ProjectCoverNeue-coverLink-U39').get_attribute('href')
                    
                    stats = element.find_elements(By.CSS_SELECTOR, '.ProjectCover-stats-QLg .Stats-stats-Q1s span')
                    appreciations = stats[0].text if stats else 'N/A'
                    views = stats[1].text if len(stats) > 1 else 'N/A'
                    
                    items.append({
                        'Title': title,
                        'Creator': creator,
                        'Link': link,
                        'Likes': appreciations,
                        'Views': views
                    })
                else:
                    title = element.find_element(By.CLASS_NAME, 'JobCard-jobTitle-LS4').text
                    company = element.find_element(By.CLASS_NAME, 'JobCard-company-GQS').text
                    location = element.find_element(By.CLASS_NAME, 'JobCard-jobLocation-sjd').text
                    link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    description = element.find_element(By.CLASS_NAME, 'JobCard-jobDescription-SYp').text
                    time_posted = element.find_element(By.CLASS_NAME, 'JobCard-time-Cvz').text
                    
                    items.append({
                        'Title': title,
                        'Company': company,
                        'Location': location,
                        'Link': link,
                        'Description': description,
                        'Time Posted': time_posted
                    })

                if len(items) >= record_limit:
                    break
            except Exception:
                continue

        if len(items) >= record_limit:
            break

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return items[:record_limit]
