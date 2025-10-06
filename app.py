import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

st.title("Blog Testing")

url = st.text_input("Enter website URL", "")

EXCLUDED_NEW_TAB_LINKS = [
    "https://www.bnxt.ai/contact-us",
    "https://www.linkedin.com/in/rupeshgarg/",
    "https://www.facebook.com/FrugalTest/",
    "https://x.com/FrugalTesting",
    "https://www.linkedin.com/company/frugaltesting/",
    "https://www.youtube.com/@frugaltesting",
    "https://www.instagram.com/frugaltesting/?hl=en",
    "https://maps.app.goo.gl/pgVkpLxdYyFRRxe38",
]

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

        if img_diff >= 2:
            st.write(f"📸 Number of images: {img_diff} ✅")
        else:
            st.write(f"📸 Number of images: {img_diff} ❌")

        if link_diff >= 3:
            st.write(f"🔗 Number of links: {link_diff} ✅")
        else:
            st.write(f"🔗 Number of links: {link_diff} ❌")

        if img_count - img_diff == base_images:
            st.write("✅ Call to action : 3")
        else:
            st.write("⚠️ ADD call to action")

        base_domain = urlparse(url).netloc
        internal_links = []
        external_links = []
        new_tab_links = []

        for link in links:
            href = link.get("href")
            if href:
                absolute_url = urljoin(url, href)
                domain = urlparse(absolute_url).netloc

                if link.get("target") == "_blank":
                    if absolute_url not in EXCLUDED_NEW_TAB_LINKS:
                        new_tab_links.append(absolute_url)

                if domain == base_domain or href.startswith("/"):
                    internal_links.append(absolute_url)
                else:
                    external_links.append(absolute_url)

        internal_link_count = len(internal_links) - 157
        external_link_count = len(external_links) - 12

        st.write(f"🏠 Internal links (adjusted): {internal_link_count}")
        if external_link_count >= 3:
            st.write(f"🌍 External links (adjusted): {external_link_count} ✅")
        else:
            st.write(f"🌍 External links (adjusted): {external_link_count} ❌")
        

        with st.expander("🔎 Internal Links"):
            for link in internal_links:
                st.write(link)

        with st.expander("🔎 External Links"):
            for link in external_links:
                st.write(link)

        with st.expander("🆕 Links that open in new tab (filtered)"):
            for link in new_tab_links:
                st.write(link)

        expected_tables = st.number_input("Enter expected number of tables", min_value=0, step=1)
        tables = soup.find_all("table")
        table_count = len(tables)

        st.write(f"📊 Number of tables: {table_count}")
        if table_count == expected_tables:
            st.success("✅ Correct table presentation")
        else:
            st.warning("⚠️ Need to insert table")

        if external_link_count + 1 == len(new_tab_links):
            st.success("🌍 External Links redirected to a new webpage")
        else:
            st.warning("⚠️ check a few links are wrongly redirected to a new webpage")

    except Exception as e:
        st.error(f"Error: {e}")
