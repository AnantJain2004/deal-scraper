# # behance_scraper.py
# import os
# import time
# import chromedriver_autoinstaller
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.edge.service import Service
# from selenium.webdriver.edge.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support import expected_conditions as EC

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
import time
import requests
from bs4 import BeautifulSoup

# Common headers to mimic a real browser
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Return canonical section URLs for Behance
def get_section_urls():
    """
    Returns (assets_url, jobs_url).
    These are stable / canonical pages we can scrape using requests.
    """
    assets_url = "https://www.behance.net/search?content=projects"   # lists projects/assets
    jobs_url = "https://www.behance.net/joblist"                     # jobs listing
    return assets_url, jobs_url


def parse_project_card(a_tag):
    """
    Given an <a> tag that likely points to a project, return a dict with
    Title, Creator (if available), Link, Likes/Views (best-effort).
    This is best-effort — Behance HTML and classes change frequently.
    """
    link = a_tag.get("href")
    if not link:
        return None
    if link.startswith("/"):
        link = "https://www.behance.net" + link

    # Title attempt: many project links include a nested img alt or a span with title
    title = a_tag.get("aria-label") or a_tag.get("title") or ""
    if not title:
        # try to find text child or nested elements
        title_el = a_tag.select_one("img[alt]") or a_tag.select_one("h3") or a_tag.select_one("div")
        if title_el:
            title = title_el.get("alt") if title_el.name == "img" else title_el.get_text(strip=True)

    # Creator is often present in a sibling or nested element
    creator = ""
    owner_el = a_tag.select_one(".ProjectCover-owner, .Owner") or a_tag.find_next("a", {"href": lambda x: x and "/people/" in x})
    if owner_el:
        creator = owner_el.get_text(strip=True)

    # Stats (likes / views) - best-effort
    likes = "N/A"
    views = "N/A"
    stat_spans = a_tag.select(".stats span") or a_tag.select(".ProjectCover-stats span")
    if stat_spans:
        try:
            likes = stat_spans[0].get_text(strip=True)
            if len(stat_spans) > 1:
                views = stat_spans[1].get_text(strip=True)
        except Exception:
            pass

    return {
        "Title": title or "(no title)",
        "Creator": creator or "N/A",
        "Link": link,
        "Likes": likes,
        "Views": views,
    }


def scrape_behance(section_url, record_limit=10):
    """
    Scrape Behance section (assets/projects or jobs) using requests+BeautifulSoup.
    - section_url: URL returned from get_section_urls()
    - record_limit: number of items to return
    Returns a list of dicts (structure differs slightly for assets vs jobs).
    """
    headers = DEFAULT_HEADERS.copy()
    items = []

    try:
        # fetch first page
        resp = requests.get(section_url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Distinguish between assets/projects and jobs by URL/content
        if "job" in section_url or "joblist" in section_url:
            # Jobs: look for links that include '/job/' or job-card containers
            # Best-effort selectors
            job_cards = soup.select("a[href*='/job/'], .JobCard, .job-card, a[href*='joblist']")
            seen = set()
            for el in job_cards:
                if len(items) >= record_limit:
                    break
                # find anchor and text
                a = el if el.name == "a" else el.select_one("a") or el
                href = a.get("href") if a else None
                if not href:
                    continue
                if href.startswith("/"):
                    href = "https://www.behance.net" + href
                # title/company/location: try best-effort
                title = (a.get_text(strip=True) or "").split("\n")[0]
                # try more precise fields if available
                company = el.select_one(".JobCard-company, .company") 
                company_text = company.get_text(strip=True) if company else ""
                location_el = el.select_one(".JobCard-jobLocation, .location")
                location_text = location_el.get_text(strip=True) if location_el else ""
                description_el = el.select_one(".JobCard-jobDescription, .description")
                description = description_el.get_text(strip=True) if description_el else ""

                item = {
                    "Title": title or "Job listing",
                    "Company": company_text or "N/A",
                    "Location": location_text or "N/A",
                    "Link": href,
                    "Description": description or "N/A"
                }
                key = href
                if key not in seen:
                    items.append(item)
                    seen.add(key)

            return items[:record_limit]

        else:
            # Assets/projects page
            # Try to find project anchors. Behance search pages often contain anchors with '/gallery' or '/projects'
            project_anchors = soup.select("a[href*='/gallery/'], a[href*='/projects/'], a[data-project-id]")
            seen = set()
            for a in project_anchors:
                if len(items) >= record_limit:
                    break
                parsed = parse_project_card(a)
                if not parsed:
                    continue
                key = parsed["Link"]
                if key not in seen:
                    items.append(parsed)
                    seen.add(key)

            # If none found, fallback: try to parse generic project tiles
            if not items:
                tiles = soup.select(".ProjectCover-root, .project-cover, .project-tile a")
                for a in tiles:
                    if len(items) >= record_limit:
                        break
                    anchor = a if a.name == "a" else a.select_one("a")
                    if not anchor:
                        continue
                    parsed = parse_project_card(anchor)
                    if parsed and parsed["Link"] not in seen:
                        items.append(parsed)
                        seen.add(parsed["Link"])

            return items[:record_limit]

    except requests.HTTPError as he:
        print("HTTP error while scraping Behance:", he)
    except Exception as e:
        print("Error scraping Behance:", e)

    return items
