import base64
import os
from pathlib import Path

import requests
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.markdown(
    """
    <style>
    :root {
        --primary-color: #ffa500;
        --background: #f5f5dc;
        --secondary-background: #f5f5dc;
        --text-color: #5a5a5a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Guard optional third-party imports so the app still starts in a minimal environment.
try:
    from streamlit_option_menu import option_menu
except Exception:  # pragma: no cover
    option_menu = None

try:
    from streamlit.components.v1 import html
except Exception:  # pragma: no cover
    html = None

try:
    from st_on_hover_tabs import on_hover_tabs
except Exception:  # pragma: no cover
    on_hover_tabs = None

try:
    from streamlit_lottie import st_lottie
except Exception:  # pragma: no cover
    st_lottie = None

try:
    import streamlit_analytics
except Exception:  # pragma: no cover
    streamlit_analytics = None

try:
    from streamlit_extras.mention import mention
except Exception:  # pragma: no cover
    mention = None

try:
    from streamlit_extras.app_logo import add_logo
except Exception:  # pragma: no cover
    add_logo = None

try:
    from streamlit_extras.echo_expander import echo_expander
except Exception:  # pragma: no cover
    echo_expander = None

st.set_page_config(page_title="Harry Chang", page_icon="desktop_computer", layout="wide", initial_sidebar_state="auto")

ROOT = Path(__file__).resolve().parent

# CSS fallback: load a bundled file if present, otherwise use a built-in style block.
def load_local_css(file_name: str):
    css_path = ROOT / file_name
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <style>
            html, body, [data-testid="stAppViewContainer"] {
                margin: 0 !important;
                padding: 0 !important;
                background: #f3efe7 !important;
            }
            [data-testid="stMain"] {
                background: #f7f4ef !important;
            }
            [data-testid="stSidebar"] {
                background: #e9e4d8 !important;
            }
            .stButton > button {
                width: 100%;
                justify-content: flex-start;
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            h1, h2, h3 {
                color: #2f2f2f;
            }
            p, li {
                color: #3c3c3c;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


# Graceful asset loading for the original portfolio code.
def build_placeholder_image(text: str, bg=(233, 228, 216), fg=(36, 36, 36), width=800, height=600):
    img = Image.new("RGB", (width, height), color=bg)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 48)
    except Exception:
        font = ImageFont.load_default()
    draw.text((50, 260), text, fill=fg, font=font)
    return img


def safe_open_image(path: str | os.PathLike, fallback_text: str = "Image"):
    path = Path(path)
    if path.exists():
        try:
            return Image.open(path)
        except Exception:
            pass
    return build_placeholder_image(fallback_text)


# Accept both original paths and a repo-local fallback.
def safe_pdf(path: str | os.PathLike):
    if Path(path).exists():
        return str(path)
    return None


# Keep the original layout hooks but make them harmless if the files are absent.
load_local_css("style.css")
if (ROOT / "style").exists():
    load_local_css("style/style.css")


def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


# PDFs and resume links.
def show_pdf(file_path):
    pdf_path = safe_pdf(file_path)
    if pdf_path is None:
        st.info("PDF file is not available in this workspace, so the file preview is unavailable.")
        return
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def pdf_link(pdf_url, link_text="Click here to view PDF"):
    return f'<a href="{pdf_url}" target="_blank">{link_text}</a>'


def social_icons(width=24, height=24, **kwargs):
    icon_template = '''
    <a href="{url}" target="_blank" style="margin-right: 18px; display: inline-block;">
        <img src="{icon_src}" alt="{alt_text}" width="{width}" height="{height}">
    </a>
    '''
    icons_html = ""
    for name, url in kwargs.items():
        icon_src = {
            "youtube": "https://img.icons8.com/ios-filled/100/ff8c00/youtube-play.png",
            "linkedin": "https://img.icons8.com/ios-filled/100/ff8c00/linkedin.png",
            "github": "https://img.icons8.com/ios-filled/100/ff8c00/github--v2.png",
            "wordpress": "https://img.icons8.com/ios-filled/100/ff8c00/wordpress--v1.png",
            "email": "https://img.icons8.com/ios-filled/100/ff8c00/filled-message.png",
        }.get(name.lower())
        if icon_src:
            icons_html += icon_template.format(url=url, icon_src=icon_src, alt_text=name.capitalize(), width=width, height=height)
    return icons_html


# Use a placeholder avatar if the local photo isn't present.
img_lh = safe_open_image(ROOT / "images" / "lh.jpg", "Harry Chang")
img_utown = safe_open_image(ROOT / "images" / "utown.JPG", "About Me")
img_ifg = safe_open_image(ROOT / "images" / "ifg.jpg", "Contact")
img_quest = safe_open_image(ROOT / "images" / "questlogo.jpg", "Experience")
img_saf = safe_open_image(ROOT / "images" / "saf.jpg", "Experience")
img_nus = safe_open_image(ROOT / "images" / "nus.jpeg", "Education")
img_dsa = safe_open_image(ROOT / "images" / "dsa.jpg", "Education")

# Sidebar navigation.
with st.sidebar:
    st.image(img_lh, width=180)
    menu_options = ["About Me", "Experience", "Technical Skills", "Education", "Projects", "Competitions", "Volunteering", "Blog", "Gallery", "Resume", "Testimonials", "Contact"]
    if option_menu is not None:
        choose = option_menu(
            "Harry Chang",
            menu_options,
            icons=['person fill', 'clock history', 'tools', 'book half', 'clipboard', 'trophy fill', 'heart', 'pencil square', 'image', 'paperclip', 'star fill', 'envelope'],
            default_index=0,
            menu_icon="mortarboard",
            styles={
                "container": {"padding": "0!important", "background-color": "#f5f5dc"},
                "icon": {"color": "darkorange", "font-size": "20px"},
                "nav-link": {"font-size": "17px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#cfcfb4"},
            },
        )
    else:
        choose = st.radio("Menu", menu_options, index=0)

    social_links = {
        "Youtube": "https://www.youtube.com/@harrychangjr",
        "LinkedIn": "https://www.linkedin.com/in/harrychangjr/",
        "GitHub": "https://github.com/harrychangjr",
        "Wordpress": "https://antcabbage.wordpress.com",
        "Email": "mailto:harrychang.work@gmail.com",
    }
    st.markdown(social_icons(28, 28, **social_links), unsafe_allow_html=True)

# Main content sections.
if choose == "About Me":
    col_left, col_mid, col_right = st.columns((2.2, 0.3, 1.2))
    with col_left:
        st.header("About Me")
        st.subheader("Aspiring Data Analyst / Product Manager")
        st.write("Hi, I'm Harry — a data science and analytics undergraduate based in Singapore. I enjoy building products, extracting insight from data, and turning ideas into useful experiences.")
        st.write("I am especially interested in data visualization, recommendation systems, market basket analysis, and product analytics.")
        st.write("I enjoy running, writing, gaming, and learning new tools that help me become more effective in data-driven roles.")
        st.markdown("[Resume (1 page)](https://drive.google.com/file/d/164EEVH6BmvC89q2M4WsBNF1JyddDAbNY/view?usp=sharing)")
    with col_right:
        st.image(img_utown, width=500)

elif choose == "Experience":
    st.header("Experience")
    st.markdown("""
    - Product Manager, HedgeDrip (Sep 2023 - Present)
    - Data Science Intern, Groundup.ai (Jul - Dec 2023)
    - Data Science Intern, Bitmetrix (Jun - Jul 2023)
    - Actuarial Intern, SCOR (May - Aug 2022)
    - Data Analytics Intern, Quest (Feb - May 2022)
    """)
    st.image(img_quest, width=220)
    st.image(img_saf, width=220)

elif choose == "Technical Skills":
    st.header("Technical Skills")
    st.markdown("""
    - Programming: Python, R, SQL, Java, Stata, MATLAB
    - Data Viz: Tableau, Power BI, matplotlib, seaborn, Plotly, ggplot2
    - ML & DS: scikit-learn, pandas, NumPy, TensorFlow, Keras
    - Databases: MySQL, PostgreSQL, SQLite, BigQuery, Firestore
    - Cloud: AWS, GCP, Heroku, Streamlit Cloud, Render
    - Design: Figma, Canva, HTML, CSS, Streamlit, WordPress
    """)

elif choose == "Education":
    st.header("Education")
    st.subheader("Bachelor of Science in Data Science and Analytics")
    st.write("National University of Singapore (2020 - 2024)")
    st.image(img_nus, width=320)
    st.write("Relevant coursework: Data Visualization, Regression Analysis, Statistical Learning, Database Management, Data Structures and Algorithms, Machine Learning.")
    st.write("Other activities: NUS Product Club, NUS Statistics and Data Science Society, Google Developer Student Clubs NUS.")

elif choose == "Projects":
    st.header("Projects")
    st.markdown("""
    - Blockchain Social Media Webscraper
    - Enhanced TikTok Analytics Dashboard
    - Sales Volume Prediction with Regression Methods
    - Optimising Article Quality with ChatGPT and NLP
    - Statistical Learning Analysis on Video Game Sales
    """)

elif choose == "Competitions":
    st.header("Competitions")
    st.markdown("""
    - SMU-LIT Hackathon 2023
    - NUS LifeHack 2023
    - NUS LifeHack 2022
    - NUS Fintech Month Hackathon 2021
    - Shopee Product and Design Challenge 2021
    """)

elif choose == "Volunteering":
    st.header("Volunteering")
    st.markdown("""
    - NUS Fintech Society — Design Manager
    - NUS Human Capital Society — Research & Strategy Executive
    - NUS Product Club — Co-founder & President
    - NUS Statistics and Data Science Society — President / Marketing Director
    - Saturday Kids — Python Instructor
    """)

elif choose == "Blog":
    st.header("Blog")
    st.markdown("A selection of my essays, reflections, and write-ups on data, technology, policy, culture, and personal growth.")
    st.markdown("- Mayans MC – Season 5 Detailed Preview")
    st.markdown("- Finding Success as an Outlier")
    st.markdown("- Should the statue of Sir Stamford Raffles disappear for good?")

elif choose == "Gallery":
    st.header("Gallery")
    st.write("Highlights across my educational journey, from primary school to university.")
    cols = st.columns(3)
    for idx, col in enumerate(cols):
        with col:
            st.image(build_placeholder_image(f"Year {2020 + idx}", width=500, height=350), width=500)

elif choose == "Resume":
    st.header("Resume")
    st.write("The original resume file is not present in this workspace, but the public Google Drive link remains available.")
    st.markdown(pdf_link("https://drive.google.com/file/d/164EEVH6BmvC89q2M4WsBNF1JyddDAbNY/view?usp=sharing", "Open Resume"), unsafe_allow_html=True)

elif choose == "Testimonials":
    st.header("Testimonials")
    st.write("The original PDF bundle is not included in this workspace, so only the public link is available here.")
    st.markdown(pdf_link("https://drive.google.com/file/d/1ZyTmg_r18sUuuU5JOJBqUb2EP8MnjvJU/view?usp=sharing", "Compiled Testimonials"), unsafe_allow_html=True)

elif choose == "Contact":
    st.header("Contact")
    st.write("Let’s connect! You can reach me at harrychang.work@gmail.com.")
    st.markdown(social_icons(32, 32, LinkedIn="https://www.linkedin.com/in/harrychangjr/", GitHub="https://github.com/harrychangjr", Email="mailto:harrychang.work@gmail.com"), unsafe_allow_html=True)
    st.image(img_ifg, width=260)

st.markdown("*Copyright © 2023 Harry Chang*")
