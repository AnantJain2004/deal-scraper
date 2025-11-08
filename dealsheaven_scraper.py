# dealsheaven_scraper.py
import os
import time
import requests
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
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
    # Install the chromedriver that matches installed Chrome (places binary in local folder / PATH)
    chromedriver_autoinstaller.install()

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")   # or "--headless"
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Explicitly point to chrome binary from Dockerfile
    chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")
    chrome_options.binary_location = chrome_bin

    # Let chromedriver_autoinstaller put chromedriver on PATH; Service() without path will use it
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to scrape store list dynamically from the website
# def fetch_store_list():
#     driver = init_driver()
#     driver.get("https://dealsheaven.in/stores")
#     time.sleep(2)
    
#     stores = {}
#     headers = driver.find_elements(By.TAG_NAME, "h4")
#     store_lists = driver.find_elements(By.CLASS_NAME, "store-listings")

#     for header, store_list in zip(headers, store_lists):
#         store_category = header.text.strip()
#         store_items = store_list.find_elements(By.TAG_NAME, "a")
        
#         for store in store_items:
#             store_name = store.text.strip()
#             store_link = store.get_attribute("href")
#             if store_name not in stores:
#                 stores[store_name] = store_link

#     driver.quit()
#     return stores

# Function to fetch store list without using Selenium (works on Render)
def fetch_store_list():
    url = "https://dealsheaven.in/stores"
    stores = {}

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find all store blocks (Dealsheaven groups stores under categories)
        all_links = soup.select("a[href*='/store/']")
        for link in all_links:
            name = link.get_text(strip=True)
            href = link.get("href")
            if name and href:
                if href.startswith("/"):
                    href = "https://dealsheaven.in" + href
                stores[name] = href

        if not stores:
            print("⚠️ No stores found — possibly blocked or site structure changed.")

    except Exception as e:
        print(f"Error fetching store list: {e}")

    return stores

# Function to scrape deals from the selected store
# def scrape_deals(store_url, page_count=1, search_query=None):
#     driver = init_driver()
#     products = []
    
#     for page in range(1, page_count + 1):
#         url = f"{store_url}?page={page}"
#         driver.get(url)
#         time.sleep(2)

#         product_items = driver.find_elements(By.CLASS_NAME, "product-item-detail")
#         for item in product_items:
#             try:
#                 product_name = item.find_element(By.TAG_NAME, "h3").get_attribute("title")
#                 if search_query and search_query.lower() not in product_name.lower():
#                     continue
#                 product_link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
#                 image_link = item.find_element(By.CSS_SELECTOR, ".product-img img").get_attribute("src")
#                 time_info = item.find_element(By.CLASS_NAME, "time").text
#                 mrp = item.find_element(By.CLASS_NAME, "price").text.replace("₹", "").strip()
#                 discounted_price = item.find_element(By.CLASS_NAME, "spacail-price").text.replace("₹", "").strip()
#                 discount = item.find_element(By.CLASS_NAME, "discount").text

#                 product = {
#                     'Product Name': product_name,
#                     'Product Link': product_link,
#                     'Image Link': image_link,
#                     'Time': time_info,
#                     'MRP': mrp,
#                     'Discounted Price': discounted_price,
#                     'Discount': discount
#                 }
#                 products.append(product)
#             except Exception as e:
#                 print(f"Error extracting product data: {e}")

#     driver.quit()
#     return products

def scrape_deals(store_url, page_count=1, search_query=None):
    products = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    for page in range(1, page_count + 1):
        try:
            url = f"{store_url}?page={page}"
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            product_cards = soup.select(".product-item-detail, .deal-list, .product")

            for card in product_cards:
                try:
                    title_el = card.select_one("h3, .product-title, a")
                    title = title_el.get("title") if title_el and title_el.has_attr("title") else title_el.get_text(strip=True) if title_el else "N/A"

                    if search_query and search_query.lower() not in title.lower():
                        continue

                    link_el = card.select_one("a")
                    link = link_el.get("href") if link_el else ""
                    if link.startswith("/"):
                        link = "https://dealsheaven.in" + link

                    img_el = card.select_one("img")
                    image = img_el.get("data-src") or img_el.get("src") if img_el else ""

                    price_el = card.select_one(".price, .deal-price")
                    mrp = price_el.get_text(strip=True).replace("₹", "") if price_el else "N/A"

                    sp_el = card.select_one(".spacail-price, .special-price, .discount-price")
                    discounted_price = sp_el.get_text(strip=True).replace("₹", "") if sp_el else "N/A"

                    discount_el = card.select_one(".discount, .off")
                    discount = discount_el.get_text(strip=True) if discount_el else "N/A"

                    time_el = card.select_one(".time, .posted")
                    posted_time = time_el.get_text(strip=True) if time_el else "N/A"

                    products.append({
                        "Product Name": title,
                        "Product Link": link,
                        "Image Link": image,
                        "MRP": mrp,
                        "Discounted Price": discounted_price,
                        "Discount": discount,
                        "Time": posted_time
                    })

                except Exception as e:
                    print("Error parsing product:", e)

        except Exception as e:
            print("Error fetching deals:", e)

    return products
