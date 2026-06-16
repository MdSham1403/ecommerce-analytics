"""
E-Commerce Sales Analytics Dashboard
Author : Mohamed Shameer
Stack  : Python · Pandas · Plotly · Streamlit · SQLite
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.data_loader import load_data, run_sql
from utils.kpi import compute_kpis
import warnings
warnings.filterwarnings("ignore")

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #F8FAFC; }
    /* KPI cards */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 20px 24px;
        border-left: 4px solid #1D4ED8;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .kpi-label { font-size: 13px; color: #6B7280; font-weight: 500; margin-bottom: 4px; }
    .kpi-value { font-size: 26px; font-weight: 700; color: #111827; }
    .kpi-delta { font-size: 12px; margin-top: 4px; }
    .kpi-delta.pos { color: #16A34A; }
    .kpi-delta.neg { color: #DC2626; }
    /* Section headers */
    .section-title {
        font-size: 16px; font-weight: 600;
        color: #1D4ED8; margin: 24px 0 12px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #DBEAFE;
    }
    /* Sidebar */
    .css-1d391kg { background-color: #F1F5F9; }
    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df_raw = get_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/fluency/48/shopping-cart.png", width=40)
    st.title("🔍 Filters")
    st.markdown("---")

    # Year filter
    years = sorted(df_raw["year"].unique(), reverse=True)
    sel_years = st.multiselect("📅 Year", years, default=years)

    # Region filter
    regions = sorted(df_raw["region"].unique())
    sel_regions = st.multiselect("🗺️ Region", regions, default=regions)

    # Category filter
    cats = sorted(df_raw["category"].unique())
    sel_cats = st.multiselect("📦 Category", cats, default=cats)

    # Order status
    statuses = sorted(df_raw["order_status"].unique())
    sel_status = st.multiselect("📋 Order Status", statuses, default=statuses)

    st.markdown("---")
    st.caption("📊 Data: 5,000 Indian E-Commerce Orders (2022–2024)")
    st.caption("👨‍💻 Built by Mohamed Shameer")

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
df = df_raw[
    df_raw["year"].isin(sel_years) &
    df_raw["region"].isin(sel_regions) &
    df_raw["category"].isin(sel_cats) &
    df_raw["order_status"].isin(sel_status)
].copy()

if df.empty:
    st.warning("⚠️ No data for selected filters. Please adjust.")
    st.stop()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("## 🛒 E-Commerce Sales Analytics Dashboard")
st.markdown(f"Showing **{len(df):,}** orders · {sel_years[0] if len(sel_years)==1 else f'{min(sel_years)}–{max(sel_years)}'}")
st.markdown("---")

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
kpis = compute_kpis(df, df_raw)

col1, col2, col3, col4, col5 = st.columns(5)

def kpi_card(col, label, value, delta=None, positive=True):
    delta_class = "pos" if positive else "neg"
    delta_html  = f'<div class="kpi-delta {delta_class}">{delta}</div>' if delta else ""
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

kpi_card(col1, "💰 Total Revenue",   kpis["revenue"],      kpis["revenue_delta"],  kpis["revenue_pos"])
kpi_card(col2, "📈 Total Profit",    kpis["profit"],       kpis["profit_delta"],   kpis["profit_pos"])
kpi_card(col3, "🛒 Total Orders",    kpis["orders"],       kpis["orders_delta"],   kpis["orders_pos"])
kpi_card(col4, "📦 Avg Order Value", kpis["aov"],          kpis["aov_delta"],      kpis["aov_pos"])
kpi_card(col5, "✅ Delivery Rate",   kpis["delivery_rate"], None)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 1 — SALES TREND + REGION PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 Sales Trends & Regional Performance</div>', unsafe_allow_html=True)
c1, c2 = st.columns([3, 2])

with c1:
    # Monthly revenue trend
    trend = (
        df.groupby(["year_month", "month_label"])
          .agg(revenue=("revenue","sum"), orders=("order_id","count"), profit=("profit","sum"))
          .reset_index()
          .sort_values("year_month")
    )
    metric = st.radio("Trend metric", ["Revenue", "Orders", "Profit"],
                      horizontal=True, key="trend_metric")
    y_col  = {"Revenue":"revenue","Orders":"orders","Profit":"profit"}[metric]
    y_label= {"Revenue":"Revenue (₹)","Orders":"Order Count","Profit":"Profit (₹)"}[metric]

    fig_trend = px.line(
        trend, x="month_label", y=y_col,
        markers=True,
        labels={"month_label": "Month", y_col: y_label},
        title=f"Monthly {metric} Trend",
        color_discrete_sequence=["#1D4ED8"],
        template="plotly_white",
    )
    fig_trend.update_traces(line_width=2.5, marker_size=6)
    fig_trend.update_layout(
        height=340, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_tickangle=-45, xaxis_title=None,
        title_font_size=14,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with c2:
    # Region donut
    region_df = (
        df.groupby("region")
          .agg(revenue=("revenue","sum"), orders=("order_id","count"))
          .reset_index()
    )
    fig_region = px.pie(
        region_df, names="region", values="revenue",
        hole=0.55,
        title="Revenue by Region",
        color_discrete_sequence=["#1D4ED8","#3B82F6","#93C5FD","#BFDBFE"],
        template="plotly_white",
    )
    fig_region.update_traces(textposition="outside", textinfo="label+percent")
    fig_region.update_layout(
        height=340, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False, title_font_size=14,
    )
    st.plotly_chart(fig_region, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 2 — TOP CATEGORIES + TOP PRODUCTS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📦 Category & Product Performance</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)

with c3:
    # Category bar chart
    cat_df = (
        df.groupby("category")
          .agg(revenue=("revenue","sum"), profit=("profit","sum"), orders=("order_id","count"))
          .reset_index()
          .sort_values("revenue", ascending=True)
    )
    fig_cat = px.bar(
        cat_df, x="revenue", y="category",
        orientation="h",
        text=cat_df["revenue"].apply(lambda x: f"₹{x/1e5:.1f}L"),
        title="Revenue by Category",
        color="revenue",
        color_continuous_scale=["#BFDBFE","#1D4ED8"],
        template="plotly_white",
    )
    fig_cat.update_traces(textposition="outside")
    fig_cat.update_layout(
        height=340, margin=dict(l=10, r=60, t=40, b=10),
        coloraxis_showscale=False, xaxis_title="Revenue (₹)",
        yaxis_title=None, title_font_size=14,
    )
    st.plotly_chart(fig_cat, use_container_width=True)

with c4:
    # Top 10 products
    top_n = st.slider("Top N Products", 5, 15, 10, key="topn")
    prod_df = (
        df.groupby("product_name")
          .agg(revenue=("revenue","sum"), orders=("order_id","count"))
          .reset_index()
          .sort_values("revenue", ascending=False)
          .head(top_n)
          .sort_values("revenue", ascending=True)
    )
    fig_prod = px.bar(
        prod_df, x="revenue", y="product_name",
        orientation="h",
        text=prod_df["revenue"].apply(lambda x: f"₹{x/1e5:.1f}L"),
        title=f"Top {top_n} Products by Revenue",
        color="revenue",
        color_continuous_scale=["#DBEAFE","#1E40AF"],
        template="plotly_white",
    )
    fig_prod.update_traces(textposition="outside")
    fig_prod.update_layout(
        height=340, margin=dict(l=10, r=60, t=40, b=10),
        coloraxis_showscale=False, xaxis_title="Revenue (₹)",
        yaxis_title=None, title_font_size=14,
    )
    st.plotly_chart(fig_prod, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 3 — CITY PERFORMANCE + PAYMENT METHODS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🏙️ City & Payment Insights</div>', unsafe_allow_html=True)
c5, c6 = st.columns([3, 2])

with c5:
    # Top cities grouped bar
    city_df = (
        df.groupby(["region", "city"])
          .agg(revenue=("revenue","sum"), orders=("order_id","count"))
          .reset_index()
          .sort_values("revenue", ascending=False)
          .head(12)
    )
    fig_city = px.bar(
        city_df, x="city", y="revenue", color="region",
        text=city_df["revenue"].apply(lambda x: f"₹{x/1e5:.1f}L"),
        title="Top Cities by Revenue",
        color_discrete_sequence=["#1D4ED8","#3B82F6","#60A5FA","#93C5FD"],
        template="plotly_white",
        barmode="group",
    )
    fig_city.update_traces(textposition="outside", textfont_size=10)
    fig_city.update_layout(
        height=340, margin=dict(l=10, r=10, t=40, b=10),
        xaxis_tickangle=-35, xaxis_title=None,
        yaxis_title="Revenue (₹)", title_font_size=14,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_city, use_container_width=True)

with c6:
    # Payment method donut
    pay_df = (
        df.groupby("payment_method")
          .agg(orders=("order_id","count"), revenue=("revenue","sum"))
          .reset_index()
    )
    fig_pay = px.pie(
        pay_df, names="payment_method", values="orders",
        hole=0.55,
        title="Orders by Payment Method",
        color_discrete_sequence=["#1D4ED8","#2563EB","#3B82F6","#60A5FA","#93C5FD"],
        template="plotly_white",
    )
    fig_pay.update_traces(textposition="outside", textinfo="label+percent")
    fig_pay.update_layout(
        height=340, margin=dict(l=10, r=10, t=40, b=10),
        showlegend=False, title_font_size=14,
    )
    st.plotly_chart(fig_pay, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# ROW 4 — PROFIT MARGIN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">💹 Profit Margin Analysis</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)

with c7:
    margin_df = (
        df.groupby("category")
          .agg(revenue=("revenue","sum"), profit=("profit","sum"))
          .reset_index()
    )
    margin_df["margin_pct"] = (margin_df["profit"] / margin_df["revenue"] * 100).round(1)
    fig_margin = px.bar(
        margin_df.sort_values("margin_pct"),
        x="margin_pct", y="category", orientation="h",
        text=margin_df.sort_values("margin_pct")["margin_pct"].apply(lambda x: f"{x}%"),
        title="Profit Margin % by Category",
        color="margin_pct",
        color_continuous_scale=["#93C5FD","#1D4ED8"],
        template="plotly_white",
    )
    fig_margin.update_traces(textposition="outside")
    fig_margin.update_layout(
        height=300, margin=dict(l=10,r=60,t=40,b=10),
        coloraxis_showscale=False, xaxis_title="Margin %",
        yaxis_title=None, title_font_size=14,
    )
    st.plotly_chart(fig_margin, use_container_width=True)

with c8:
    # Order status breakdown
    status_df = (
        df.groupby("order_status")
          .agg(orders=("order_id","count"), revenue=("revenue","sum"))
          .reset_index()
    )
    colors = {"Delivered":"#1D4ED8","Returned":"#EF4444","Cancelled":"#F59E0B"}
    fig_status = px.bar(
        status_df, x="order_status", y="orders",
        text="orders",
        title="Orders by Status",
        color="order_status",
        color_discrete_map=colors,
        template="plotly_white",
    )
    fig_status.update_traces(textposition="outside")
    fig_status.update_layout(
        height=300, margin=dict(l=10,r=10,t=40,b=10),
        showlegend=False, xaxis_title=None,
        yaxis_title="Order Count", title_font_size=14,
    )
    st.plotly_chart(fig_status, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SQL QUERY EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 SQL Query Explorer</div>', unsafe_allow_html=True)
st.markdown("Run SQL directly on the orders dataset — great for data analysis interviews!")

preset_queries = {
    "-- Select a query --": "",
    "Top 5 categories by revenue": """
