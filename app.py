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
SOCIAL_DOMAINS = (
    "facebook.com",
    "linkedin.com",
    "x.com",
    "twitter.com",
    "instagram.com",
    "youtube.com",
)
# Only static exclusion (Contact Us)
EXCLUDE_INTERNAL = [
    "https://www.bnxt.ai/contact-us"
]
def choose_main_article_node(container):
    children = [c for c in container.find_all(recursive=False) if getattr(c, "text", "").strip()]
    if not children:
        return container
    best = None
    best_len = 0
    for c in children:
        text_len = len(c.get_text(strip=True))
        if text_len > best_len:
            best_len = text_len
            best = c
    if best is None or best_len < 200:
        return container
    return best
if url:
    # Exclude ONLY the current blog link dynamically
    EXCLUDE_INTERNAL.append(url.rstrip("/"))
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        possible_selectors = [
            ("div", "blog-details-desc"),
            ("section", "blog-details-area"),
            ("div", "col-lg-8"),
            ("div", "blog-details-right"),
            ("div", "single-blog-details-area"),
            ("div", "blog-details"),
            ("article", None),
        ]
        content = None
        for tag, cls in possible_selectors:
            if cls:
                found = soup.find(tag, class_=cls)
            else:
                found = soup.find(tag)
            if found and len(found.get_text(strip=True)) > 200:
                content = found
                break
        if not content:
            all_divs = soup.find_all("div")
            largest = None
            max_len = 0
            for d in all_divs:
                tlen = len(d.get_text(strip=True))
                if tlen > max_len:
                    max_len = tlen
                    largest = d
            if largest and max_len > 500:
                content = largest
        if not content:
            st.error(":x: Blog content container not found — update required")
            st.stop()
        st.success(":white_check_mark: Blog content container detected")
        article_node = choose_main_article_node(content)
        # --------------------------------------------------------------------
        # :fire: UPDATED IMAGE FILTERING + STREAMLIT DISPLAY (ONLY THIS PART CHANGED)
        # --------------------------------------------------------------------
        images = []
        # Images inside <figure> (main blog images)
        for fig in article_node.find_all("figure"):
            img = fig.find("img")
            if img:
                images.append(img)
        # Images inside <p> (inline blog images)
        for p in article_node.find_all("p"):
            img = p.find("img")
            if img:
                images.append(img)
        # Remove duplicates
        unique_images = []
        seen_src = set()
        for img in images:
            src = img.get("src") or ""
            if not src:
                continue
            if src not in seen_src:
                seen_src.add(src)
                unique_images.append(img)
        st.write(f":camera_with_flash: Images Found: {len(unique_images)}")
        # Display images visually
        with st.expander("Show Blog Images"):
            if not unique_images:
                st.info("No content images found.")
            else:
                for img in unique_images:
                    src = img.get("src")
                    if src:
                        # Fix relative URLs
                        if src.startswith("//"):
                            src = "https:" + src
                        elif src.startswith("/"):
                            src = urljoin(url, src)
                        st.image(src, use_column_width=True)
                        st.caption(src)
        # --------------------------------------------------------------------
        # LINKS
        links = article_node.find_all("a")
        base_domain = urlparse(url).netloc
        internal_links = []
        external_links = []
        new_tab_links = []
        seen = set()
        for a in links:
            href = a.get("href")
            if not href:
                continue
            absolute = urljoin(url, href.split("#")[0].strip())
            if absolute in seen:
                continue
            seen.add(absolute)
            if absolute.startswith("javascript:") or absolute.startswith("mailto:"):
                continue
            domain = urlparse(absolute).netloc.lower()
            if domain == base_domain or href.startswith("/"):
                if any(absolute.startswith(x) for x in EXCLUDE_INTERNAL):
                    continue
                internal_links.append(absolute)
            else:
                external_links.append(absolute)
            if a.get("target") == "_blank":
                if absolute not in EXCLUDED_NEW_TAB_LINKS:
                    new_tab_links.append(absolute)
        total_links = len(internal_links) + len(external_links)
        st.write(f":link: Total Links: {total_links}")
        st.write(f":house: Internal links: {len(internal_links)}")
        st.write(f":earth_africa: External links: {len(external_links)}")
        with st.expander("Internal Links"):
            for l in internal_links:
                st.write(l)
        with st.expander("External Links"):
            for l in external_links:
                st.write(f"{l} :link:")
        with st.expander("New Tab Links"):
            for l in new_tab_links:
                symbol = ":x:" if l.startswith("https://www.bnxt.ai/") else ":white_check_mark:"
                st.write(f"{l} {symbol}")
        # TABLE CHECK
        tables = article_node.find_all("table")
        table_count = len(tables)
        expected_tables = st.number_input("Enter expected number of tables", min_value=0, step=1)
        st.write(f":bar_chart: Number of tables: {table_count}")
        if table_count == expected_tables:
            st.success(":white_check_mark: Correct table count")
        else:
            st.warning(":warning: Table count mismatch")
        # NEW TAB CHECK FOR EXTERNAL LINKS
        ext_set = set(external_links)
        newtab_set = set(new_tab_links)
        if ext_set and ext_set.issubset(newtab_set):
            st.success(":earth_africa: All external links open in new tab")
        else:
            st.warning(":warning: Some external links do not open in new tab")
    except Exception as e:
        st.error(f"Error: {e}")
