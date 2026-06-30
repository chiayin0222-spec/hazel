import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai

# Load .env file manually if it exists
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k.strip()] = v.strip().strip('"').strip("'")

DATA_FILE = os.path.join(os.path.dirname(__file__), 'movies.json')


def load_movies():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


st.set_page_config(page_title='電影查詢聊天機器人', page_icon='🎬', layout='wide')

# Custom Titanic Movie Theme CSS Styling
style_html = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* Global body & app background styling */
html, body, .stApp, [data-testid="stAppViewContainer"], section.main, div.block-container {
    font-family: 'Outfit', 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, #E2E8F0 0%, #CBD5E1 100%) !important;
    color: #0F172A !important;
}

[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Sidebar styling - Silver/Slate */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #CBD5E1 0%, #94A3B8 100%) !important;
    border-right: 1px solid rgba(15, 23, 42, 0.15) !important;
}

/* Custom shimmering slate gradient title */
.titanic-title {
    font-size: 2.8em !important;
    font-weight: 800 !important;
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #0F172A 100%) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    margin-bottom: 25px !important;
    text-align: center !important;
    text-shadow: none !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #CBD5E1;
}
::-webkit-scrollbar-thumb {
    background: #94A3B8;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #64748B;
}

/* Streamlit Tabs custom design - Glass style */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    background-color: rgba(255, 255, 255, 0.4) !important;
    border: 1px solid rgba(15, 23, 42, 0.1) !important;
    border-bottom: none !important;
    color: #475569 !important;
    font-weight: 600;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 8px 18px;
    transition: all 0.2s ease;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #0F172A !important;
    background-color: rgba(255, 255, 255, 0.6) !important;
}
.stTabs [aria-selected="true"] {
    background-color: rgba(255, 255, 255, 0.8) !important;
    color: #1E3A8A !important;
    border-color: rgba(15, 23, 42, 0.2) !important;
    border-bottom: none !important;
    box-shadow: 0 -4px 12px rgba(15, 23, 42, 0.05);
}

/* Chat bubble overrides */
.stChatMessage {
    background-color: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(15, 23, 42, 0.1) !important;
    border-radius: 12px !important;
    margin-bottom: 8px !important;
}
.stChatMessage [data-testid="stMarkdownContainer"] p {
    color: #0F172A !important;
    font-size: 0.9em !important;
}

/* Custom list layout movie card - Frosted Glass Light */
.titanic-card {
    display: flex;
    background: rgba(255, 255, 255, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(15, 23, 42, 0.08) !important;
    backdrop-filter: blur(12px) saturate(120%);
    -webkit-backdrop-filter: blur(12px) saturate(120%);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.titanic-card:hover {
    transform: translateY(-5px) scale(1.005);
    border-color: rgba(255, 255, 255, 0.8) !important;
    box-shadow: 0 15px 40px rgba(15, 23, 42, 0.15) !important;
    background: rgba(255, 255, 255, 0.85) !important;
}
.titanic-card-img {
    flex: 0 0 120px;
    margin-right: 20px;
}
.titanic-card-img img {
    width: 120px;
    border-radius: 8px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15);
    border: 1px solid rgba(255, 255, 255, 0.4);
}
.titanic-card-info {
    flex: 1;
}
.titanic-card-title a {
    font-family: 'Outfit', sans-serif;
    font-size: 1.4em;
    font-weight: 700;
    color: #0F172A !important;
    text-decoration: none;
    transition: color 0.2s ease;
}
.titanic-card-title a:hover {
    color: #1E3A8A !important;
}
.titanic-badges {
    margin: 10px 0;
}
.titanic-badge {
    background-color: rgba(15, 23, 42, 0.06);
    color: #0F172A;
    border: 1px solid rgba(15, 23, 42, 0.12);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    margin-right: 6px;
    font-weight: 600;
    display: inline-block;
}
.titanic-meta {
    font-size: 0.9em;
    color: #475569;
    margin-bottom: 6px;
}
.titanic-score {
    font-size: 1.0em;
    font-weight: bold;
    color: #0F172A;
    margin-top: 10px;
}
.titanic-score span {
    color: #D97706;
    font-size: 1.3em;
    font-weight: 800;
}

/* Custom Rank card - Frosted Glass Light */
.titanic-rank-card {
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 12px;
    padding: 12px;
    margin-bottom: 12px;
    box-shadow: 0 4px 15px rgba(15, 23, 42, 0.05) !important;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    transition: all 0.2s ease;
}
.titanic-rank-card:hover {
    transform: translateX(5px);
    border-color: rgba(255, 255, 255, 0.8) !important;
    background: rgba(255, 255, 255, 0.75) !important;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.08) !important;
}
.titanic-rank-img {
    flex: 0 0 50px;
    margin-right: 12px;
}
.titanic-rank-img img {
    width: 50px;
    height: 70px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.3);
}
.titanic-rank-info {
    flex: 1;
}
.titanic-rank-num {
    font-size: 1.1em;
    color: #D97706;
    font-weight: 800;
}
.titanic-rank-name {
    font-size: 0.9em;
    font-weight: 600;
    color: #0F172A;
}
.titanic-rank-val {
    font-size: 0.85em;
    color: #475569;
    margin-top: 2px;
}

