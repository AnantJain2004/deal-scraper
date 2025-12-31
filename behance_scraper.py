# behance_scraper.py
import os
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

# # Function to initialize the WebDriver for Edge
# # def init_driver():
# #     edge_driver_path = r'C:\Users\Anant_Jain\OneDrive\Desktop\Infosys Springboard\Tasks\msedgedriver.exe' # path to driver
# #     edge_service = Service(edge_driver_path)
# #     edge_options = Options()
# #     # edge_options.add_argument("--headless=new")  # optional, for no GUI
# #     edge_options.add_argument("--disable-gpu")
# #     return webdriver.Edge(service=edge_service, options=edge_options)

# # Function to initialize the WebDriver for Chrome
# def init_driver():
#     # Install the chromedriver that matches installed Chrome (places binary in local folder / PATH)
#     chromedriver_autoinstaller.install()

#     chrome_options = Options()
#     chrome_options.add_argument("--headless=new")   # or "--headless"
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-gpu")
#     chrome_options.add_argument("--window-size=1920,1080")

#     # Explicitly point to chrome binary from Dockerfile
#     chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")
#     chrome_options.binary_location = chrome_bin

#     # Let chromedriver_autoinstaller put chromedriver on PATH; Service() without path will use it
#     service = Service()
#     driver = webdriver.Chrome(service=service, options=chrome_options)
#     return driver

# # Function to get section URLs from the navigation menu
# def get_section_urls(driver):
#     driver.get("https://www.behance.net")
#     wait = WebDriverWait(driver, 10)
    
#     try:
#         menu_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".PrimaryNav-strip-Xyi .PrimaryNav-hamburgerButton-AQr")))
#         menu_button.click()
        
#         assets_link = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/assets')]")))
#         jobs_link = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@href, '/joblist')]")))

#         assets_url = assets_link.get_attribute("href")
#         jobs_url = jobs_link.get_attribute("href")
#         return assets_url, jobs_url
#     except Exception as e:
#         print("Error locating menu or links:", e)
#         return None, None

# # Function to scrape assets or jobs from Behance
# def scrape_behance(driver, section_url, record_limit=10):
#     driver.get(section_url)

#     items = []
#     last_height = driver.execute_script("return document.body.scrollHeight")

#     while len(items) < record_limit:
#         item_elements = driver.find_elements(By.CSS_SELECTOR, '.ProjectCover-root-X6u') if 'assets' in section_url else driver.find_elements(By.CLASS_NAME, 'JobCard-jobCard-mzZ')

#         for element in item_elements:
#             try:
#                 if 'assets' in section_url:
#                     title = element.find_element(By.CSS_SELECTOR, '.Title-title-lpJ').text
#                     creator = element.find_element(By.CSS_SELECTOR, '.Owners-owner-EEG').text
#                     link = element.find_element(By.CSS_SELECTOR, 'a.ProjectCoverNeue-coverLink-U39').get_attribute('href')
                    
#                     stats = element.find_elements(By.CSS_SELECTOR, '.ProjectCover-stats-QLg .Stats-stats-Q1s span')
#                     appreciations = stats[0].text if stats else 'N/A'
#                     views = stats[1].text if len(stats) > 1 else 'N/A'
                    
#                     items.append({
#                         'Title': title,
#                         'Creator': creator,
#                         'Link': link,
#                         'Likes': appreciations,
#                         'Views': views
#                     })
#                 else:
#                     title = element.find_element(By.CLASS_NAME, 'JobCard-jobTitle-LS4').text
#                     company = element.find_element(By.CLASS_NAME, 'JobCard-company-GQS').text
#                     location = element.find_element(By.CLASS_NAME, 'JobCard-jobLocation-sjd').text
#                     link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
#                     description = element.find_element(By.CLASS_NAME, 'JobCard-jobDescription-SYp').text
#                     time_posted = element.find_element(By.CLASS_NAME, 'JobCard-time-Cvz').text
                    
#                     items.append({
#                         'Title': title,
#                         'Company': company,
#                         'Location': location,
#                         'Link': link,
#                         'Description': description,
#                         'Time Posted': time_posted
#                     })

#                 if len(items) >= record_limit:
#                     break
#             except Exception:
#                 continue

#         if len(items) >= record_limit:
#             break

#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         new_height = driver.execute_script("return document.body.scrollHeight")
#         if new_height == last_height:
#             break
#         last_height = new_height

#     return items[:record_limit]

# behance_scraper.py (requests + BeautifulSoup version)
# import requests
# from bs4 import BeautifulSoup

# def scrape_behance(section_url, record_limit=10):
#     """
#     Scrapes Behance Jobs or Assets using requests + BeautifulSoup.
#     Works with current Behance structure (Nov 2025).
#     """
#     items = []
#     headers = {
#         "User-Agent": (
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#             "AppleWebKit/537.36 (KHTML, like Gecko) "
#             "Chrome/120.0.0.0 Safari/537.36"
#         ),
#         "Accept-Language": "en-US,en;q=0.9",
#     }

#     try:
#         response = requests.get(section_url, headers=headers, timeout=15)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.text, "html.parser")

#         # ===============================
#         # JOBS SECTION (https://www.behance.net/joblist)
#         # ===============================
#         if "job" in section_url or "joblist" in section_url:
#             job_cards = soup.select("div.JobCard-jobCard-mzZ")

