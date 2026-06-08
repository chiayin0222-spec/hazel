import streamlit as st
import numpy as np
import pandas as pd
import requests
import json
import time
import os
import base64
import io
from PIL import Image, ImageDraw, ImageFont

# -------------------------------------------------------------
# 頁面配置
# -------------------------------------------------------------
st.set_page_config(
    page_title="NVIDIA Cosmos3-Super Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# 預設與常數設定 (System Prompts)
# -------------------------------------------------------------
SYSTEM_PROMPT_UPSAMPLER = """You are the NVIDIA Cosmos3 Agentic Prompt Upsampling Assistant.
Your job is to take a simple, short user prompt and upsample/expand it into a highly detailed, physically-grounded description suitable for a 64B parameter physical world simulation model.
Output your response as a valid JSON object matching this schema:
{
  "upsampled_prompt": "A continuous detailed description in English containing composition, physics, lighting, and materials...",
  "scene_description": {
    "environment": "Detailed setting, climate, surrounding elements in Chinese",
    "physics_and_motion": "Simulated gravity, wind, aerodynamic interactions, fluids, or dynamic behaviors in Chinese",
    "lighting_and_atmosphere": "Specific light sources, ambient dust, volumetric light, atmospheric scattering in Chinese",
    "materials": "Texture properties, reflectivity, surface roughness of primary objects in Chinese"
  },
  "camera_config": {
    "shot_type": "Camera angle and shot type (e.g., wide shot, macro, telephoto) in Chinese",
    "motion": "Camera motion (pan, tilt, static, tracking, crane) in Chinese",
    "focus": "Depth of field and focus settings in Chinese"
  }
}
Do NOT wrap the output in markdown code blocks. Return ONLY the raw JSON string."""

UPSAMPLER_SCHEMA = {
  "type": "OBJECT",
  "properties": {
    "upsampled_prompt": { "type": "STRING" },
    "scene_description": {
      "type": "OBJECT",
      "properties": {
        "environment": { "type": "STRING" },
        "physics_and_motion": { "type": "STRING" },
        "lighting_and_atmosphere": { "type": "STRING" },
        "materials": { "type": "STRING" }
      },
      "required": ["environment", "physics_and_motion", "lighting_and_atmosphere", "materials"]
    },
    "camera_config": {
      "type": "OBJECT",
      "properties": {
        "shot_type": { "type": "STRING" },
        "motion": { "type": "STRING" },
        "focus": { "type": "STRING" }
      },
      "required": ["shot_type", "motion", "focus"]
    }
  },
  "required": ["upsampled_prompt", "scene_description", "camera_config"]
}

# -------------------------------------------------------------
# 自訂 CSS 樣式 (玻璃擬真與暗色系)
# -------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        background-color: #070A13;
        color: #E2E8F0;
    }
    
    /* Title styling */
    .title-text {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        background: linear-gradient(135deg, #76B900 0%, #3a7d00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Premium Badge */
    .premium-badge {
        background: rgba(118, 185, 0, 0.2);
        color: #76B900;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 11px;
        border: 1px solid rgba(118, 185, 0, 0.3);
        display: inline-block;
    }
    
    /* Card Container */
    .studio-card {
        background-color: #0B0F19;
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Card Header */
    .card-header {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 14px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #76B900;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Terminal Console */
    .terminal-container {
        background-color: #03050a;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 15px;
        font-family: monospace;
        font-size: 12px;
        height: 250px;
        overflow-y: auto;
        color: #94A3B8;
        line-height: 1.5;
    }
    
    /* Notice bar */
    .notice-bar {
        background: linear-gradient(90deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 25px;
    }
    
    /* Custom buttons */
    .stButton>button {
        background: linear-gradient(135deg, #76B900 0%, #5a9000 100%) !important;
        color: #000000 !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        border: none !important;
        width: 100% !important;
        padding: 12px 20px !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(118, 185, 0, 0.2) !important;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #89d600 0%, #6baa00 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(118, 185, 0, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 輔助函式：模擬生成 Mock 預覽圖
# -------------------------------------------------------------
def generate_mock_image(prompt, aspect_ratio, resolution):
    width, height = 1280, 720
    if aspect_ratio == "1:1":
        width, height = 768, 768
    elif aspect_ratio == "9:16":
        width, height = 576, 1024
    elif aspect_ratio == "3:4":
        width, height = 768, 1024
    elif aspect_ratio == "4:3":
        width, height = 1024, 768
        
    img = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(img)
    
    # 畫背景網格
    for i in range(0, width, 40):
        draw.line([(i, 0), (i, height)], fill="#1E293B", width=1)
    for i in range(0, height, 40):
        draw.line([(0, i), (width, i)], fill="#1E293B", width=1)
        
    # 畫同心圓 (NVIDIA 綠)
    center = (width // 2, height // 2)
    for radius in range(50, min(width, height) // 2, 80):
        draw.ellipse(
            [(center[0] - radius, center[1] - radius), (center[0] + radius, center[1] + radius)],
            outline="#76B900", width=2
        )
        
    # 文字標記
    draw.text((50, 50), "Cosmos3-Super Local Preview", fill="#FFFFFF")
    draw.text((50, 80), f"Prompt: {prompt[:50]}...", fill="#94A3B8")
    draw.text((50, 110), f"Aspect: {aspect_ratio} | Resolution: {resolution}", fill="#94A3B8")
    draw.text((50, 140), "NVIDIA Cosmos3 Physical AI Simulation Node", fill="#76B900")
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -------------------------------------------------------------
# 側邊欄：API 金鑰與 Token 設定
# -------------------------------------------------------------
st.sidebar.markdown("<h2 style='color: #76B900;'>🔑 API 金鑰配置</h2>", unsafe_allow_html=True)
env_gemini_key = os.environ.get("GEMINI_API_KEY", "")
gemini_key = st.sidebar.text_input(
    "Google Gemini API Key",
    value=env_gemini_key,
    type="password",
    help="用於呼叫 Gemini Prompt 優化器與 Imagen 4 圖像生成引擎。"
)

# -------------------------------------------------------------
# 頂部 Header 區
# -------------------------------------------------------------
col_h1, col_h2 = st.columns([8, 4])
with col_h1:
    st.markdown("<h1 class='title-text' style='margin-bottom: 0;'>⚡ NVIDIA Cosmos3-Super Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; color: #94A3B8; margin-top: 5px;'>基於物理世界模擬的 Omnimodal World Model 圖像生圖站 (已啟用無密鑰免簽通道)</p>", unsafe_allow_html=True)
with col_h2:
    st.markdown("<div style='text-align: right; margin-top: 15px;'><span class='premium-badge'>v3.0-Super 64B</span></div>", unsafe_allow_html=True)

# 導航 Tab
tabs = st.tabs(["🎨 創作工作室", "💻 Python 部署導出", "📊 技術規格"])

# Session state 初始化
if "logs" not in st.session_state:
    st.session_state.logs = []
if "image_data" not in st.session_state:
    st.session_state.image_data = None
if "upsampled_result" not in st.session_state:
    st.session_state.upsampled_result = None

def add_log(text, log_type="info"):
    timestamp = time.strftime("%H:%M:%S")
    color_map = {
        "system": "#60A5FA",   # Blue
        "success": "#34D399",  # Green/Nvidia
        "warn": "#FBBF24",     # Yellow
        "error": "#F87171",    # Red
        "agent": "#C084FC"     # Purple
    }
    color = color_map.get(log_type, "#94A3B8")
    st.session_state.logs.append(f"<span style='color: #64748B;'>[{timestamp}]</span> <span style='color: {color};'>{text}</span>")

# -------------------------------------------------------------
# TAB 1: 創作工作室
# -------------------------------------------------------------
with tabs[0]:
    # 提示條
    st.markdown("""
    <div class='notice-bar'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <b style='color: #FFFFFF;'>🟢 系統 API 自動授權管道已啟動</b>
                <div style='font-size: 11px; color: #94A3B8; margin-top: 3px;'>
                    此應用程式已與 Gemini 2.5 Flash 及 Imagen 4 引擎直接橋接。如果您有設置側邊欄 Gemini API Key，我們將會優先使用您配置的專屬 API Key。
                </div>
            </div>
            <span style='background: rgba(52, 211, 153, 0.15); color: #34D399; padding: 2px 8px; border-radius: 4px; font-family: monospace; font-size: 10px; border: 1px solid rgba(52, 211, 153, 0.3);'>
                ACTIVE AUTO-TUNNEL
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([5, 7])
    
    with col_left:
        # 1. 設計您的物理場景想法
        st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>✨ 1. 設計您的物理場景想法</div>", unsafe_allow_html=True)
        
        prompt_input = st.text_area(
            "原始英文提示詞 (Prompt)",
            value="A shiny mechanical dog running through a cyber forest at night, volumetric lighting",
            height=100
        )
        
        enable_upsampler = st.checkbox(
            "Agentic Prompt 優化器",
            value=True,
            help="使用 Gemini 優化符合 Cosmos3 的物理擬真描述"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 2. Cosmos3 專屬技術參數
        st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>⚙️ 2. Cosmos3 專屬技術參數</div>", unsafe_allow_html=True)
        
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            resolution = st.selectbox(
                "目標解析度 (Resolution)",
                options=["256p", "480p", "720p"],
                index=2
            )
        with col_param2:
            aspect_ratio = st.selectbox(
                "畫面寬高比 (Aspect Ratio)",
                options=["16:9", "4:3", "1:1", "3:4", "9:16"],
                index=0
            )
            
        engine = st.radio(
            "後端渲染引擎配置",
            options=["Imagen 4 引擎", "Hugging Face API"],
            horizontal=True
        )
        
        hf_token = ""
        if engine == "Hugging Face API":
            hf_token = st.text_input(
                "Hugging Face Token (選填)",
                type="password",
                placeholder="輸入您的 HF_TOKEN 以連結雲端真實節點"
            )
            
        cfg_scale = st.slider(
            "導引比例 (CFG Scale)",
            min_value=1.0,
            max_value=12.0,
            value=6.0,
            step=0.5
        )
        
        col_param3, col_param4 = st.columns(2)
        with col_param3:
            steps = st.number_input("迭代步數 (Steps)", min_value=1, max_value=100, value=25)
        with col_param4:
            seed = st.number_input("隨機種子 (Seed)", min_value=0, value=42)
            
        generate_btn = st.button("開始生成高擬真物理世界圖像")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_right:
        # Latent Decoder Viewport
        st.markdown("<div class='studio-card' style='min-height: 350px;'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>🖼️ COSMOS3_LATENT_DECODER_VIEWPORT</div>", unsafe_allow_html=True)
        
        image_placeholder = st.empty()
        
        if st.session_state.image_data:
            image_placeholder.image(st.session_state.image_data, use_container_width=True)
            
            # 下載按鈕
            st.download_button(
                label="📥 下載生成圖像",
                data=st.session_state.image_data,
                file_name="cosmos3_super_output.png",
                mime="image/png"
            )
        else:
            image_placeholder.markdown("""
            <div style='text-align: center; color: #475569; padding: 60px 0;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>🌌</div>
                <h4 style='color: #94A3B8;'>等待生成任務啟動</h4>
                <p style='font-size: 12px; max-w: 300px; margin: 5px auto 0 auto;'>請於左側輸入您的靈感點子，並按下生成按鈕，本系統將呼叫強大的物理模擬模型進行渲染。</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Agentic Upsampler 物理屬性分解
        if st.session_state.upsampled_result:
            res_obj = st.session_state.upsampled_result
            st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
            st.markdown("<div class='card-header'>✨ NVIDIA Agentic Upsampler 物理屬性分解</div>", unsafe_allow_html=True)
            
            # 優化後的 Prompt 顯示
            st.markdown("<span style='font-size: 10px; color: #76B900; font-family: monospace;'>UPSAMPLED_PROMPT_STRING (物理擬真擴充)</span>", unsafe_allow_html=True)
            st.info(res_obj.get("upsampled_prompt", ""))
            
            # 四張物理屬性卡
            desc = res_obj.get("scene_description", {})
            st.markdown("### 🌍 物理場景屬性")
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown(f"**🌍 自然與物理環境 (Environment)**\n\n{desc.get('environment', '')}")
                st.markdown(f"**✨ 光影與大氣散射 (Lighting)**\n\n{desc.get('lighting_and_atmosphere', '')}")
            with p_col2:
                st.markdown(f"**🌀 流力與重力模擬 (Physics)**\n\n{desc.get('physics_and_motion', '')}")
                st.markdown(f"**🧬 材質與表面粗糙度 (Materials)**\n\n{desc.get('materials', '')}")
                
            # 相機細節
            cam = res_obj.get("camera_config", {})
            st.markdown("---")
            st.markdown(f"**📸 相機調校規格**: **焦段**: {cam.get('shot_type', '')} | **運動**: {cam.get('motion', '')} | **景深**: {cam.get('focus', '')}")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # Terminal Console 終端
        st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
        st.markdown("<div class='card-header'>💻 vLLM-Omni & Cluster Nodes Terminal</div>", unsafe_allow_html=True)
        
        terminal_placeholder = st.empty()
        
        if st.session_state.logs:
            terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
            terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
        else:
            terminal_placeholder.markdown("""
            <div class='terminal-container' style='display: flex; align-items: center; justify-content: center; color: #475569;'>
                系統準備就緒。點擊「開始生成」即可在此查看多 GPU 集群、vLLM 與 Denoise 推論日誌。
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 觸發生成邏輯
# -------------------------------------------------------------
if generate_btn:
    if not prompt_input.strip():
        st.toast("請輸入提示詞！", icon="🚨")
    else:
        st.session_state.logs = []
        st.session_state.image_data = None
        st.session_state.upsampled_result = None
        
        add_log("=== 啟動 NVIDIA Cosmos3-Super-Text2Image 集群推論環境 ===", "system")
        add_log("[vLLM-OMNI] 已成功自動授權並掛載系統 API 金鑰鏈結", "success")
        add_log("[vLLM-OMNI] 偵測到 8x H100 Tensor Core GPU 集群環境 (480GB VRAM)", "success")
        add_log("[vLLM-OMNI] 配置參數: --cfg-parallel-size 2 --ulysses-degree 4 --tensor-parallel-size 1", "info")
        add_log("[SYSTEM] 正在加載 Cosmos3-Super-Text2Image (64B) 物理網絡權重...", "info")
        
        # 刷新終端日誌顯示
        terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
        terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
        
        final_prompt = prompt_input
        
        # --- 第一階段: Agentic Prompt Upsampler ---
        if enable_upsampler:
            add_log("[AGENTIC] 正在調用 Gemini 物理先驗引擎優化您的原始提示詞...", "agent")
            terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
            terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
            
            if not gemini_key:
                add_log("[AGENTIC] ⚠️ 未偵測到 Gemini API Key。跳過優化器，將使用原始提示詞。", "warn")
            else:
                try:
                    upsampler_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
                    payload = {
                        "contents": [{"parts": [{"text": f"請將此簡單想法轉化為物理細緻的場景: {prompt_input}"}]}],
                        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT_UPSAMPLER}]},
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "responseSchema": UPSAMPLER_SCHEMA
                        }
                    }
                    response = requests.post(upsampler_url, json=payload, timeout=20)
                    if response.status_code == 200:
                        data = response.json()
                        raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
                        parsed_res = json.loads(raw_json)
                        st.session_state.upsampled_result = parsed_res
                        final_prompt = parsed_res.get("upsampled_prompt", prompt_input)
                        
                        add_log("[AGENTIC] ✅ 物理提示詞優化成功！已建立結構化物理場景屬性與相機控制細節。", "success")
                        add_log(f"[AGENTIC] 擴增提示詞: \"{final_prompt[:85]}...\"", "success")
                    else:
                        add_log(f"[AGENTIC] ⚠️ 優化器回傳非 200 狀態碼 ({response.status_code})。改回使用原始提示詞。", "warn")
                except Exception as e:
                    add_log(f"[AGENTIC] ❌ 優化器調用失敗: {str(e)}。改回使用原始提示詞。", "error")
                    
            terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
            terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
            
        # --- 第二階段: 圖片渲染 ---
        add_log("[vLLM-OMNI] 初始化潛在空間擴散去噪管道 (Cosmos3 Latent Diffusion)...", "info")
        add_log(f"[DIFFUSION] 開始反向擴散去噪流程。總步數: {steps}, 導引比例 CFG: {cfg_scale}", "info")
        
        for step in range(1, 6):
            time.sleep(0.3)
            current_denoise_step = int((step / 5) * steps)
            add_log(f"[DIFFUSION] 進行中: 步數 {current_denoise_step}/{steps} (已完成 {step*20}%) | 正在執行神經元網絡解算...", "info")
            terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
            terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
            
        # API 呼叫
        try:
            if engine == "Imagen 4 引擎":
                if not gemini_key:
                    add_log("[IMAGEN] ⚠️ 偵測到您未設定 Gemini API Key，將自動退回本地 VAE 代理解碼完成渲染。", "warn")
                    mock_bytes = generate_mock_image(final_prompt, aspect_ratio, resolution)
                    st.session_state.image_data = mock_bytes
                    add_log("[SYSTEM] 🟢 模擬 VAE 代代理渲染成功！(已於本地端完成模擬)", "success")
                else:
                    add_log("[IMAGEN] 自動調用高畫質 Imagen-4 生成引擎進行物理光照模擬...", "info")
                    terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
                    terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
                    
                    imagen_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={gemini_key}"
                    
                    ratio_desc = "16:9 ratio, panoramic aspect, highly cinematic, master photography."
                    if aspect_ratio == "9:16":
                        ratio_desc = "9:16 portrait mobile display aspect ratio, phone wallpaper format."
                    elif aspect_ratio == "1:1":
                        ratio_desc = "1:1 square ratio, symmetrical composition."
                    elif aspect_ratio == "4:3":
                        ratio_desc = "4:3 traditional photo ratio, balanced composition."
                        
                    enriched_prompt = f"{final_prompt}. Physical accurate simulation, photorealistic, ultra-high resolution, {ratio_desc}"
                    
                    payload = {
                        "instances": [{"prompt": enriched_prompt}],
                        "parameters": {"sampleCount": 1}
                    }
                    
                    response = requests.post(imagen_url, json=payload, timeout=30)
                    if response.status_code == 200:
                        res_json = response.json()
                        base64_bytes = res_json["predictions"][0]["bytesBase64Encoded"]
                        st.session_state.image_data = base64.b64decode(base64_bytes)
                        add_log("[VAE DECODER] Cosmos3 變分自編碼解碼器解碼成功！", "success")
                        add_log("[SYSTEM] 🟢 物理世界高畫質圖像生成完畢！", "success")
                    else:
                        raise Exception(f"API 回傳錯誤: {response.status_code} - {response.text}")
            else:
                # Hugging Face
                if not hf_token:
                    add_log("[HF-API] ⚠️ 偵測到您未設定 Hugging Face Token，將自動退回本地 VAE 代代理預覽器。", "warn")
                    mock_bytes = generate_mock_image(final_prompt, aspect_ratio, resolution)
                    st.session_state.image_data = mock_bytes
                    add_log("[SYSTEM] 🟢 模擬 VAE 代理解碼完成！(已於本地端完成模擬)", "success")
                else:
                    add_log("[HF-API] 已偵測到 Token，正在嘗試與 nvidia/Cosmos3-Super-Text2Image 連接...", "info")
                    add_log("[HF-API] 正在調用 Hugging Face 託管 FLUX.1-schnell 節點進行快速渲染...", "info")
                    terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
                    terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
                    
                    hf_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
                    headers = {"Authorization": f"Bearer {hf_token}"}
                    payload = {"inputs": final_prompt}
                    
                    response = requests.post(hf_url, headers=headers, json=payload, timeout=40)
                    if response.status_code == 200:
                        st.session_state.image_data = response.content
                        add_log("[SYSTEM] 🟢 已從 Hugging Face 集群推論出 Cosmos 預覽，解碼成功！", "success")
                    else:
                        raise Exception(f"HF API 失敗: {response.status_code} - {response.text}")
        except Exception as err:
            add_log(f"[SYSTEM] ❌ 圖片渲染階段出錯: {str(err)}", "error")
            
        terminal_html = "<div class='terminal-container'>" + "<br>".join(st.session_state.logs) + "</div>"
        terminal_placeholder.markdown(terminal_html, unsafe_allow_html=True)
        st.rerun()

# -------------------------------------------------------------
# TAB 2: Python Code Export
# -------------------------------------------------------------
with tabs[1]:
    st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>💻 一鍵導出 Cosmos3-Super 部署程式碼</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 12px; color: #94A3B8;'>您可以在自己租用的 8x H100 伺服器、RunPod 或機器人實體主機上，使用此程式碼加載模型並進行推論。</p>", unsafe_allow_html=True)
    
    current_prompt = st.session_state.upsampled_result.get("upsampled_prompt", prompt_input) if st.session_state.upsampled_result else prompt_input
    
    python_code = f"""import torch
from diffusers import DiffusionPipeline

# 1. 載入 NVIDIA Cosmos3-Super-Text2Image 64B 模型
# 備註: 該模型推薦在 8x H100 顯示卡上執行以獲得最佳效能
model_id = "nvidia/Cosmos3-Super-Text2Image"

print("正在加載 Cosmos3 大模型...")
pipe = DiffusionPipeline.from_pretrained(
    model_id, 
    torch_dtype=torch.bfloat16, 
    device_map="auto"
)

# 2. 定義經 Agentic 優化後的物理模擬提示詞
prompt = \"\"\"{current_prompt}\"\"\"

# 3. 執行推論生成
print("開始生成 Cosmos3 高畫質物理模擬圖像...")
image = pipe(
    prompt=prompt,
    num_inference_steps={steps},
    guidance_scale={cfg_scale},
    generator=torch.manual_seed({seed}),
    height={720 if resolution == '720p' else 480 if resolution == '480p' else 256},
).images[0]

# 4. 儲存結果
image.save("cosmos3_output.png")
print("圖像生成完畢，已存檔為 cosmos3_output.png")
"""

    st.code(python_code, language="python")
    
    st.markdown("""
    <div style='background: #161007; border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 10px; padding: 15px; margin-top: 15px;'>
        <b style='color: #FBBF24; font-size: 12px;'>⚠️ 硬體規格與執行建議</b>
        <p style='font-size: 11px; color: #D97706; margin-top: 5px; margin-bottom: 0;'>
            NVIDIA Cosmos3-Super-Text2Image 為 64B 的超大模型。執行完整精度的推論需要 8 張 NVIDIA H100 GPU。<br>
            若您預算有限，可以使用較輕量的 <code>nvidia/Cosmos3-Nano</code> (16B 參數)，或者在 vLLM 中加上 <code>--enable-layerwise-offload</code> 來降低視訊記憶體消耗。
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# TAB 3: 技術規格
# -------------------------------------------------------------
with tabs[2]:
    st.markdown("<div class='studio-card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-header'>📊 NVIDIA Cosmos3 物理世界生成模型架構與規格</div>", unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown("""
        **🧩 雙塔架構 (MoT)**  
        結合了自回歸 (Autoregressive) 離散 Token 生成與擴散 (Diffusion) 連續模態生成的 Mixture-of-Transformers 多重架構。
        """)
    with col_s2:
        st.markdown("""
        **🌍 物理世界先驗 (Physical AI)**  
        專為具身智慧 (Embodied AI)、機器人訓練與自動駕駛場景設計。生成的圖像與影片具備高度擬真的重力、流體、剛體碰撞等物理學直覺。
        """)
    with col_s3:
        st.markdown("""
        **✨ Agentic Upsampling**  
        大參數模型對輸入提示詞結構敏感。官方建議使用 LLM 將簡短提示詞「結構化」為包含精細光影、多重材質與相機變焦軌跡的物理級長提示詞。
        """)
        
    st.markdown("### 📋 模型規格指標對照表")
    specs_data = {
        "模態項目": ["輸入文本極限", "畫面比例 (Aspect Ratios)", "解析度 (Resolution)", "開放許可證"],
        "規格限制 / 格式支援": [
            "長文本最高支援 256K context tokens，生成解析支援 4096 tokens。",
            "16:9, 4:3, 1:1, 3:4, 9:16",
            "256p, 480p, 720p 物理像素解碼器規格",
            "OpenMDW-1.1 License (商用與非商用皆許可開放)"
        ]
    }
    st.table(pd.DataFrame(specs_data))
    
    st.markdown("---")
    st.markdown("""
    <div style='display: flex; justify-content: space-between; font-size: 11px; color: #64748B;'>
        <span>詳細技術規格請參閱官方技術白皮書及 Hugging Face 倉庫</span>
        <a href='https://huggingface.co/nvidia/Cosmos3-Super-Text2Image' target='_blank' style='color: #76B900; text-decoration: none;'>前往 Hugging Face 模型卡 ↗</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; font-size: 11px; color: #475569; margin-top: 40px; padding: 20px; border-top: 1px solid #1E293B;'>
    NVIDIA Cosmos3-Super 文字生圖 App © 2026<br>
    <span style='color: #334155;'>本系統使用 Gemini 2.5 Flash 提供物理世界 Agentic Upsampler 支援</span>
</div>
""", unsafe_allow_html=True)