/* Custom Grid card - Frosted Glass Light */
.titanic-grid-card {
    text-align: center;
    background: rgba(255, 255, 255, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    transition: all 0.3s ease;
    height: 380px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.titanic-grid-card:hover {
    transform: translateY(-5px);
    border-color: rgba(255, 255, 255, 0.8) !important;
    box-shadow: 0 15px 35px rgba(15, 23, 42, 0.1) !important;
    background: rgba(255, 255, 255, 0.75) !important;
}
.titanic-grid-img img {
    width: 100%;
    height: 250px;
    object-fit: cover;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.3);
}
.titanic-grid-title {
    font-size: 0.9em;
    font-weight: bold;
    color: #0F172A;
    margin: 8px 0 4px 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.titanic-grid-score {
    font-size: 0.85em;
    color: #D97706;
    font-weight: bold;
}
.titanic-grid-link a {
    font-size: 0.8em;
    color: #475569 !important;
    text-decoration: none;
    transition: color 0.2s ease;
}
.titanic-grid-link a:hover {
    color: #1E3A8A !important;
}

/* Cinema Footer Styling */
.cinema-footer {
    background: rgba(255, 255, 255, 0.4) !important;
    border-top: 1px solid rgba(15, 23, 42, 0.1) !important;
    padding: 50px 0 35px 0 !important;
    margin-top: 80px !important;
    text-align: center !important;
    width: 100% !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 -10px 40px rgba(15, 23, 42, 0.03) !important;
}
.footer-svg {
    width: 85% !important;
    max-width: 950px !important;
    height: auto !important;
    margin: 0 auto !important;
    display: block !important;
}
.footer-text {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.0em !important;
    font-weight: 700 !important;
    color: #1E3A8A !important;
    margin-top: 20px !important;
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    opacity: 0.95 !important;
}
.svg-element {
    animation: floatSVG 4s ease-in-out infinite !important;
    filter: drop-shadow(0 0 4px rgba(15, 23, 42, 0.15)) !important;
}
.svg-element:nth-child(2) { animation-delay: 1.0s !important; }
.svg-element:nth-child(3) { animation-delay: 2.0s !important; }
.svg-element:nth-child(4) { animation-delay: 3.0s !important; }

@keyframes floatSVG {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-5px); }
}
</style>
"""
st.markdown(style_html, unsafe_allow_html=True)
st.markdown('<h1 class="titanic-title">🎬 電影查詢聊天機器人</h1>', unsafe_allow_html=True)

movies = load_movies()
if not movies:
    st.error('請先執行 crawler.py 爬取資料')
    st.stop()

# API Key Config & Chatbot in Sidebar
st.sidebar.title("🤖 AI 助手設定")
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    api_key_input = st.sidebar.text_input("輸入 Gemini API Key", type="password", help="請輸入您的 Gemini API 密鑰以啟用聊天機器人")
    if api_key_input:
        api_key = api_key_input

# Initialize Chatbot history in sidebar with greeting and keyword tips
if "chat_history" not in st.session_state:
    welcome_msg = (
        "👋 您好！我是您的 **AI 電影小助理**。我已載入目前資料庫中的 100 部精選電影。\n\n"
        "您可以直接向我發問，或參考以下**詢問關鍵字/範例**：\n"
        "- 🔍 **地區與類型**：例如「推薦我一些*法國*的*犯罪*片」\n"
        "- 🏆 **評分與片長**：例如「哪部電影*評分*最高？」或「片長大於 *150分鐘* 的電影有哪些？」\n"
        "- 🎬 **電影詳情**：例如「介紹一下*這個殺手不太冷*」\n"
        "- 📊 **數據統計**：例如「熱門的電影分類前三名是哪些？」\n\n"
        "請問今天想看什麼電影呢？🍿"
    )
    st.session_state.chat_history = [{"role": "assistant", "content": welcome_msg}]

st.sidebar.subheader("💬 AI 電影小助理")

if not api_key:
    st.sidebar.info("💡 請先設定 API Key 以啟用小助理")
else:
    # Clear chat history button
    if st.sidebar.button("🗑️ 清除對話紀錄"):
        if "chat_history" in st.session_state:
            del st.session_state["chat_history"]
        st.rerun()

    # Scrollable container for chat history in sidebar
    chat_container = st.sidebar.container(height=380)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input at the bottom of the sidebar
    if prompt := st.sidebar.chat_input("詢問小助理...", key="sidebar_chat_input"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        try:
            genai.configure(api_key=api_key)
            movies_str = json.dumps(movies, ensure_ascii=False, indent=2)
            system_instruction = (
                "你是一位專業且友善的電影影評助手（Movie Assistant）。\n"
                "你的主要任務是回答使用者關於電影的問題，特別是關於目前資料庫中這 100 部電影的資訊。\n"
                "以下是目前資料庫中的 100 部電影完整 JSON 資料：\n"
                f"{movies_str}\n\n"
                "注意事項：\n"
                "1. 當使用者詢問特定評分、片長、地區、上映日期或進行推薦時，請優先參考並精確比對此資料庫的內容。\n"
                "2. 若資料庫中沒有相關資訊，你可以使用你本身擁好的外部電影知識來補充或進行回答，但請說明這是外部知識。\n"
                "3. 請一律使用繁體中文（Traditional Chinese）回答，語氣保持客氣、專業且生動。\n"
                "4. 回答請條理清晰，適當使用 markdown 粗體、清單或表格來美化版面。\n"
            )
            
            model = genai.GenerativeModel(
                model_name="gemini-3.5-flash",
                system_instruction=system_instruction
            )
            
            gemini_history = []
            for h in st.session_state.chat_history[:-1]:
                role = "user" if h["role"] == "user" else "model"
                gemini_history.append({
                    "role": role,
                    "parts": [h["content"]]
                })
                
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt)
            response_text = response.text
            
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.session_state.chat_history.append({"role": "assistant", "content": f"❌ 發生錯誤: {e}"})
        st.rerun()


def display_movie_card(m):
    st.markdown(f"""
    <div class="titanic-card">
        <div class="titanic-card-img">
            <img src="{m['poster']}" referrerpolicy="no-referrer" alt="Poster">
        </div>
        <div class="titanic-card-info">
            <div class="titanic-card-title"><a href="{m['detail_url']}" target="_blank">🎬 {m['name']}</a></div>
            <div class="titanic-badges">
                {"".join([f'<span class="titanic-badge">{c}</span>' for c in m['categories']])}
            </div>
            <div class="titanic-meta">🌍 地區: {m['region']} &nbsp;&nbsp;|&nbsp;&nbsp; ⏱️ 時長: {m['duration']}</div>
            <div class="titanic-meta">📅 上映時間: {m['release'] if m['release'] else 'N/A'}</div>
            <div class="titanic-score">⭐ 評分: <span>{m['score']}</span> / 10</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