#             for job in job_cards[:record_limit]:
#                 # Job link
#                 link_tag = job.select_one("a.JobCard-jobCardLink-Ywm")
#                 link = (
#                     "https://www.behance.net" + link_tag["href"]
#                     if link_tag and link_tag.get("href", "").startswith("/")
#                     else (link_tag["href"] if link_tag else "")
#                 )

#                 # Job title
#                 title_tag = job.select_one("h3.JobCard-jobTitle-LS4")
#                 title = title_tag.get_text(strip=True) if title_tag else "N/A"

#                 # Company
#                 company_tag = job.select_one("p.JobCard-company-GQS")
#                 company = company_tag.get_text(strip=True) if company_tag else "N/A"

#                 # Location
#                 location_tag = job.select_one("p.JobCard-jobLocation-sjd")
#                 location = location_tag.get_text(strip=True) if location_tag else "N/A"

#                 # Description
#                 desc_tag = job.select_one("p.JobCard-jobDescription-SYp")
#                 description = desc_tag.get_text(strip=True) if desc_tag else "N/A"

#                 # Time posted
#                 time_tag = job.select_one("span.JobCard-time-Cvz")
#                 time_posted = time_tag.get_text(strip=True) if time_tag else "N/A"

#                 items.append({
#                     "Title": title,
#                     "Company": company,
#                     "Location": location,
#                     "Description": description,
#                     "Time Posted": time_posted,
#                     "Link": link
#                 })

#         # ===============================
#         # ASSETS / PROJECTS SECTION (https://www.behance.net/search/assets)
#         # ===============================
#         else:
#             project_cards = soup.select("a.ProjectCoverNeue-coverLink-U39")

#             for a in project_cards[:record_limit]:
#                 project_link = (
#                     "https://www.behance.net" + a["href"]
#                     if a and a.get("href", "").startswith("/")
#                     else (a["href"] if a else "")
#                 )

#                 # Title
#                 title_tag = soup.find("a", {"class": "Title-title-lpJ"})
#                 title = title_tag.get_text(strip=True) if title_tag else "N/A"

#                 # Creator
#                 creator_tag = soup.find("a", {"class": "Owners-owner-EEG"})
#                 creator = creator_tag.get_text(strip=True) if creator_tag else "N/A"

#                 # Likes and Views
#                 stats_div = soup.find("div", {"class": "Stats-stats-Q1s"})
#                 if stats_div:
#                     spans = stats_div.find_all("span")
#                     likes = spans[0].get_text(strip=True) if len(spans) > 0 else "N/A"
#                     views = spans[1].get_text(strip=True) if len(spans) > 1 else "N/A"
#                 else:
#                     likes = "N/A"
#                     views = "N/A"

#                 items.append({
#                     "Title": title,
#                     "Creator": creator,
#                     "Likes": likes,
#                     "Views": views,
#                     "Link": project_link
#                 })

#     except Exception as e:
#         print(f"Error scraping Behance: {e}")

#     return items


# def get_section_urls():
#     """Returns main URLs for Assets and Jobs."""
#     assets_url = "https://www.behance.net/search/assets"
#     jobs_url = "https://www.behance.net/joblist"
#     return assets_url, jobs_url

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    chrome_bin = os.environ.get("CHROME_BIN", "/usr/bin/google-chrome")
    options.binary_location = chrome_bin

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver
# ==================================== new version

def get_section_urls():
    return (
        "https://www.behance.net/search/assets",
        "https://www.behance.net/joblist"
    )


def scrape_behance(section_url, record_limit=10):
    driver = init_driver()
    driver.get(section_url)
    time.sleep(5)

    items = []

    # ================= JOBS =================
    if "joblist" in section_url:
        cards = driver.find_elements(By.CLASS_NAME, "JobCard-jobCard-mzZ")

        for card in cards[:record_limit]:
            try:
                title = card.find_element(By.CLASS_NAME, "JobCard-jobTitle-LS4").text
                company = card.find_element(By.CLASS_NAME, "JobCard-company-GQS").text
                location = card.find_element(By.CLASS_NAME, "JobCard-jobLocation-sjd").text
                time_posted = card.find_element(By.CLASS_NAME, "JobCard-time-Cvz").text
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")

                items.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Time Posted": time_posted,
                    "Link": link
                })
            except:
                continue

    # ================= ASSETS =================
    else:
        cards = driver.find_elements(By.CLASS_NAME, "ProjectCoverNeue-coverLink-U39")

        for card in cards[:record_limit]:
            try:
                link = card.get_attribute("href")
                parent = card.find_element(By.XPATH, "./ancestor::div[contains(@class,'ProjectCover-root')]")

                title = parent.find_element(By.CLASS_NAME, "Title-title-lpJ").text
                creator = parent.find_element(By.CLASS_NAME, "Owners-owner-EEG").text

                stats = parent.find_elements(By.CSS_SELECTOR, ".Stats-stats-Q1s span")
                likes = stats[0].text if len(stats) > 0 else "N/A"
                views = stats[1].text if len(stats) > 1 else "N/A"

                items.append({
                    "Title": title,
                    "Creator": creator,
                    "Likes": likes,
                    "Views": views,
                    "Link": link
                })
            except:
                continue

    driver.quit()
    return items
