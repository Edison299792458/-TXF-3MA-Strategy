import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 設定網頁標題與寬度
st.set_page_config(page_title="三均線策略分析儀表板", layout="wide")
st.title("📈 三均線策略交易分析儀表板")

# 2. 讀取與處理資料 (使用 st.cache_data 避免重複讀取)
@st.cache_data
def load_data():
    df = pd.read_csv(r"C:\Users\USER\Edison_Trading_Data_code\訊號成交紀錄\林董\三均線\三均線_signal_trades.csv")
    # 將時間轉換為 Datetime 格式
    df['entry_time'] = pd.to_datetime(df['entry_time'])
    df['exit_time'] = pd.to_datetime(df['exit_time'])
    # 計算累積損益與累積點數
    df['cumulative_pnl'] = df['export_net_pnl'].cumsum()
    df['cumulative_points'] = df['export_net_points'].cumsum()
    # 判斷每筆交易是賺還是賠
    df['is_win'] = df['export_net_pnl'] > 0
    return df

df = load_data()

# 3. 建立側邊欄過濾器 (Sidebar Filters)
st.sidebar.header("🔍 篩選條件")
selected_dir = st.sidebar.multiselect(
    "選擇交易方向", 
    options=df['entry_dir'].unique(), 
    default=df['entry_dir'].unique()
)

# 套用篩選條件
filtered_df = df[df['entry_dir'].isin(selected_dir)]

# 4. 顯示核心數據指標 (KPI Metrics)
st.subheader("💡 核心績效指標")
col1, col2, col3, col4 = st.columns(4)

total_trades = len(filtered_df)
win_trades = len(filtered_df[filtered_df['is_win']])
win_rate = (win_trades / total_trades * 100) if total_trades > 0 else 0
total_pnl = filtered_df['export_net_pnl'].sum()
avg_pnl = filtered_df['export_net_pnl'].mean() if total_trades > 0 else 0

col1.metric("總交易筆數", f"{total_trades} 筆")
col2.metric("總淨利 (NTD)", f"{total_pnl:,.0f}")
col3.metric("勝率", f"{win_rate:.2f}%")
col4.metric("平均每筆損益", f"{avg_pnl:,.0f}")

st.markdown("---")

# 5. 繪製圖表
col_chart1, col_chart2 = st.columns(2)

# 圖表 A：資金曲線 (Cumulative PnL)
with col_chart1:
    st.subheader("📊 資金曲線 (累積損益)")
    # 注意：如果經過篩選，需重新計算累積損益以利畫圖
    filtered_df = filtered_df.copy()
    filtered_df['filtered_cum_pnl'] = filtered_df['export_net_pnl'].cumsum()
    
    fig_equity = px.line(
        filtered_df, x='exit_time', y='filtered_cum_pnl', 
        markers=True, title="隨時間變化的累積淨利",
        labels={'exit_time': '出場時間', 'filtered_cum_pnl': '累積淨利'}
    )
    st.plotly_chart(fig_equity, use_container_width=True)

# 圖表 B：多空方向勝率分佈
with col_chart2:
    st.subheader("⚖️ 多/空方向損益分佈")
    fig_box = px.box(
        filtered_df, x="entry_dir", y="export_net_pnl", 
        color="entry_dir", title="LONG vs SHORT 單筆損益分佈",
        labels={'entry_dir': '交易方向', 'export_net_pnl': '單筆淨利'}
    )
    st.plotly_chart(fig_box, use_container_width=True)

st.markdown("---")

# 圖表 C：出場理由統計
st.subheader("🚪 出場理由分析")
exit_reason_counts = filtered_df['exit_reason'].value_counts().reset_index()
exit_reason_counts.columns = ['exit_reason', 'count']

fig_exit = px.bar(
    exit_reason_counts, x='count', y='exit_reason', 
    orientation='h', title="各出場理由觸發次數",
    color='count', color_continuous_scale='Blues'
)
fig_exit.update_layout(yaxis={'categoryorder':'total ascending'}) # 讓數量多的在上面
st.plotly_chart(fig_exit, use_container_width=True)

# 6. 顯示原始資料表
st.subheader("📋 交易紀錄明細")
st.dataframe(filtered_df[['entry_time', 'entry_price', 'entry_dir', 'exit_time', 'exit_price', 'export_net_pnl', 'exit_reason']].sort_values(by='entry_time', ascending=False))