SELECT category,
       COUNT(order_id)          AS total_orders,
       ROUND(SUM(revenue), 2)   AS total_revenue,
       ROUND(SUM(profit), 2)    AS total_profit,
       ROUND(AVG(revenue), 2)   AS avg_order_value
FROM orders
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;""",
    "Monthly revenue trend": """
SELECT strftime('%Y-%m', order_date) AS month,
       COUNT(order_id)               AS orders,
       ROUND(SUM(revenue), 2)        AS revenue,
       ROUND(SUM(profit), 2)         AS profit
FROM orders
WHERE order_status = 'Delivered'
GROUP BY month
ORDER BY month;""",
    "Region-wise performance": """
SELECT region,
       COUNT(DISTINCT city)          AS cities,
       COUNT(order_id)               AS total_orders,
       ROUND(SUM(revenue), 2)        AS total_revenue,
       ROUND(AVG(delivery_days), 1)  AS avg_delivery_days
FROM orders
GROUP BY region
ORDER BY total_revenue DESC;""",
    "Top 10 products by profit": """
SELECT product_name,
       category,
       COUNT(order_id)        AS orders,
       ROUND(SUM(revenue),2)  AS revenue,
       ROUND(SUM(profit),2)   AS profit,
       ROUND(SUM(profit)/SUM(revenue)*100, 1) AS margin_pct
