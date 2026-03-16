# ============================================
# [01] Imports
# ============================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from streamlit_autorefresh import st_autorefresh

# ============================================
# [02] 基本設定
# ============================================
# 每 60000 毫秒 (60秒) 自動重整一次頁面
st_autorefresh(interval=60000, key="data_refresh")

st.set_page_config(
    page_title="三均線策略實盤分析",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# [03] 全站黑色主題 + Dashboard 風格 CSS
# ============================================
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #050505 !important;
    color: #F3F4F6 !important;
    font-family: "Segoe UI", "Microsoft JhengHei", sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(75, 85, 99, 0.12), transparent 30%),
        radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 25%),
        linear-gradient(180deg, #070707 0%, #050505 100%) !important;
}

.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 1.2rem !important;
    max-width: 1500px !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.dashboard-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 1.5rem;
    letter-spacing: 0.3px;
}

.panel {
    background: linear-gradient(180deg, rgba(19,19,22,0.96) 0%, rgba(10,10,12,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 18px 20px;
    box-shadow:
        0 12px 40px rgba(0,0,0,0.45),
        inset 0 1px 0 rgba(255,255,255,0.04);
    margin-bottom: 18px;
}

.panel-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: #F9FAFB;
    margin-bottom: 4px;
}

.panel-subtitle {
    font-size: 0.86rem;
    color: #9CA3AF;
    margin-bottom: 12px;
}

.kpi-card {
    background: linear-gradient(180deg, rgba(20,20,24,0.98) 0%, rgba(10,10,12,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 18px 18px;
    min-height: 124px;
    box-shadow:
        0 10px 30px rgba(0,0,0,0.38),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

.kpi-label {
    font-size: 0.92rem;
    color: #A1A1AA;
    margin-bottom: 10px;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #F9FAFB;
    line-height: 1.15;
    margin-bottom: 8px;
}

/* 台灣習慣：紅正綠負 */
.text-red { color: #F87171 !important; }
.text-green { color: #34D399 !important; }
.text-blue { color: #60A5FA !important; }
.text-purple { color: #A78BFA !important; }
.text-orange { color: #FBBF24 !important; }
.text-white { color: #FFFFFF !important; }

.kpi-foot {
    font-size: 0.82rem;
    color: #71717A;
}

.info-badge {
    display: inline-block;
    background: rgba(34,197,94,0.12);
    border: 1px solid rgba(34,197,94,0.22);
    color: #86EFAC;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 8px;
}

.info-badge-blue {
    display: inline-block;
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.22);
    color: #93C5FD;
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    margin-right: 8px;
}

/* 深色表格專屬 CSS */
.dark-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.9rem;
}
.dark-table th {
    background-color: rgba(255, 255, 255, 0.03);
    color: #A1A1AA;
    padding: 14px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    font-weight: 600;
}
.dark-table td {
    padding: 14px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #E5E7EB;
}
.dark-table tr:hover {
    background-color: rgba(255, 255, 255, 0.04);
}
</style>
""", unsafe_allow_html=True)

# 格式化金額：紅正綠負，加上加號與減號
def format_currency_tw(val):
    if val > 0:
        return f'<span class="text-red">+${val:,.0f}</span>'
    elif val < 0:
        return f'<span class="text-green">-${abs(val):,.0f}</span>'
    else:
        return f'<span style="color: #A1A1AA;">$0</span>'

# ============================================
# [04] 資料讀取與處理
# ============================================
@st.cache_data(ttl=60)
def load_data():
    # 使用相對路徑，確保 GitHub / Streamlit Cloud 可以讀到
    file_path = "三均線_signal_trades.csv"
    
    if not os.path.exists(file_path):
        return pd.DataFrame()
        
    df = pd.read_csv(file_path)
    
    # 時間格式轉換
    df['entry_time'] = pd.to_datetime(df['entry_time'])
    df['exit_time'] = pd.to_datetime(df['exit_time'])
    
    # 確保依照出場時間排序，避免資金曲線錯亂
    df = df.sort_values('exit_time').reset_index(drop=True)
    
    # 計算時間維度與進階指標
    df['duration'] = df['exit_time'] - df['entry_time']
    df['cum_pnl'] = df['export_net_pnl'].cumsum()
    df['cum_peak'] = df['cum_pnl'].cummax()
    df['drawdown'] = df['cum_pnl'] - df['cum_peak']
    
    # 日期文字 (提供圖表使用)
    df["日期文字"] = df["exit_time"].dt.strftime("%Y-%m-%d %H:%M")
    df["Hover顯示"] = df["export_net_pnl"].apply(lambda x: f"+{x:,.0f}" if x > 0 else (f"-{abs(x):,.0f}" if x < 0 else "0"))
    
    return df

# ============================================
# [05] Dashboard 頂部 & 側邊欄
# ============================================
st.markdown('<div class="dashboard-title">📈 三均線策略---最新實單績效分析</div>', unsafe_allow_html=True)

df = load_data()

if df.empty:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">找不到資料</div>
        <div class="panel-subtitle">找不到 `三均線_signal_trades.csv`，請確認檔案是否有上傳至同一個資料夾中。</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 側邊欄篩選
st.sidebar.markdown('<h2 style="color:white;">🔍 策略分析篩選</h2>', unsafe_allow_html=True)
selected_dir = st.sidebar.multiselect(
    "選擇交易方向 (LONG / SHORT)", 
    options=df['entry_dir'].unique(), 
    default=df['entry_dir'].unique()
)

if st.sidebar.button("🔄 獲取最新資料 (重整)"):
    st.cache_data.clear()
    st.rerun()

# 套用篩選
filtered_df = df[df['entry_dir'].isin(selected_dir)].copy()
if filtered_df.empty:
    st.warning("您取消了所有方向的勾選，無資料可顯示。")
    st.stop()

# 重新計算篩選後的資金曲線與回撤
filtered_df = filtered_df.sort_values('exit_time').reset_index(drop=True)
filtered_df['cum_pnl'] = filtered_df['export_net_pnl'].cumsum()
filtered_df['cum_peak'] = filtered_df['cum_pnl'].cummax()
filtered_df['drawdown'] = filtered_df['cum_pnl'] - filtered_df['cum_peak']

# ============================================
# [06] 核心 KPI 運算與展示
# ============================================
total_pnl = filtered_df["export_net_pnl"].sum()
total_trades = len(filtered_df)
win_trades = (filtered_df["export_net_pnl"] > 0).sum()
loss_trades = (filtered_df["export_net_pnl"] < 0).sum()
flat_trades = (filtered_df["export_net_pnl"] == 0).sum()
win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0

running_days = (filtered_df["exit_time"].max() - filtered_df["entry_time"].min()).days
running_days = max(running_days, 1) # 避免0天

avg_win = filtered_df.loc[filtered_df["export_net_pnl"] > 0, "export_net_pnl"].mean()
avg_loss = filtered_df.loc[filtered_df["export_net_pnl"] < 0, "export_net_pnl"].mean()
avg_win = 0 if pd.isna(avg_win) else avg_win
avg_loss = 0 if pd.isna(avg_loss) else avg_loss

payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
profit_factor = filtered_df.loc[filtered_df["export_net_pnl"] > 0, "export_net_pnl"].sum() / abs(filtered_df.loc[filtered_df["export_net_pnl"] < 0, "export_net_pnl"].sum()) if avg_loss != 0 else float('inf')
max_drawdown = filtered_df['drawdown'].min()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">總累計淨損益</div>
        <div class="kpi-value">{format_currency_tw(total_pnl)}</div>
        <div class="kpi-foot">扣除滑價後淨利</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">總交易次數 (勝率)</div>
        <div class="kpi-value text-blue">{total_trades} <span style='font-size:1.1rem; color:#A78BFA'>({win_rate:.1f}%)</span></div>
        <div class="kpi-foot">完整平倉趟數</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">最大連續回撤 (MDD)</div>
        <div class="kpi-value text-green">-${abs(max_drawdown):,.0f}</div>
        <div class="kpi-foot">資金曲線歷史最大跌幅</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">盈虧比 (Payoff)</div>
        <div class="kpi-value text-orange">{payoff_ratio:.2f}</div>
        <div class="kpi-foot">均盈 / 均虧</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    pf_color = "text-red" if profit_factor > 1.5 else "text-orange" if profit_factor > 1 else "text-green"
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">獲利因子 (Profit Factor)</div>
        <div class="kpi-value {pf_color}">{profit_factor:.2f}</div>
        <div class="kpi-foot">總獲利 / 總虧損</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ============================================
# [07] 中段圖表：主圖 (資金曲線) & 統計面板
# ============================================
left_col, right_col = st.columns([2.3, 1])

with left_col:
    st.markdown("""
    <div class="panel" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border-bottom: none;">
        <div class="panel-title">累計資金曲線 (Equity Curve)</div>
        <div class="panel-subtitle" style="margin-bottom: 0px;">
            <span class="info-badge">策略淨值</span>
            <span class="info-badge-blue">扣除滑價</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_equity = go.Figure()
    
    # 新增資金曲線
    fig_equity.add_trace(go.Scatter(
        x=filtered_df["日期文字"],
        y=filtered_df["cum_pnl"],
        text=filtered_df["Hover顯示"],
        mode="lines",
        line=dict(color="#8B5CF6", width=4), # 科技紫
        name="累計損益",
        hovertemplate="<b>%{x}</b><br>累計損益: %{y:,.0f}<br>單趟: %{text}<extra></extra>"
    ))

    fig_equity.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=18, r=18, t=10, b=18),
        paper_bgcolor="rgba(19,19,22,0.96)", 
        plot_bgcolor="rgba(19,19,22,0.96)",
        xaxis=dict(
            title="",
            type="category",
            showgrid=False,
            tickfont=dict(size=12, color="#A1A1AA"),
            showline=False,
            zeroline=False,
            nticks=10 # 避免X軸日期擠在一起
        ),
        yaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.08)",
            tickfont=dict(size=12, color="#A1A1AA"),
            zeroline=True,
            zerolinecolor="rgba(255,255,255,0.2)",
            separatethousands=True
        ),
        showlegend=False
    )
    st.plotly_chart(fig_equity, use_container_width=True, config={'displayModeBar': False})

with right_col:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">策略維度分析</div>
        <div class="panel-subtitle">勝敗場與平均時長</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom:14px;">
        <div class="kpi-label">勝 / 敗 / 平</div>
        <div class="kpi-value" style="font-size:1.55rem;"><span class="text-red">{win_trades}</span> / <span class="text-green">{loss_trades}</span> / {flat_trades}</div>
        <div class="kpi-foot">依單筆損益統計</div>
    </div>
    """, unsafe_allow_html=True)

    avg_duration = filtered_df['duration'].mean()
    duration_str = f"{avg_duration.components.hours}小時 {avg_duration.components.minutes}分" if not pd.isna(avg_duration) else "N/A"

    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom:14px;">
        <div class="kpi-label">平均持倉時間</div>
        <div class="kpi-value" style="font-size:1.55rem; color:#60A5FA;">{duration_str}</div>
        <div class="kpi-foot">進場至出場時間差</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# [08] 下半部：多空分析與出場理由分佈
# ============================================
st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("""
    <div class="panel" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border-bottom: none;">
        <div class="panel-title">LONG vs SHORT 績效貢獻</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 計算多空的總獲利
    dir_pnl = filtered_df.groupby('entry_dir')['export_net_pnl'].sum().reset_index()
    # 給予對應顏色 (LONG 多為紅色系，SHORT 多為綠色系)
    dir_pnl['color'] = dir_pnl['entry_dir'].map({'LONG': '#F87171', 'SHORT': '#34D399'})
    
    fig_dir = go.Figure(go.Bar(
        x=dir_pnl['entry_dir'],
        y=dir_pnl['export_net_pnl'],
        marker_color=dir_pnl['color'],
        text=dir_pnl['export_net_pnl'].apply(lambda x: f"${x:,.0f}"),
        textposition='auto',
        hovertemplate="%{x}: %{y:,.0f}<extra></extra>"
    ))
    fig_dir.update_layout(
        template="plotly_dark", height=300, margin=dict(l=18, r=18, t=10, b=18),
        paper_bgcolor="rgba(19,19,22,0.96)", plot_bgcolor="rgba(19,19,22,0.96)",
        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(255,255,255,0.08)", zeroline=True)
    )
    st.plotly_chart(fig_dir, use_container_width=True, config={'displayModeBar': False})

with col_b2:
    st.markdown("""
    <div class="panel" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border-bottom: none;">
        <div class="panel-title">出場理由觸發佔比</div>
    </div>
    """, unsafe_allow_html=True)
    
    exit_counts = filtered_df['exit_reason'].value_counts().reset_index()
    exit_counts.columns = ['exit_reason', 'count']
    
    fig_exit = px.pie(
        exit_counts, values='count', names='exit_reason', hole=0.4,
        color_discrete_sequence=px.colors.sequential.Tealgrn
    )
    fig_exit.update_layout(
        template="plotly_dark", height=300, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(19,19,22,0.96)", plot_bgcolor="rgba(19,19,22,0.96)",
        showlegend=False
    )
    fig_exit.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_exit, use_container_width=True, config={'displayModeBar': False})


# ============================================
# [09] 底部：自訂義深色表格 (最新交易明細)
# ============================================
st.markdown("<br>", unsafe_allow_html=True)

table_html = """
<div class="panel" style="padding: 0; overflow: hidden;">
    <div style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.05);">
        <span style="font-size: 1.05rem; font-weight: 700; color: #F9FAFB;"> 最新 10 筆平倉紀錄明細</span>
    </div>
    <div style="overflow-x: auto;">
        <table class="dark-table">
            <thead>
                <tr>
                    <th>進場時間</th>
                    <th>出場時間</th>
                    <th>方向</th>
                    <th>進場價</th>
                    <th>出場價</th>
                    <th>淨損益 (NTD)</th>
                    <th>出場原因</th>
                </tr>
            </thead>
            <tbody>
"""

# 取最新 10 筆 (根據時間倒序)
recent_trades = filtered_df.tail(10).iloc[::-1].reset_index(drop=True)

for _, row in recent_trades.iterrows():
    en_time = row['entry_time'].strftime('%m-%d %H:%M') if pd.notnull(row['entry_time']) else "N/A"
    ex_time = row['exit_time'].strftime('%m-%d %H:%M') if pd.notnull(row['exit_time']) else "N/A"
    
    dir_val = row.get('entry_dir', '')
    if dir_val == 'LONG':
        dir_str = "<span class='text-red'>多 (LONG)</span>"
    elif dir_val == 'SHORT':
        dir_str = "<span class='text-green'>空 (SHORT)</span>"
    else:
        dir_str = dir_val
        
    en_price = f"{row.get('entry_price', 0):,.0f}"
    ex_price = f"{row.get('exit_price', 0):,.0f}"
    pnl = row.get('export_net_pnl', 0)
    pnl_str = format_currency_tw(pnl)
    
    reason = str(row.get('exit_reason', ''))
    # 縮短太長的理由文字避免跑版
    if len(reason) > 20: reason = reason[:20] + "..."
    
    table_html += f"<tr><td>{en_time}</td><td>{ex_time}</td><td>{dir_str}</td><td>{en_price}</td><td>{ex_price}</td><td><b>{pnl_str}</b></td><td>{reason}</td></tr>"

table_html += """
            </tbody>
        </table>
    </div>
</div>
"""

st.markdown(table_html, unsafe_allow_html=True)
