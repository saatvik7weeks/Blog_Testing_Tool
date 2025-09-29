import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

st.title("Blog Testing")

url = st.text_input("Enter website URL", "")

if url:
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        images = soup.find_all("img")
        img_count = len(images)

        links = soup.find_all("a")
        link_count = len(links)

        base_images = 79
        base_links = 169

        img_diff = img_count - base_images
        link_diff = link_count - base_links

        st.write(f"📸 Number of images: {img_diff}")
        st.write(f"🔗 Number of links: {link_diff}")

        if img_count - img_diff == base_images:
            st.write("✅ Call to action : 3")
        else:
            st.write("⚠️ ADD call to action")

        base_domain = urlparse(url).netloc
        internal_links = []
        external_links = []

        for link in links:
            href = link.get("href")
            if href:
                absolute_url = urljoin(url, href)
                domain = urlparse(absolute_url).netloc

                if domain == base_domain or href.startswith("/"):
                    internal_links.append(absolute_url)
                else:
                    external_links.append(absolute_url)

      
        internal_link_count = len(internal_links) - 157
        external_link_count = len(external_links) - 12

        st.write(f"🏠 Internal links (adjusted): {internal_link_count}")
        st.write(f"🌍 External links (adjusted): {external_link_count}")
        
        expected_tables = st.number_input("Enter expected number of tables", min_value=0, step=1)
        tables = soup.find_all("table")
        table_count = len(tables)
        table_diff = table_count - expected_tables

        st.write(f"📊 Number of tables: {table_count}")
        if table_count == expected_tables:
            st.success("✅ Correct table presentation")
        else:
            st.warning("⚠️ Need to insert table")

    except Exception as e:
        st.error(f"Error: {e}")

    except Exception as e:
        st.error(f"Error: {e}")