FROM orders
GROUP BY product_name, category
ORDER BY profit DESC
LIMIT 10;""",
    "Payment method analysis": """
SELECT payment_method,
       COUNT(order_id)          AS total_orders,
       ROUND(SUM(revenue), 2)   AS total_revenue,
       ROUND(AVG(revenue), 2)   AS avg_order_value
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;""",
    "Return rate by category": """
SELECT category,
       COUNT(order_id) AS total_orders,
       SUM(CASE WHEN order_status='Returned' THEN 1 ELSE 0 END) AS returns,
       ROUND(SUM(CASE WHEN order_status='Returned' THEN 1.0 ELSE 0 END)
             / COUNT(order_id) * 100, 1) AS return_rate_pct
FROM orders
GROUP BY category
ORDER BY return_rate_pct DESC;""",
}

col_q1, col_q2 = st.columns([2, 3])

with col_q1:
    selected_preset = st.selectbox("📋 Preset Queries", list(preset_queries.keys()))

with col_q2:
    custom_query = st.text_area(
        "✏️ Write your own SQL (table name: `orders`)",
        value=preset_queries[selected_preset],
        height=120,
        placeholder="SELECT * FROM orders LIMIT 10;"
    )

if st.button("▶ Run Query", type="primary") and custom_query.strip():
    try:
        result = run_sql(custom_query)
        st.success(f"✅ {len(result)} rows returned")
        st.dataframe(result, use_container_width=True)
        csv = result.to_csv(index=False)
        st.download_button("⬇ Download CSV", csv, "query_result.csv", "text/csv")
    except Exception as e:
        st.error(f"❌ SQL Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# RAW DATA TABLE
# ══════════════════════════════════════════════════════════════════════════════
with st.expander("📋 View Raw Data"):
    st.dataframe(df.head(100), use_container_width=True)
    csv_raw = df.to_csv(index=False)
    st.download_button("⬇ Download Full Dataset", csv_raw, "ecommerce_orders.csv", "text/csv")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center style='color:#9CA3AF;font-size:13px;'>"
    "🛒 E-Commerce Analytics Dashboard · Built with Python, Pandas, Plotly & Streamlit · "
    "Mohamed Shameer · <a href='https://github.com/MdSham1403' style='color:#1D4ED8'>GitHub</a>"
    "</center>",
    unsafe_allow_html=True
)
