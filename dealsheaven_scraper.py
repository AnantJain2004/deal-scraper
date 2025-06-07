# dealsheaven_scraper.py
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Function to initialize the WebDriver
def init_driver():
    edge_service = Service(EdgeChromiumDriverManager().install())
    edge_options = Options()
    return webdriver.Edge(service=edge_service, options=edge_options)

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
