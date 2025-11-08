# main_app.py
import streamlit as st
import pandas as pd
from dealsheaven_scraper import fetch_store_list, scrape_deals
from behance_scraper import get_section_urls, scrape_behance#, init_driver
import json
from io import BytesIO
import os
os.environ['WDM_LOG_LEVEL'] = '0'

# Streamlit UI
def main():
    st.set_page_config(page_title="Scraper App", layout="wide")
    st.title("🔍 Scraper App")
    st.markdown("This app scrapes data from Dealsheaven and Behance.")

    scraper_choice = st.selectbox("Choose a scraper:", ["Dealsheaven", "Behance"])

    if scraper_choice == "Dealsheaven":
        st.subheader("Dealsheaven Scraper")
        stores = fetch_store_list()
        selected_store = st.selectbox("Select Store", list(stores.keys()))
        page_count = st.number_input("Number of pages to scrape", min_value=1, value=1)
        search_query = st.text_input("Search for a product (optional)")

        if st.button("Scrape Data"):
            store_url = stores[selected_store]
            scraped_data = scrape_deals(store_url, page_count, search_query)
            if scraped_data:
                df = pd.DataFrame(scraped_data)
                st.dataframe(df)
                csv = df.to_csv(index=False)
                st.download_button(label="Download CSV", data=csv, mime="text/csv", file_name=f"{selected_store}_deals.csv")
            else:
                st.warning("No products found matching your search query in this store.")

    elif scraper_choice == "Behance":
        st.subheader("Behance Scraper")
        driver = init_driver()  # Initialize the WebDriver for Behance
        assets_url, jobs_url = get_section_urls(driver)

        section = st.selectbox("Choose section to scrape:", ["Assets", "Jobs"])
        record_limit = st.number_input("Enter the number of items to scrape:", min_value=1, max_value=100, value=10)
        search_term = st.text_input("Enter a search term to filter items (optional):")

        if st.button("🔍 Scrape Data"):
            if assets_url and jobs_url:
                section_url = assets_url if section == "Assets" else jobs_url

                with st.spinner("Scraping data from Behance..."):
                    items = scrape_behance(driver, section_url, record_limit)
                    st.success("Scraping completed!")

                driver.quit()

                if items:
                    # Apply the search filter across all fields, case-insensitive
                    if search_term:
                        filtered_items = [
                            item for item in items 
                            if any(search_term.lower() in str(value).lower() for value in item.values())
                        ]
                        st.info(f"Found {len(filtered_items)} items matching '{search_term}' in the first {record_limit} items.")
                        df = pd.DataFrame(filtered_items)
                    else:
                        df = pd.DataFrame(items)
                        st.info(f"Displaying the first {record_limit} items.")

                    if not df.empty:
                        df.insert(0, 'S.No.', range(1, len(df) + 1))
                        df['Link'] = df['Link'].apply(lambda x: f'<a href="{x}" target="_blank">View Item</a>')
                        
                        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.download_button("📥 Download as CSV", df.to_csv(index=False).encode('utf-8'), "items.csv", "text/csv")
                        with col2:
                            st.download_button("📥 Download as JSON", json.dumps(items, indent=4), "items.json", "application/json")
                        with col3:
                            excel_buffer = BytesIO()
                            df.to_excel(excel_buffer, index=False, engine='openpyxl')
                            excel_buffer.seek(0)
                            st.download_button("📥 Download as Excel", excel_buffer, "items.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        st.warning("No items to display.")
                else:
                    st.warning("No items found.")
            else:
                st.error("Failed to retrieve section URLs from Behance. Please try again.")

if __name__ == "__main__":
    main()