rank_tab, all_tab = st.tabs(['🏆 排名', '📋 全部電影'])

with rank_tab:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('評分 TOP 10')
        top_score = sorted(movies, key=lambda x: x['score'], reverse=True)[:10]
        for i, m in enumerate(top_score, 1):
            st.markdown(f"""
            <div class="titanic-rank-card">
                <div class="titanic-rank-img">
                    <img src="{m['poster']}" referrerpolicy="no-referrer" alt="Poster">
                </div>
                <div class="titanic-rank-info">
                    <div class="titanic-rank-num">#{i}</div>
                    <div class="titanic-rank-name">{m['name']}</div>
                    <div class="titanic-rank-val">⭐ {m['score']}</div>
                    <div style="font-size: 0.8em; margin-top: 2px;"><a href="{m['detail_url']}" target="_blank" style="color: #C5A059; text-decoration: none;">詳情連結 🔗</a></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.subheader('時長 TOP 10')
        valid = [m for m in movies if m['duration']]
        def parse_dur(d):
            return int(d.replace('分钟', '').strip())
        top_dur = sorted(valid, key=lambda x: parse_dur(x['duration']), reverse=True)[:10]
        for i, m in enumerate(top_dur, 1):
            st.markdown(f"""
            <div class="titanic-rank-card">
                <div class="titanic-rank-img">
                    <img src="{m['poster']}" referrerpolicy="no-referrer" alt="Poster">
                </div>
                <div class="titanic-rank-info">
                    <div class="titanic-rank-num">#{i}</div>
                    <div class="titanic-rank-name">{m['name']}</div>
                    <div class="titanic-rank-val">⏱️ {m['duration']}</div>
                    <div style="font-size: 0.8em; margin-top: 2px;"><a href="{m['detail_url']}" target="_blank" style="color: #C5A059; text-decoration: none;">詳情連結 🔗</a></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

with all_tab:
    st.subheader(f'全部電影（共 {len(movies)} 部）')
    
    # Grid parameters
    movies_per_page = 12
    total_movies = len(movies)
    total_pages = (total_movies + movies_per_page - 1) // movies_per_page
    
    # Pagination controls at the top
    page_col1, page_col2 = st.columns([1, 4])
    with page_col1:
        page = st.selectbox('選擇頁碼', options=list(range(1, total_pages + 1)), index=0)
        
    start_idx = (page - 1) * movies_per_page
    end_idx = min(start_idx + movies_per_page, total_movies)
    page_movies = movies[start_idx:end_idx]
    
    st.write(f"顯示第 {start_idx + 1} 至 {end_idx} 部電影，共 {total_movies} 部")
    
    # 4 columns grid
    grid_cols = st.columns(4)
    for idx, m in enumerate(page_movies):
        col = grid_cols[idx % 4]
        with col:
            short_name = m['name'].split(' - ')[0]
            if len(short_name) > 15:
                short_name = short_name[:15] + '...'
            st.markdown(f"""
            <div class="titanic-grid-card">
                <div class="titanic-grid-img">
                    <img src="{m['poster']}" referrerpolicy="no-referrer" alt="Poster">
                </div>
                <div class="titanic-grid-title">{short_name}</div>
                <div class="titanic-grid-score">⭐ {m['score']}</div>
                <div class="titanic-grid-link"><a href="{m['detail_url']}" target="_blank">🔗 詳情頁面</a></div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div class="cinema-footer">
<svg viewBox="0 0 1200 120" class="footer-svg" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="beam-grad" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="#38bdf8" stop-opacity="0.4"/>
<stop offset="100%" stop-color="#ec4899" stop-opacity="0.0"/>
</linearGradient>
<linearGradient id="line-grad" x1="0%" y1="0%" x2="100%" y2="0%">
<stop offset="0%" stop-color="rgba(255, 255, 255, 0.05)"/>
<stop offset="20%" stop-color="rgba(56, 189, 248, 0.3)"/>
<stop offset="50%" stop-color="rgba(236, 72, 153, 0.3)"/>
<stop offset="80%" stop-color="rgba(255, 224, 130, 0.3)"/>
<stop offset="100%" stop-color="rgba(255, 255, 255, 0.05)"/>
</linearGradient>
</defs>

<!-- Dynamic wavy film strip lines -->
<path d="M 0,60 C 300,20 300,100 600,60 C 900,20 900,100 1200,60" fill="none" stroke="url(#line-grad)" stroke-width="3.5" />
<path d="M 0,70 C 300,30 300,110 600,70 C 900,30 900,110 1200,70" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="8,8" />

<!-- Projector on the left (around X=150, Y=60) -->
<g transform="translate(150, 40)" class="svg-element">
<!-- Projector Light Beam -->
<polygon points="40,20 180,-10 180,50" fill="url(#beam-grad)" />
<polygon points="40,20 180,-10 180,50" fill="none" stroke="#38bdf8" stroke-width="1.5" />
<!-- Projector Body -->
<rect x="0" y="10" width="40" height="25" rx="3" fill="none" stroke="#f8fafc" stroke-width="3" />
<!-- Projector Reels -->
<circle cx="10" cy="-5" r="14" fill="none" stroke="#38bdf8" stroke-width="3" />
<circle cx="10" cy="-5" r="4" fill="#38bdf8" />
<circle cx="30" cy="-5" r="14" fill="none" stroke="#38bdf8" stroke-width="3" />
<circle cx="30" cy="-5" r="4" fill="#38bdf8" />
<!-- Projector Lens -->
<polygon points="40,18 48,13 48,27 40,22" fill="none" stroke="#f8fafc" stroke-width="3" />
<!-- Stand -->
<line x1="20" y1="35" x2="10" y2="55" stroke="#f8fafc" stroke-width="3" />
<line x1="20" y1="35" x2="30" y2="55" stroke="#f8fafc" stroke-width="3" />
</g>

<!-- Clapperboard in the middle-left (around X=450, Y=65) -->
<g transform="translate(450, 45)" class="svg-element">
<!-- Clapper Main Board -->
<rect x="0" y="12" width="36" height="26" rx="2" fill="none" stroke="#f8fafc" stroke-width="3" />
<!-- Clapper Top Bar (open) -->
<g transform="rotate(-20, 0, 12)">
<rect x="0" y="4" width="36" height="8" fill="none" stroke="#ec4899" stroke-width="3" />
<line x1="8" y1="4" x2="14" y2="12" stroke="#ec4899" stroke-width="2" />
<line x1="18" y1="4" x2="24" y2="12" stroke="#ec4899" stroke-width="2" />
<line x1="28" y1="4" x2="34" y2="12" stroke="#ec4899" stroke-width="2" />
</g>
<!-- Details lines on board -->
<line x1="6" y1="20" x2="30" y2="20" stroke="#f8fafc" stroke-width="2.5" />
<line x1="6" y1="28" x2="16" y2="28" stroke="#f8fafc" stroke-width="2.5" />
<line x1="20" y1="28" x2="30" y2="28" stroke="#f8fafc" stroke-width="2.5" />
</g>

<!-- Popcorn in the middle-right (around X=750, Y=60) -->
<g transform="translate(750, 45)" class="svg-element">
<!-- Cup -->
<path d="M 6,15 L 10,42 L 26,42 L 30,15 Z" fill="none" stroke="#f8fafc" stroke-width="3" />
<line x1="14" y1="15" x2="14" y2="42" stroke="#f8fafc" stroke-width="2" />
<line x1="22" y1="15" x2="22" y2="42" stroke="#f8fafc" stroke-width="2" />
<!-- Popcorn Kernels -->
<circle cx="12" cy="11" r="5" fill="none" stroke="#FFE082" stroke-width="2.5" />
<circle cx="18" cy="8" r="6" fill="none" stroke="#FFE082" stroke-width="2.5" />
<circle cx="24" cy="11" r="5" fill="none" stroke="#FFE082" stroke-width="2.5" />
<circle cx="15" cy="5" r="4" fill="none" stroke="#FFE082" stroke-width="2.5" />
<circle cx="21" cy="5" r="4" fill="none" stroke="#FFE082" stroke-width="2.5" />
</g>

<!-- Movie ticket on the right (around X=1000, Y=60) -->
<g transform="translate(1000, 45)" class="svg-element">
<g transform="rotate(15, 20, 20)">
<!-- Ticket Outer Body with notched corners -->
<path d="M 0,8 C 4,8 6,10 6,14 C 6,18 4,20 0,20 L 0,30 Q 0,32 2,32 L 42,32 Q 44,32 44,30 L 44,20 C 40,20 38,18 38,14 C 38,10 40,8 44,8 L 44,2 Q 44,0 42,0 L 2,0 Q 0,0 0,2 Z" fill="none" stroke="#38bdf8" stroke-width="3" />
<!-- Star inside ticket -->
<polygon points="22,8 24,13 29,13 25,16 27,21 22,18 17,21 19,16 15,13 20,13" fill="none" stroke="#38bdf8" stroke-width="2" />
<!-- Dash separation line -->
<line x1="10" y1="0" x2="10" y2="32" stroke="#38bdf8" stroke-width="2" stroke-dasharray="4,4" />
</g>
</g>
</svg>
<div class="footer-text">✨ 🎬 Explore the Wonders of Cinematic Arts 🎬 ✨</div>
</div>
""", unsafe_allow_html=True)
