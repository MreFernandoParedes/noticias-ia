import streamlit as st
import pandas as pd
from database import init_db, save_news, get_recent_news
from rss_fetcher import update_news
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Try to load secrets or env var
# Priority: 1. Environment Variable (.env) 2. Streamlit Secrets
env_key = os.environ.get("OPENAI_API_KEY")
secret_key = None

try:
    secret_key = st.secrets["openai"]["api_key"]
except:
    pass

# Select the valid key
SECRET_API_KEY = None

def is_valid_key(k):
    if not k: return False
    # Check for placeholders
    if k == "sk-..." or k == "sk-tu-clave-aqui" or k.endswith("..."):
        return False
    return True

if is_valid_key(env_key):
    SECRET_API_KEY = env_key
elif is_valid_key(secret_key):
    SECRET_API_KEY = secret_key

# Debug output to console
if SECRET_API_KEY:
    print(f"Loaded API Key: {SECRET_API_KEY[:5]}...{SECRET_API_KEY[-3:]} (Valid format)")
else:
    print(f"Warning: No valid API Key found. Env: {env_key}, Secret: {secret_key}")


# --- Config and Setup ---
st.set_page_config(
    page_title="Noticias IA",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize DB
try:
    init_db()
except Exception as e:
    st.error(f"Error initializing DB: {e}")

# --- CSS Styling ---
# --- CSS Styling ---
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }

    /* Fixed Header Styles */
    .sticky-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #FFFFFF;
        z-index: 999999; /* Maintain on top */
        padding: 10px 0; /* Reduced padding */
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-bottom: 4px solid #C8102E;
    }
    
    .sticky-title {
        font-size: 1.2rem; /* Reduced to 60% of 2rem */
        font-weight: 800;
        color: #1a1a1a;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Streamlit overrides */
    [data-testid="stHeader"] {
        display: none;
    }
    
    .block-container {
        padding-top: 7rem !important; /* Push content down */
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Card Styles */
    .news-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 5px solid #C8102E; 
        transition: transform 0.2s, box-shadow 0.2s;
        height: 380px; 
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .card-header {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 10px;
        margin-bottom: 8px;
    }
    
    .card-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #C8102E; 
        line-height: 1.25;
        margin: 0;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        max-height: 3.8em; 
    }
    
    .card-summary {
        font-size: 0.9rem;
        color: #333;
        margin-bottom: 8px;
        margin-top: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 9;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        flex-grow: 1;
        line-height: 1.4;
    }
    
    .card-footer {
        margin-top: auto;
        border-top: 1px solid #EEEEEE;
        padding-top: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .read-more {
        font-size: 0.75rem;
        color: #C8102E;
        text-decoration: none;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .read-more:hover {
        text-decoration: underline;
    }
    
    .source-tag {
        font-size: 0.7rem;
        color: #999;
        font-style: italic;
    }

    .status-dot {
        width: 14px;
        height: 14px;
        min-width: 14px;
        border-radius: 50%;
        margin-top: 3px;
        flex-shrink: 0;
    }
    
    .dot-red { background-color: #D32F2F; border: 2px solid #FFCDD2; }
    .dot-yellow { background-color: #FBC02D; border: 2px solid #FFF9C4; }
    .dot-green { background-color: #388E3C; border: 2px solid #C8E6C9; }
    
    .section-header {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #333;
        border-left: 4px solid #C8102E;
        padding-left: 8px;
        background: #FFFFFF;
        padding: 8px;
        border-radius: 0 4px 4px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

</style>
<div class="sticky-header">
    <div class="sticky-title">Resumen de noticias con IA</div>
</div>
""", unsafe_allow_html=True)

# --- Logic ---

def refresh_data(api_key=None):
    with st.spinner('Actualizando noticias...'):
        try:
            news = update_news(api_key)
            save_news(news)
            time.sleep(0.5) 
        except Exception as e:
            st.error(f"Error al actualizar: {e}")
    st.rerun() 

# --- Layout ---
# Sidebar for API Key
with st.sidebar:
    st.header("Configuración")
    
    if SECRET_API_KEY and "sk-" in SECRET_API_KEY:
        api_key = SECRET_API_KEY
        st.success("API Key cargada desde secretos 🔒")
    else:
        api_key = st.text_input("OpenAI API Key", type="password", help="Introduce tu clave para habilitar IA")
    
    if not api_key:
        st.warning("⚠️ MODO SIN IA: Mostrando títulos originales.")
        st.info("Ingresa tu API Key para generar resúmenes neutrales.")
    else:
        st.success("✅ MODO IA ACTIVO")

# Header Area with Actions
col_actions, col_filters = st.columns([1, 3], vertical_alignment="bottom")

with col_actions:
    if st.button('Actualizar Fuentes 🔄', use_container_width=True):
        refresh_data(api_key)

with col_filters:
    # Filter using Pills (Streamlit 1.40+)
    selected_filter = st.pills(
        "",
        ["Todas", "Noticias Positivas", "Noticias Neutras", "Noticias Negativas"],
        default="Todas",
        selection_mode="single"
    )

# Fetch Data
df = get_recent_news(hours=168)

# Remove duplicates based on title (keep the most recent one)
if not df.empty:
    df = df.drop_duplicates(subset=['title'], keep='first')

if df.empty:
    st.warning("No hay noticias recientes de las últimas 48 horas. Intenta actualizar.")
else:
    # APPLY FILTER
    if selected_filter == "Noticias Positivas":
        df = df[df['sentiment'] == 'green']
    elif selected_filter == "Noticias Neutras":
        df = df[df['sentiment'] == 'yellow']
    elif selected_filter == "Noticias Negativas":
        df = df[df['sentiment'] == 'red']
    
    # Filter by section
    sections = ['Cancilleria', 'Peru', 'Mundo']
    cols = st.columns(3)
    
    for i, section in enumerate(sections):
        with cols[i]:
            st.markdown(f'<div class="section-header">{section}</div>', unsafe_allow_html=True)
            
            section_news = df[df['section'] == section].copy()
            
            if section_news.empty:
                st.info("Sin noticias recientes.")
            else:
                for _, row in section_news.iterrows():
                    color_class = f"dot-{row['sentiment']}"
                    
                    # Clean title
                    clean_title = row['title'].split(' - ')[0]
                    clean_title = clean_title.split(' | ')[0]
                    
                    if len(clean_title) > 150:
                         clean_title = clean_title[:147] + "..."
                    
                    # Clean Date
                    date_str = pd.to_datetime(row['published_date']).strftime("%d/%m %H:%M")
                    
                    # Create card HTML
                    card_html = (
                        f'<div class="news-card">'
                        f'<div class="card-header">'
                        f'<div class="status-dot {color_class}"></div>'
                        f'<div class="card-title" title="{row["title"]}">{clean_title}</div>'
                        f'</div>'
                        f'<div class="card-summary">{row["summary"]}</div>'
                        f'<div class="card-footer">'
                        f'<span class="source-tag">{row["source"]} &bull; {date_str}</span>'
                        f'<a href="{row["link"]}" target="_blank" class="read-more">LEER MÁS &rarr;</a>'
                        f'</div>'
                        f'</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

# Auto-refresh check
if df.empty:
    pass
