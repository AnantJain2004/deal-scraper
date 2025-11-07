# dealsheaven_scraper.py
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

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

# Function to scrape store list dynamically from the website
def fetch_store_list():
    driver = init_driver()
    driver.get("https://dealsheaven.in/stores")
    time.sleep(2)
    
    stores = {}
    headers = driver.find_elements(By.TAG_NAME, "h4")
    store_lists = driver.find_elements(By.CLASS_NAME, "store-listings")

    for header, store_list in zip(headers, store_lists):
        store_category = header.text.strip()
        store_items = store_list.find_elements(By.TAG_NAME, "a")
        
        for store in store_items:
            store_name = store.text.strip()
            store_link = store.get_attribute("href")
            if store_name not in stores:
                stores[store_name] = store_link

    driver.quit()
    return stores

# Function to scrape deals from the selected store
def scrape_deals(store_url, page_count=1, search_query=None):
    driver = init_driver()
    products = []
    
    for page in range(1, page_count + 1):
        url = f"{store_url}?page={page}"
        driver.get(url)
        time.sleep(2)

        product_items = driver.find_elements(By.CLASS_NAME, "product-item-detail")
        for item in product_items:
            try:
                product_name = item.find_element(By.TAG_NAME, "h3").get_attribute("title")
                if search_query and search_query.lower() not in product_name.lower():
                    continue
                product_link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
                image_link = item.find_element(By.CSS_SELECTOR, ".product-img img").get_attribute("src")
                time_info = item.find_element(By.CLASS_NAME, "time").text
                mrp = item.find_element(By.CLASS_NAME, "price").text.replace("₹", "").strip()
                discounted_price = item.find_element(By.CLASS_NAME, "spacail-price").text.replace("₹", "").strip()
                discount = item.find_element(By.CLASS_NAME, "discount").text

                product = {
                    'Product Name': product_name,
                    'Product Link': product_link,
                    'Image Link': image_link,
                    'Time': time_info,
                    'MRP': mrp,
                    'Discounted Price': discounted_price,
                    'Discount': discount
                }
                products.append(product)
            except Exception as e:
                print(f"Error extracting product data: {e}")

    driver.quit()
    return products
