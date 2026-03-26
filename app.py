# ============================================
# [01] Imports
# ============================================
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import calendar
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

# ============================================
# [02] 基本設定
# ============================================
# 每 60000 毫秒 (60秒) 自動重整一次頁面
st_autorefresh(interval=60000, key="data_refresh")

st.set_page_config(
    page_title="三均線策略實盤分析",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    max-width: 1700px !important;
}

/* 隱藏預設 Header / Footer */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
[data-testid="collapsedControl"] {display: none;}

.dashboard-title {
    font-size: 2.1rem;
    font-weight: 800;
    color: #FFFFFF;
    margin-bottom: 0.8rem;
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
    padding: 16px 16px;
    min-height: 124px;
    box-shadow:
        0 10px 30px rgba(0,0,0,0.38),
        inset 0 1px 0 rgba(255,255,255,0.04);
}

.kpi-label {
    font-size: 0.92rem;
    color: #A1A1AA;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: #F9FAFB;
    line-height: 1.15;
    margin-bottom: 6px;
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

/* 深色表格 */
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

/* 月曆樣式 */
.calendar-wrap {
    display: grid;
    grid-template-columns: 1fr 220px;
    gap: 14px;
    align-items: start;
}

.calendar-grid {
    width: 100%;
    border-collapse: separate;
    border-spacing: 8px;
}

.calendar-grid th {
    color: #A1A1AA;
    font-size: 0.86rem;
    font-weight: 600;
    text-align: center;
    padding-bottom: 4px;
}

.calendar-cell {
    height: 110px;
    vertical-align: top;
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.08);
    padding: 10px;
    background: rgba(18,18,20,0.95);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

.calendar-empty {
    height: 110px;
    border-radius: 14px;
    background: rgba(255,255,255,0.015);
    border: 1px solid rgba(255,255,255,0.03);
}

.day-num {
    font-size: 0.86rem;
    color: #D1D5DB;
    margin-bottom: 8px;
}

.day-pnl {
    font-size: 1.15rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 4px;
}

.day-sub {
    font-size: 0.78rem;
    color: #C4C7CF;
    line-height: 1.35;
}

.cal-pos-1 { background: rgba(16, 185, 129, 0.16); }
.cal-pos-2 { background: rgba(16, 185, 129, 0.24); }
.cal-pos-3 { background: rgba(16, 185, 129, 0.34); }

.cal-neg-1 { background: rgba(239, 68, 68, 0.16); }
.cal-neg-2 { background: rgba(239, 68, 68, 0.24); }
.cal-neg-3 { background: rgba(239, 68, 68, 0.34); }

.week-side-card {
    background: linear-gradient(180deg, rgba(20,20,24,0.98) 0%, rgba(10,10,12,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 10px;
}

.week-side-title {
    font-size: 0.82rem;
    color: #E5E7EB;
    margin-bottom: 6px;
}

.week-side-pnl {
    font-size: 1.35rem;
    font-weight: 800;
    margin-bottom: 4px;
}

.week-side-sub {
    font-size: 0.78rem;
    color: #A1A1AA;
}

.ctrl-label {
    font-size: 0.92rem;
    color: #D1D5DB;
    font-weight: 600;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# [04] 共用函式
# ============================================
def format_currency_tw(val):
    if val > 0:
        return f'<span class="text-red">+${val:,.0f}</span>'
    elif val < 0:
        return f'<span class="text-green">-${abs(val):,.0f}</span>'
    else:
        return f'<span style="color: #A1A1AA;">$0</span>'

def format_currency_text(val):
    if val > 0:
        return f"+${val:,.0f}"
    elif val < 0:
        return f"-${abs(val):,.0f}"
    else:
        return "$0"

def pnl_text_class(val):
    return "text-red" if val > 0 else ("text-green" if val < 0 else "text-white")

def get_period_start(latest_dt, period_label):
    if period_label == "近1個月":
        return latest_dt - pd.DateOffset(months=1)
    elif period_label == "近3個月":
        return latest_dt - pd.DateOffset(months=3)
    elif period_label == "近9個月":
        return latest_dt - pd.DateOffset(months=9)
    elif period_label == "近12個月":
        return latest_dt - pd.DateOffset(months=12)
    else:
        return None

def get_month_options(df):
    if df.empty:
        return []
    months = (
        df["exit_time"]
        .dt.to_period("M")
        .astype(str)
        .drop_duplicates()
        .sort_values(ascending=False)
        .tolist()
    )
    return months

def calendar_intensity_class(val, max_abs):
    if pd.isna(val) or val == 0 or max_abs <= 0:
        return ""
    ratio = abs(val) / max_abs
    if ratio < 0.33:
        level = 1
    elif ratio < 0.66:
        level = 2
    else:
        level = 3
    return f"cal-pos-{level}" if val > 0 else f"cal-neg-{level}"

def build_monthly_calendar_html(month_df, selected_month_str):
    if selected_month_str is None:
        return "<div class='panel'>無可顯示月份</div>"

    year, month = map(int, selected_month_str.split("-"))
    month_df = month_df.copy()
    month_df["exit_date"] = month_df["exit_time"].dt.date

    daily = month_df.groupby("exit_date").agg(
        day_pnl=("export_net_pnl", "sum"),
        trades=("export_net_pnl", "size"),
        win_rate=("export_net_pnl", lambda s: (s.gt(0).mean() * 100) if len(s) > 0 else 0)
    ).reset_index()

    daily_map = {
        row["exit_date"]: {
            "pnl": row["day_pnl"],
            "trades": int(row["trades"]),
            "win_rate": row["win_rate"]
        }
        for _, row in daily.iterrows()
    }

    cal = calendar.Calendar(firstweekday=6)  # Sun first
    weeks = cal.monthdatescalendar(year, month)

    month_pnls = [v["pnl"] for v in daily_map.values()] if daily_map else [0]
    max_abs = max(abs(x) for x in month_pnls) if month_pnls else 0

    month_title_dt = datetime(year, month, 1)
    month_title = month_title_dt.strftime("%Y-%m")

    html = f"""
    <div class="panel">
        <div class="panel-title">每日績效月曆</div>
        <div class="panel-subtitle">
            觀察每日損益、交易次數、勝率分布（月曆視圖）
        </div>
        <div style="font-size:1.15rem;font-weight:800;margin-bottom:10px;">{month_title}</div>
        <div class="calendar-wrap">
            <div>
                <table class="calendar-grid">
                    <thead>
                        <tr>
                            <th>Sun</th>
                            <th>Mon</th>
                            <th>Tue</th>
                            <th>Wed</th>
                            <th>Thu</th>
                            <th>Fri</th>
                            <th>Sat</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    week_cards = []

    for w_idx, week in enumerate(weeks, start=1):
        html += "<tr>"
        week_pnl = 0
        week_days_with_trade = 0

        for day in week:
            if day.month != month:
                html += "<td class='calendar-empty'></td>"
                continue

            day_info = daily_map.get(day, None)

            if day_info is None:
                html += f"""
                <td class="calendar-cell">
                    <div class="day-num">{day.day}</div>
                </td>
                """
            else:
                pnl = day_info["pnl"]
                trades = day_info["trades"]
                wr = day_info["win_rate"]
                cls = calendar_intensity_class(pnl, max_abs)
                pnl_cls = pnl_text_class(pnl)

                week_pnl += pnl
                week_days_with_trade += 1

                html += f"""
                <td class="calendar-cell {cls}">
                    <div class="day-num">{day.day}</div>
                    <div class="day-pnl {pnl_cls}">{format_currency_text(pnl)}</div>
                    <div class="day-sub">{trades} trade{'s' if trades != 1 else ''}</div>
                    <div class="day-sub">{wr:.1f}%</div>
                </td>
                """
        html += "</tr>"

        week_cls = pnl_text_class(week_pnl)
        week_cards.append(f"""
        <div class="week-side-card">
            <div class="week-side-title">Week {w_idx}</div>
            <div class="week-side-pnl {week_cls}">{format_currency_text(week_pnl)}</div>
            <div class="week-side-sub">{week_days_with_trade} days</div>
        </div>
        """)

    html += """
                    </tbody>
                </table>
            </div>
            <div>
    """

    html += "".join(week_cards)
    html += """
            </div>
        </div>
    </div>
    """
    return html

# ============================================
# [05] 資料讀取與處理
# ============================================
@st.cache_data(ttl=60)
def load_data():
    file_path = "三均線_signal_trades.csv"

    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    df['entry_time'] = pd.to_datetime(df['entry_time'])
    df['exit_time'] = pd.to_datetime(df['exit_time'])

    df = df.sort_values('exit_time').reset_index(drop=True)

    df['duration'] = df['exit_time'] - df['entry_time']
    df["日期文字"] = df["exit_time"].dt.strftime("%Y-%m-%d %H:%M")
    df["Hover顯示"] = df["export_net_pnl"].apply(
        lambda x: f"+{x:,.0f}" if x > 0 else (f"-{abs(x):,.0f}" if x < 0 else "0")
    )

    return df

# ============================================
# [06] Dashboard 頂部
# ============================================
st.markdown('<div class="dashboard-title">📈 三均線策略 --- 最新實單績效分析</div>', unsafe_allow_html=True)

if st.button("🔄 獲取最新資料 (重整)"):
    st.cache_data.clear()
    st.rerun()

df = load_data()

if df.empty:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">找不到資料</div>
        <div class="panel-subtitle">找不到 `三均線_signal_trades.csv`，請確認檔案是否在同一資料夾。</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

latest_exit = df["exit_time"].max()

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

ctrl1, ctrl2 = st.columns([1.1, 1.1])

with ctrl1:
    period_label = st.selectbox(
        "📆 選擇績效統計期間",
        ["近1個月", "近3個月", "近9個月", "近12個月", "全部"],
        index=1
    )

period_start = get_period_start(latest_exit, period_label)
if period_start is not None:
    filtered_df = df[df["exit_time"] >= period_start].copy()
else:
    filtered_df = df.copy()

filtered_df = filtered_df.sort_values("exit_time").reset_index(drop=True)

if filtered_df.empty:
    st.warning("所選期間內沒有資料。")
    st.stop()

month_options = get_month_options(filtered_df)

with ctrl2:
    selected_month = st.selectbox(
        "🗓️ 選擇月曆月份",
        month_options,
        index=0 if len(month_options) > 0 else None
    )

# 重新計算資金曲線與回撤
filtered_df['cum_pnl'] = filtered_df['export_net_pnl'].cumsum()
filtered_df['cum_peak'] = filtered_df['cum_pnl'].cummax()
filtered_df['drawdown'] = filtered_df['cum_pnl'] - filtered_df['cum_peak']

# ============================================
# [07] 核心 KPI
# ============================================
total_pnl = filtered_df["export_net_pnl"].sum()
total_trades = len(filtered_df)
win_trades = (filtered_df["export_net_pnl"] > 0).sum()
loss_trades = (filtered_df["export_net_pnl"] < 0).sum()
flat_trades = (filtered_df["export_net_pnl"] == 0).sum()
win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0

running_days = (filtered_df["exit_time"].max() - filtered_df["entry_time"].min()).days
running_days = max(running_days, 1)

avg_win = filtered_df.loc[filtered_df["export_net_pnl"] > 0, "export_net_pnl"].mean()
avg_loss = filtered_df.loc[filtered_df["export_net_pnl"] < 0, "export_net_pnl"].mean()
avg_win = 0 if pd.isna(avg_win) else avg_win
avg_loss = 0 if pd.isna(avg_loss) else avg_loss

payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
max_drawdown = filtered_df['drawdown'].min()

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">總累計淨損益</div>
        <div class="kpi-value">{format_currency_tw(total_pnl)}</div>
        <div class="kpi-foot">{period_label} 統計</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">總交易次數</div>
        <div class="kpi-value text-blue">{total_trades}</div>
        <div class="kpi-foot">完整平倉趟數</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">交易勝率</div>
        <div class="kpi-value text-purple">{win_rate:.1f}%</div>
        <div class="kpi-foot">獲利趟數 / 總趟數</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">最大連續回撤</div>
        <div class="kpi-value text-green">-${abs(max_drawdown):,.0f}</div>
        <div class="kpi-foot">歷史最大跌幅</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">盈虧比 (Payoff)</div>
        <div class="kpi-value text-orange">{payoff_ratio:.2f}</div>
        <div class="kpi-foot">均盈 / 均虧</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">實績運行天數</div>
        <div class="kpi-value" style="color:#FCD34D;">{running_days} 天</div>
        <div class="kpi-foot">首筆至最新交易日</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ============================================
# [08] 中段圖表：主圖 (資金曲線) & 統計面板
# ============================================
left_col, right_col = st.columns([2.8, 1])

with left_col:
    st.markdown("""
    <div class="panel" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px; border-bottom: none;">
        <div class="panel-title">累計資金曲線 (Equity Curve)</div>
        <div class="panel-subtitle" style="margin-bottom: 0px;">
            <span class="info-badge">策略淨值</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_equity = go.Figure()

    fig_equity.add_trace(go.Scatter(
        x=filtered_df["日期文字"],
        y=filtered_df["cum_pnl"],
        text=filtered_df["Hover顯示"],
        mode="lines",
        line=dict(color="#8B5CF6", width=4),
        name="累計損益",
        hovertemplate="<b>%{x}</b><br>累計損益: %{y:,.0f}<br>單趟: %{text}<extra></extra>"
    ))

    fig_equity.update_layout(
        template="plotly_dark",
        height=380,
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
            nticks=10
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
    if pd.isna(avg_duration):
        duration_str = "N/A"
    else:
        total_seconds = int(avg_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        duration_str = f"{hours}小時 {minutes}分"

    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom:14px;">
        <div class="kpi-label">平均持倉時間</div>
        <div class="kpi-value" style="font-size:1.55rem; color:#60A5FA;">{duration_str}</div>
        <div class="kpi-foot">進場至出場時間差</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

# ============================================
# [09] 每日績效月曆
# ============================================
if selected_month is not None:
    month_df = filtered_df[
        filtered_df["exit_time"].dt.to_period("M").astype(str) == selected_month
    ].copy()
    calendar_html = build_monthly_calendar_html(month_df, selected_month)
    st.markdown(calendar_html, unsafe_allow_html=True)

# ============================================
# [10] 底部：最新交易紀錄明細
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
        dir_str = str(dir_val)

    en_price = f"{row.get('entry_price', 0):,.0f}"
    ex_price = f"{row.get('exit_price', 0):,.0f}"
    pnl = row.get('export_net_pnl', 0)
    pnl_str = format_currency_tw(pnl)

    reason = str(row.get('exit_reason', ''))
    if len(reason) > 25:
        reason = reason[:25] + "..."

    table_html += f"""
    <tr>
        <td>{en_time}</td>
        <td>{ex_time}</td>
        <td>{dir_str}</td>
        <td>{en_price}</td>
        <td>{ex_price}</td>
        <td><b>{pnl_str}</b></td>
        <td>{reason}</td>
    </tr>
    """

table_html += """
            </tbody>
        </table>
    </div>
</div>
"""

st.markdown(table_html, unsafe_allow_html=True)
