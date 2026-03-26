# ============================================
# [01] Imports
# ============================================
import os
import calendar
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# ============================================
# [02] 基本設定
# ============================================
st_autorefresh(interval=60000, key="data_refresh")

st.set_page_config(
    page_title="三均線策略實盤分析",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# [03] 全站樣式
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

.kpi-foot {
    font-size: 0.82rem;
    color: #71717A;
}

.text-red { color: #F87171 !important; }
.text-green { color: #34D399 !important; }
.text-blue { color: #60A5FA !important; }
.text-purple { color: #A78BFA !important; }
.text-orange { color: #FBBF24 !important; }
.text-white { color: #FFFFFF !important; }

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

/* ===== 月曆 ===== */
.calendar-head {
    text-align: center;
    color: #C7CDD8;
    font-size: 0.90rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.calendar-side-head {
    text-align: center;
    color: transparent;
    font-size: 0.90rem;
    font-weight: 700;
    margin-bottom: 8px;
}

.calendar-empty {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.05);
    min-height: 110px;
    padding: 10px 10px;
    background: rgba(255,255,255,0.02);
    margin-bottom: 10px;
}

.calendar-card-neutral {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.06);
    min-height: 110px;
    padding: 10px 10px;
    background: rgba(12,14,20,0.92);
    margin-bottom: 10px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}

.calendar-card-pos {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.07);
    min-height: 110px;
    padding: 10px 10px;
    background: linear-gradient(180deg, rgba(120,28,28,0.92) 0%, rgba(78,18,18,0.96) 100%);
    margin-bottom: 10px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}

.calendar-card-neg {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.07);
    min-height: 110px;
    padding: 10px 10px;
    background: linear-gradient(180deg, rgba(6,78,59,0.92) 0%, rgba(4,52,40,0.96) 100%);
    margin-bottom: 10px;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}

.day-num {
    font-size: 0.88rem;
    font-weight: 700;
    margin-bottom: 10px;
    color: #FFFFFF;
}

.day-pnl-pos {
    font-size: 1.02rem;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 6px;
    color: #FFD4D4;
}

.day-pnl-neg {
    font-size: 1.02rem;
    font-weight: 800;
    line-height: 1.15;
    margin-bottom: 6px;
    color: #C7FFE8;
}

.day-sub-pos {
    font-size: 0.76rem;
    line-height: 1.35;
    color: #FFDCDC;
}

.day-sub-neg {
    font-size: 0.76rem;
    line-height: 1.35;
    color: #D1FFEE;
}

.day-sub-neutral {
    font-size: 0.76rem;
    line-height: 1.35;
    color: #FFFFFF;
}

.week-side-card {
    background: linear-gradient(180deg, rgba(20,20,24,0.98) 0%, rgba(10,10,12,0.98) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 12px 14px;
    min-height: 110px;
    margin-bottom: 10px;
}

.week-side-title {
    font-size: 0.82rem;
    color: #E5E7EB;
    margin-bottom: 10px;
    font-weight: 700;
}

.week-side-pnl {
    font-size: 1.2rem;
    font-weight: 800;
    margin-bottom: 6px;
}

.week-side-sub {
    font-size: 0.78rem;
    color: #A1A1AA;
}

div[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ============================================
# [04] 共用函式
# ============================================
def format_currency_tw(val):
    if pd.isna(val):
        val = 0
    if val > 0:
        return f'<span class="text-red">+${val:,.0f}</span>'
    elif val < 0:
        return f'<span class="text-green">-${abs(val):,.0f}</span>'
    else:
        return '<span style="color:#A1A1AA;">$0</span>'

def format_currency_text(val):
    if pd.isna(val):
        val = 0
    if val > 0:
        return f"+${val:,.0f}"
    elif val < 0:
        return f"-${abs(val):,.0f}"
    else:
        return "$0"

def pnl_class_name(val):
    if pd.isna(val) or val == 0:
        return "text-white"
    return "text-red" if val > 0 else "text-green"

def get_period_start(latest_dt, period_label):
    if period_label == "近1個月":
        return latest_dt - pd.DateOffset(months=1)
    elif period_label == "近3個月":
        return latest_dt - pd.DateOffset(months=3)
    elif period_label == "近9個月":
        return latest_dt - pd.DateOffset(months=9)
    elif period_label == "近12個月":
        return latest_dt - pd.DateOffset(months=12)
    return None

def get_month_options(df):
    if df.empty:
        return []
    return (
        df["exit_time"]
        .dt.to_period("M")
        .astype(str)
        .drop_duplicates()
        .sort_values(ascending=False)
        .tolist()
    )

def safe_direction_text(x):
    x = str(x).upper()
    if x == "LONG":
        return "多 (LONG)"
    elif x == "SHORT":
        return "空 (SHORT)"
    return x

def calc_avg_duration_str(series):
    if len(series) == 0:
        return "N/A"
    avg_duration = series.mean()
    if pd.isna(avg_duration):
        return "N/A"
    total_seconds = int(avg_duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}小時 {minutes}分"

def get_day_card_info(pnl_value):
    if pd.isna(pnl_value) or pnl_value == 0:
        return {
            "card_class": "calendar-card-neutral",
            "pnl_class": "day-sub-neutral",
            "sub_class": "day-sub-neutral"
        }
    elif pnl_value > 0:
        return {
            "card_class": "calendar-card-pos",
            "pnl_class": "day-pnl-pos",
            "sub_class": "day-sub-pos"
        }
    else:
        return {
            "card_class": "calendar-card-neg",
            "pnl_class": "day-pnl-neg",
            "sub_class": "day-sub-neg"
        }

# ============================================
# [05] 讀取資料
# ============================================
@st.cache_data(ttl=60)
def load_data():
    file_path = "三均線_signal_trades.csv"

    if not os.path.exists(file_path):
        return pd.DataFrame()

    df = pd.read_csv(file_path)

    required_cols = [
        "entry_time", "exit_time", "export_net_pnl",
        "entry_price", "exit_price", "exit_reason", "entry_dir"
    ]
    for c in required_cols:
        if c not in df.columns:
            df[c] = None

    df["entry_time"] = pd.to_datetime(df["entry_time"], errors="coerce")
    df["exit_time"] = pd.to_datetime(df["exit_time"], errors="coerce")

    df = df.dropna(subset=["exit_time"]).sort_values("exit_time").reset_index(drop=True)
    df["duration"] = df["exit_time"] - df["entry_time"]

    df["日期文字"] = df["exit_time"].dt.strftime("%Y-%m-%d")
    df["Hover顯示"] = df["export_net_pnl"].fillna(0).apply(
        lambda x: f"+{x:,.0f}" if x > 0 else (f"-{abs(x):,.0f}" if x < 0 else "0")
    )

    return df

# ============================================
# [06] 頂部
# ============================================
st.markdown('<div class="dashboard-title">📈 三均線策略 --- 實單績效分析</div>', unsafe_allow_html=True)

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

ctrl_col1, ctrl_col2 = st.columns([1.1, 1.1])

with ctrl_col1:
    period_label = st.selectbox(
        "📆 選擇績效統計期間",
        ["近1個月", "近3個月", "近9個月", "近12個月", "全部"],
        index=4
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

filtered_df["cum_pnl"] = filtered_df["export_net_pnl"].fillna(0).cumsum()
filtered_df["cum_peak"] = filtered_df["cum_pnl"].cummax()
filtered_df["drawdown"] = filtered_df["cum_pnl"] - filtered_df["cum_peak"]

month_options = get_month_options(filtered_df)

# ============================================
# [07] KPI
# ============================================
total_pnl = filtered_df["export_net_pnl"].fillna(0).sum()
total_trades = len(filtered_df)
win_trades = (filtered_df["export_net_pnl"].fillna(0) > 0).sum()
loss_trades = (filtered_df["export_net_pnl"].fillna(0) < 0).sum()
flat_trades = (filtered_df["export_net_pnl"].fillna(0) == 0).sum()
win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0

running_days = (filtered_df["exit_time"].max() - filtered_df["entry_time"].min()).days
running_days = max(running_days, 1)

avg_win = filtered_df.loc[filtered_df["export_net_pnl"] > 0, "export_net_pnl"].mean()
avg_loss = filtered_df.loc[filtered_df["export_net_pnl"] < 0, "export_net_pnl"].mean()
avg_win = 0 if pd.isna(avg_win) else avg_win
avg_loss = 0 if pd.isna(avg_loss) else avg_loss
payoff_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else 0
max_drawdown = filtered_df["drawdown"].min()

k1, k2, k3, k4, k5, k6 = st.columns(6)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">總累計淨損益</div>
        <div class="kpi-value">{format_currency_tw(total_pnl)}</div>
        <div class="kpi-foot">{period_label} 統計</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">總交易次數</div>
        <div class="kpi-value text-blue">{total_trades}</div>
        <div class="kpi-foot">完整平倉趟數</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">交易勝率</div>
        <div class="kpi-value text-purple">{win_rate:.1f}%</div>
        <div class="kpi-foot">獲利趟數 / 總趟數</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">最大連續回撤</div>
        <div class="kpi-value text-green">-${abs(max_drawdown):,.0f}</div>
        <div class="kpi-foot">歷史最大跌幅</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">盈虧比 (Payoff)</div>
        <div class="kpi-value text-orange">{payoff_ratio:.2f}</div>
        <div class="kpi-foot">均盈 / 均虧</div>
    </div>
    """, unsafe_allow_html=True)

with k6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">實績運行天數</div>
        <div class="kpi-value" style="color:#FCD34D;">{running_days} 天</div>
        <div class="kpi-foot">首筆至最新交易日</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

# ============================================
# [08] 資金曲線 + 右側分析
# ============================================
left_col, right_col = st.columns([2.8, 1])

with left_col:
    st.markdown("""
    <div class="panel" style="margin-bottom:0px; border-bottom-left-radius:0px; border-bottom-right-radius:0px; border-bottom:none;">
        <div class="panel-title">累計資金曲線 (Equity Curve)</div>
        <div class="panel-subtitle" style="margin-bottom:0px;">
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

    st.plotly_chart(fig_equity, use_container_width=True, config={"displayModeBar": False})

    if len(month_options) > 0:
        selected_month = st.selectbox(
            "🗓️ 選擇月曆月份",
            options=month_options,
            index=0,
            key="calendar_month_select"
        )
    else:
        selected_month = None

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
        <div class="kpi-value" style="font-size:1.55rem;">
            <span class="text-red">{win_trades}</span> /
            <span class="text-green">{loss_trades}</span> /
            {flat_trades}
        </div>
        <div class="kpi-foot">依單筆損益統計</div>
    </div>
    """, unsafe_allow_html=True)

    duration_str = calc_avg_duration_str(filtered_df["duration"])

    st.markdown(f"""
    <div class="kpi-card" style="margin-bottom:14px;">
        <div class="kpi-label">平均持倉時間</div>
        <div class="kpi-value" style="font-size:1.55rem; color:#60A5FA;">{duration_str}</div>
        <div class="kpi-foot">進場至出場時間差</div>
    </div>
    """, unsafe_allow_html=True)
    # ============================================
# [09] 每日績效月曆
# ============================================
st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="panel">
    <div class="panel-title">每日績效月曆</div>
</div>
""", unsafe_allow_html=True)

if selected_month is not None:
    year, month = map(int, selected_month.split("-"))

    month_df = filtered_df[
        filtered_df["exit_time"].dt.to_period("M").astype(str) == selected_month
    ].copy()

    month_df["exit_date"] = month_df["exit_time"].dt.date

    # ==========================================================
    # 這裡是本次唯一重點修改：
    # 把所有「週六」績效併到前一天「週五」
    # Python weekday(): Monday=0 ... Friday=4, Saturday=5, Sunday=6
    # ==========================================================
    month_df["display_date"] = month_df["exit_date"].apply(
        lambda d: d - pd.Timedelta(days=1) if pd.Timestamp(d).weekday() == 5 else d
    )

    daily_df = month_df.groupby("display_date").agg(
        day_pnl=("export_net_pnl", "sum"),
        trades=("export_net_pnl", "size"),
        win_rate=("export_net_pnl", lambda s: (s.gt(0).mean() * 100) if len(s) > 0 else 0)
    ).reset_index()

    daily_map = {
        row["display_date"]: {
            "pnl": row["day_pnl"],
            "trades": int(row["trades"]),
            "win_rate": row["win_rate"]
        }
        for _, row in daily_df.iterrows()
    }

    title_dt = datetime(year, month, 1)
    st.markdown(f"### {title_dt.strftime('%Y-%m')}")

    col_widths = [1, 1, 1, 1, 1, 1, 1, 1.45]

    head_cols = st.columns(col_widths)
    weekday_names = ["日", "一", "二", "三", "四", "五", "六"]

    for i in range(7):
        with head_cols[i]:
            st.markdown(
                f"<div class='calendar-head'>{weekday_names[i]}</div>",
                unsafe_allow_html=True
            )

    with head_cols[7]:
        st.markdown(
            "<div class='calendar-side-head'>週統計</div>",
            unsafe_allow_html=True
        )

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)

    for week_idx, week in enumerate(weeks, start=1):
        row_cols = st.columns(col_widths)

        week_pnl = 0
        week_days_with_trade = 0

        for i, day in enumerate(week):
            with row_cols[i]:
                if day.month != month:
                    st.markdown("<div class='calendar-empty'></div>", unsafe_allow_html=True)
                else:
                    info = daily_map.get(day, None)

                    if info is None:
                        st.markdown(f"""
                        <div class="calendar-card-neutral">
                            <div class="day-num">{day.day}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        pnl = info["pnl"]
                        trades = info["trades"]
                        wr = info["win_rate"]

                        week_pnl += pnl
                        week_days_with_trade += 1

                        style_info = get_day_card_info(pnl)

                        st.markdown(f"""
                        <div class="{style_info['card_class']}">
                            <div class="day-num">{day.day}</div>
                            <div class="{style_info['pnl_class']}">{format_currency_text(pnl)}</div>
                            <div class="{style_info['sub_class']}">{trades} 筆交易</div>
                            <div class="{style_info['sub_class']}">勝率 {wr:.1f}%</div>
                        </div>
                        """, unsafe_allow_html=True)

        with row_cols[7]:
            pnl_cls = pnl_class_name(week_pnl)
            st.markdown(f"""
            <div class="week-side-card">
                <div class="week-side-title">第 {week_idx} 週</div>
                <div class="week-side-pnl {pnl_cls}">{format_currency_text(week_pnl)}</div>
                <div class="week-side-sub">{week_days_with_trade} 天</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================
# [10] 最新 10 筆平倉紀錄明細
# ============================================
st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="panel" style="margin-bottom:10px;">
    <div class="panel-title">最新 10 筆平倉紀錄明細</div>
</div>
""", unsafe_allow_html=True)

recent_trades = filtered_df.sort_values("exit_time", ascending=False).head(10).copy()

recent_trades["進場時間"] = recent_trades["entry_time"].dt.strftime("%m-%d %H:%M")
recent_trades["出場時間"] = recent_trades["exit_time"].dt.strftime("%m-%d %H:%M")
recent_trades["方向"] = recent_trades["entry_dir"].apply(safe_direction_text)
recent_trades["進場價"] = recent_trades["entry_price"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
recent_trades["出場價"] = recent_trades["exit_price"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
recent_trades["淨損益 (NTD)"] = recent_trades["export_net_pnl"].apply(format_currency_text)
recent_trades["出場原因"] = recent_trades["exit_reason"].fillna("").astype(str)

show_cols = ["進場時間", "出場時間", "方向", "進場價", "出場價", "淨損益 (NTD)", "出場原因"]
recent_show_df = recent_trades[show_cols].reset_index(drop=True)

def highlight_pnl(val):
    if isinstance(val, str):
        if val.startswith("+$"):
            return "color:#F87171; font-weight:700;"
        elif val.startswith("-$"):
            return "color:#34D399; font-weight:700;"
    return ""

def highlight_direction(val):
    if val == "多 (LONG)":
        return "color:#F87171; font-weight:700;"
    elif val == "空 (SHORT)":
        return "color:#34D399; font-weight:700;"
    return ""

styled_df = (
    recent_show_df.style
    .applymap(highlight_pnl, subset=["淨損益 (NTD)"])
    .applymap(highlight_direction, subset=["方向"])
)

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True,
    height=390
)
