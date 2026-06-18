import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from sklearn.metrics import accuracy_score
from utils.data_generator import generate_ring_dataset
from utils.svm_utils import train_svm, make_decision_grid, compute_decision_surface

# 頁面配置
st.set_page_config(
    page_title="SVM 3D Interactive Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" # 預設折疊側邊欄以配合三欄設計
)

# --- 快取資料產生器 ---
@st.cache_data
def get_cached_dataset(n_points, noise, seed):
    n_inner = n_points // 2
    n_outer = n_points - n_inner
    X, y = generate_ring_dataset(
        n_inner=n_inner,
        n_outer=n_outer,
        inner_radius_range=(0.0, 1.0),
        outer_radius_range=(1.6, 2.5),
        noise=noise,
        random_seed=seed
    )
    return X, y

# --- 淺色主題與現代化 UI CSS 注入 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Noto+Sans+TC:wght@300;400;500;700;900&display=swap');
    
    /* 全域背景與字型樣式 - 改為清新淺色主題 */
    .stApp {
        background-color: #f8fafc !important;
        color: #0f172a !important;
        font-family: 'Outfit', 'Noto Sans TC', sans-serif !important;
    }
    
    /* 頂部導覽列 (Header Bar) */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 20px;
        background-color: #ffffff;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 20px;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .header-logo {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .header-logo-icon {
        color: #db2777;
        font-size: 1.5rem;
    }
    
    .header-logo-text {
        font-size: 1.25rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    .header-logo-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-left: 8px;
    }
    
    .badge-webgl {
        background-color: #fdf2f8;
        color: #db2777;
        border: 1px solid #fbcfe8;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* 欄位控制面板標題 */
    .panel-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 14px;
        padding-bottom: 6px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* 設定區塊卡片 (左側面板) */
    .config-section {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    
    .config-section-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #475569;
        margin-bottom: 12px;
    }
    
    /* 步驟選擇盒樣式 (比照原圖的 STEP1/STEP2 樣式) */
    .step-box {
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    
    .step-box-active {
        border: 1px solid #db2777;
        background-color: #fdf2f8;
        color: #9d174d;
    }
    
    .step-box-inactive {
        border: 1px solid #e2e8f0;
        background-color: #f8fafc;
        color: #64748b;
    }
    
    /* 右側學術說明面板 */
    .academic-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1e293b;
        margin-top: 10px;
        margin-bottom: 8px;
    }
    
    .academic-text {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.5;
        margin-bottom: 12px;
    }
    
    /* 粉紅色提示盒 (比照原圖的警告與提示樣式) */
    .pink-callout {
        background-color: #fdf2f8;
        border-left: 4px solid #db2777;
        color: #9d174d;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        font-size: 0.88rem;
        line-height: 1.5;
        margin-top: 15px;
    }
    
    /* 中間圖表區底部的浮動說明 */
    .floating-helper {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.8rem;
        color: #475569;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        text-align: center;
        width: fit-content;
        margin: 10px auto 0 auto;
    }
    
    /* 數據面板小指標 */
    .light-metric-container {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
    }
    
    .light-metric-box {
        flex: 1;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 8px;
        text-align: center;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.01);
    }
    
    .light-metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #db2777;
    }
    
    .light-metric-label {
        font-size: 0.7rem;
        color: #64748b;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- 頂部導覽列 (Header Bar) ---
st.markdown("""
    <div class="header-bar">
        <div class="header-logo">
            <span class="header-logo-icon">⚡</span>
            <span class="header-logo-text">SVM 3D Interactive Studio</span>
            <span class="header-logo-sub">Support Vector Machine & Kernel Trick Visualizer</span>
        </div>
        <div class="badge-webgl">WebGL 3D</div>
    </div>
""", unsafe_allow_html=True)

# 初始化步驟狀態
if 'step' not in st.session_state:
    st.session_state.step = 1

# --- 三欄排版配置 ---
left_col, center_col, right_col = st.columns([1.1, 2.5, 1.1])

# ==========================================
# 1. 左側：控制面板 (Left Column)
# ==========================================
with left_col:
    st.markdown('<div class="panel-title">⚙️ 控制面板</div>', unsafe_allow_html=True)
    
    # 區塊 1：資料集設定
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.markdown('<div class="config-section-title">1. 資料集設定 (Concentric Circles)</div>', unsafe_allow_html=True)
    
    num_points = st.slider("樣本點數量 (Samples)", min_value=40, max_value=300, value=200, step=10)
    dataset_noise = st.slider("雜訊干擾度 (Noise)", min_value=0.0, max_value=0.3, value=0.05, step=0.01)
    
    # 用於觸發隨機種子更新的按鈕
    if st.button("🔄 重新產生資料", use_container_width=True):
        if 'seed_val' not in st.session_state:
            st.session_state.seed_val = 7
        st.session_state.seed_val = (st.session_state.seed_val + 17) % 9999
    
    if 'seed_val' not in st.session_state:
        st.session_state.seed_val = 7
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 載入快取資料
    X, y = get_cached_dataset(num_points, dataset_noise, st.session_state.seed_val)
    
    # 區塊 2：機器學習與高維投影步驟
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.markdown('<div class="config-section-title">2. 機器學習與高維投影步驟</div>', unsafe_allow_html=True)
    
    # 步驟 1 按鈕
    if st.button("STEP 1\n原始 2D 空間 (線性不可分)", key="step1_btn", use_container_width=True):
        st.session_state.step = 1
    
    # 步驟 2 按鈕
    if st.button("STEP 2\nZ = X² + Y² 非線性映射", key="step2_btn", use_container_width=True):
        st.session_state.step = 2
        
    # 用於呈現當前選中步驟的提示框
    if st.session_state.step == 1:
        st.markdown('<div class="step-box step-box-active">📍 當前展示：STEP 1 (2D 原始平面)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="step-box step-box-active">📍 當前展示：STEP 2 (3D 投影空間)</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 區塊 3：視覺化細節控制 (開關選項)
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.markdown('<div class="config-section-title">3. 視覺化模型控制</div>', unsafe_allow_html=True)
    
    # 這些選項只有在 STEP 2 時才能被操作，STEP 1 時為禁用狀態
    step_disabled = (st.session_state.step == 1)
    
    show_hyperplane = st.toggle("3D 分類超平面 (Hyperplane)", value=False, disabled=step_disabled, help="顯示將兩類分割開來的平面判定面。")
    show_sv = st.toggle("顯示支持向量 (Support Vectors)", value=False, disabled=step_disabled, help="高亮標記決定決策邊界的邊緣關鍵樣本點。")
    show_margin = st.toggle("顯示最大邊界間隔 (Margin)", value=False, disabled=step_disabled, help="顯示決策邊界左右的最優分類寬度間隔面。")
    show_rbf_surface = st.toggle("RBF 徑向基底高斯核函數", value=False, disabled=step_disabled, help="切換至實際以 RBF Kernel 訓練的 SVM 決策分數曲面 f(x, y)。")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 當 RBF 核開關打開時，顯示 C 與 Gamma 參數調校滑桿
    if show_rbf_surface and st.session_state.step == 2:
        st.markdown('<div class="config-section">', unsafe_allow_html=True)
        st.markdown('<div class="config-section-title">4. RBF 核心參數調校</div>', unsafe_allow_html=True)
        C_param = st.slider("正則化參數 (C)", min_value=0.1, max_value=100.0, value=10.0, step=0.1)
        gamma_param = st.slider("核心係數 (Gamma)", min_value=0.01, max_value=10.0, value=1.0, step=0.01)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        C_param = 10.0
        gamma_param = 1.0

# ==========================================
# 2. 中間：3D 視覺化圖表與數據 (Center Column)
# ==========================================
with center_col:
    # 數據指標小看板
    if show_rbf_surface and st.session_state.step == 2:
        model = train_svm(X, y, kernel='rbf', C=C_param, gamma=gamma_param)
        y_pred = model.predict(X)
        acc = accuracy_score(y, y_pred)
        n_sv = len(model.support_vectors_)
        
        st.markdown(f"""
            <div class="light-metric-container">
                <div class="light-metric-box">
                    <div class="light-metric-value">RBF SVM</div>
                    <div class="light-metric-label">當前模型</div>
                </div>
                <div class="light-metric-box">
                    <div class="light-metric-value">{acc * 100:.1f}%</div>
                    <div class="light-metric-label">訓練準確度</div>
                </div>
                <div class="light-metric-box">
                    <div class="light-metric-value">{n_sv}</div>
                    <div class="light-metric-label">支持向量個數</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # 計算 Z 軸映射坐標與表面
    grid_res = 85
    xx, yy, grid_points = make_decision_grid(X, resolution=grid_res, padding=0.5)
    
    # 初始化 3D 繪圖
    fig_3d = go.Figure()
    
    # 決定每個點的 Z 軸高度
    if st.session_state.step == 1:
        # STEP 1: 原始平面，Z 全部為 0
        z_points = np.zeros(X.shape[0])
        z_min, z_max = -0.5, 3.5
    else:
        # STEP 2: 高維投影
        if show_rbf_surface:
            # 訓練 RBF SVM，Z 軸使用決策分數 f(x, y)
            model = train_svm(X, y, kernel='rbf', C=C_param, gamma=gamma_param)
            z_points = model.decision_function(X)
            Z_grid = compute_decision_surface(model, grid_points, resolution=grid_res)
            z_min, z_max = Z_grid.min() - 0.5, Z_grid.max() + 0.5
            
            # 繪製 RBF 決策評分表面
            fig_3d.add_trace(go.Surface(
                x=np.linspace(xx.min(), xx.max(), grid_res),
                y=np.linspace(yy.min(), yy.max(), grid_res),
                z=Z_grid,
                colorscale="RdBu",
                opacity=0.45,
                showscale=False,
                name="決策函數曲面"
            ))
            
            # 若啟用超平面 (RBF 時，邊界平面為 z = 0)
            if show_hyperplane:
                z_plane = np.zeros_like(xx)
                fig_3d.add_trace(go.Surface(
                    x=np.linspace(xx.min(), xx.max(), grid_res),
                    y=np.linspace(yy.min(), yy.max(), grid_res),
                    z=z_plane,
                    colorscale=[[0, 'rgba(236, 72, 153, 0.35)'], [1, 'rgba(236, 72, 153, 0.35)']],
                    opacity=0.3,
                    showscale=False,
                    name="z=0 超平面"
                ))
                
            # 若啟用最大邊界間隔 (RBF 時，間隔為 z = -1 與 z = 1)
            if show_margin:
                for z_val, color in [(-1.0, 'rgba(239, 68, 68, 0.15)'), (1.0, 'rgba(59, 130, 246, 0.15)')]:
                    z_margin_plane = np.full_like(xx, z_val)
                    fig_3d.add_trace(go.Surface(
                        x=np.linspace(xx.min(), xx.max(), grid_res),
                        y=np.linspace(yy.min(), yy.max(), grid_res),
                        z=z_margin_plane,
                        colorscale=[[0, color], [1, color]],
                        opacity=0.2,
                        showscale=False,
                        name=f"間隔面 z={z_val}"
                    ))
        else:
            # 原始拋物線映射 Z = X^2 + Y^2
            z_points = X[:, 0]**2 + X[:, 1]**2
            Z_grid = xx**2 + yy**2
            z_min, z_max = 0.0, 7.5
            
            # 繪製拋物線表面
            fig_3d.add_trace(go.Surface(
                x=np.linspace(xx.min(), xx.max(), grid_res),
                y=np.linspace(yy.min(), yy.max(), grid_res),
                z=Z_grid,
                colorscale="Blues",
                opacity=0.25,
                showscale=False,
                name="映射拋物面"
            ))
            
            # 若啟用分類超平面 (拋物線映射時，分類超平面設定在 z = 2.0)
            if show_hyperplane:
                z_plane = np.full_like(xx, 2.0)
                fig_3d.add_trace(go.Surface(
                    x=np.linspace(xx.min(), xx.max(), grid_res),
                    y=np.linspace(yy.min(), yy.max(), grid_res),
                    z=z_plane,
                    colorscale=[[0, 'rgba(236, 72, 153, 0.35)'], [1, 'rgba(236, 72, 153, 0.35)']],
                    opacity=0.35,
                    showscale=False,
                    name="超平面 z=2.0"
                ))
                
            # 若啟用最大邊界間隔 (拋物線映射時，間隔定義在 z = 1.0 與 z = 3.0)
            if show_margin:
                for z_val, color in [(1.0, 'rgba(239, 68, 68, 0.15)'), (3.0, 'rgba(59, 130, 246, 0.15)')]:
                    z_margin_plane = np.full_like(xx, z_val)
                    fig_3d.add_trace(go.Surface(
                        x=np.linspace(xx.min(), xx.max(), grid_res),
                        y=np.linspace(yy.min(), yy.max(), grid_res),
                        z=z_margin_plane,
                        colorscale=[[0, color], [1, color]],
                        opacity=0.2,
                        showscale=False,
                        name=f"間隔面 z={z_val}"
                    ))
                    
    # 繪製資料點 3D 散佈
    idx0 = (y == 0)
    idx1 = (y == 1)
    
    # 類別 0 (內圈，藍色點)
    fig_3d.add_trace(go.Scatter3d(
        x=X[idx0, 0], y=X[idx0, 1], z=z_points[idx0],
        mode="markers",
        name="藍色樣本 (內圈)",
        marker=dict(color="#3b82f6", size=5, line=dict(color="#1e3a8a", width=0.5))
    ))
    
    # 類別 1 (外圈，紅色點)
    fig_3d.add_trace(go.Scatter3d(
        x=X[idx1, 0], y=X[idx1, 1], z=z_points[idx1],
        mode="markers",
        name="紅色樣本 (外圈)",
        marker=dict(color="#ef4444", size=5, line=dict(color="#7f1d1d", width=0.5))
    ))
    
    # 若啟用支持向量標記高亮
    if show_sv and st.session_state.step == 2:
        if show_rbf_surface:
            # RBF 模型的實體支持向量索引
            sv_indices = model.support_
            fig_3d.add_trace(go.Scatter3d(
                x=X[sv_indices, 0], y=X[sv_indices, 1], z=z_points[sv_indices],
                mode="markers",
                name="支持向量",
                marker=dict(symbol="circle", color="rgba(0,0,0,0)", size=7.5, line=dict(color="#fbbf24", width=3))
            ))
        else:
            # 拋物線幾何映射時，支持向量為靠近邊緣平面 z=2.0 附近的點 (1.0 <= z <= 3.0)
            sv_mask = (z_points >= 1.0) & (z_points <= 3.0)
            fig_3d.add_trace(go.Scatter3d(
                x=X[sv_mask, 0], y=X[sv_mask, 1], z=z_points[sv_mask],
                mode="markers",
                name="支持向量 (幾何邊界點)",
                marker=dict(symbol="circle", color="rgba(0,0,0,0)", size=7.5, line=dict(color="#fbbf24", width=3))
            ))
            
    # 設定 Plotly 3D 圖表版面 (淺色極簡風)
    fig_3d.update_layout(
        margin=dict(l=0, r=0, b=0, t=10),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#475569")),
        scene=dict(
            xaxis=dict(
                title="X", backgroundcolor="#f8fafc", gridcolor="#e2e8f0", 
                zerolinecolor="#cbd5e1", showbackground=True, tickfont=dict(color="#475569")
            ),
            yaxis=dict(
                title="Y", backgroundcolor="#f8fafc", gridcolor="#e2e8f0", 
                zerolinecolor="#cbd5e1", showbackground=True, tickfont=dict(color="#475569")
            ),
            zaxis=dict(
                title="Z (決策高度)", backgroundcolor="#f8fafc", gridcolor="#e2e8f0", 
                zerolinecolor="#cbd5e1", showbackground=True, tickfont=dict(color="#475569"),
                range=[z_min, z_max]
            ),
            camera=dict(
                eye=dict(x=1.35, y=1.35, z=0.85)
            )
        ),
        height=620
    )
    
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # 底部浮動說明標記
    st.markdown('<div class="floating-helper">🔄 滑鼠拖曳旋轉 3D 空間，滾輪縮放視角</div>', unsafe_allow_html=True)

# ==========================================
# 3. 右側：學術原理與回饋 (Right Column)
# ==========================================
with right_col:
    st.markdown('<div class="panel-title">📖 學術原理說明</div>', unsafe_allow_html=True)
    
    if st.session_state.step == 1:
        st.markdown('<div class="academic-title">Step 1: 原始 2D 空間</div>', unsafe_allow_html=True)
        st.markdown("""
        在此空間中，資料呈現同心圓分佈：
        
        * **藍色樣本** 位於內部核心區域。
        * **紅色樣本** 形成外部包圍圈。
        
        由於環狀幾何特徵無法被任何一條實體線分割，因此稱作 **線性不可分 (Linearly Non-separable)**。
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="pink-callout">
                線性 SVM 在此空間中會遭遇失敗，必須進行非線性變革！
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown('<div class="academic-title">Step 2: 高維空間映射與分類</div>', unsafe_allow_html=True)
        
        if show_rbf_surface:
            st.markdown("""
            藉由訓練 RBF 核函數 SVM，模型在隱式的高維希爾伯特空間中拉大邊界。
            
            * 3D 曲面展示了決策值得分 $f(x, y)$。
            * 當 $f(x, y) = 0$ 時即為黃色決策邊界面。
            * 大於 $0$ 分入紅色類別，小於 $0$ 分入藍色類別。
            """, unsafe_allow_html=True)
            
            # C與Gamma即時教學解讀
            if C_param > 20:
                st.markdown("⚠️ **C 值偏大**：分類邊界變嚴格，試圖排除所有噪聲，這會使邊隔帶縮小。")
            if gamma_param > 3.0:
                st.markdown("⚠️ **Gamma 偏高**：曲面出現多個局部突刺，模型開始過擬合 (Overfitting) 單個資料點。")
        else:
            st.markdown("""
            藉由映射函數：
            $$\phi(x, y) = (x, y, x^2 + y^2)$$
            
            每個點根據其與原點的距離被「向上拉升」。距離越遠，上升越高。
            
            * 藍色中心點留在低處。
            * 紅色邊緣點升至高處。
            
            此時，兩類資料點變得線性可分。
            """, unsafe_allow_html=True)
            
        st.markdown("""
            <div class="pink-callout">
                在 3D 特徵空間中，可以使用平坦的超平面（例如粉紅色的平面）將兩類樣本完美切開！
            </div>
        """, unsafe_allow_html=True)


