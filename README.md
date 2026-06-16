# 🛒 E-Commerce Sales Analytics Dashboard

A production-grade data analytics dashboard built with **Python, Pandas, Plotly, and Streamlit** — analysing 5,000 Indian e-commerce orders across 6 categories, 4 regions, and 20 cities (2022–2024).

**🔗 Live Demo:** [Click to open dashboard](#) *(add your Streamlit Cloud URL here)*

---

## 📊 Features

| Feature | Description |
|---|---|
| **KPI Cards** | Total Revenue, Profit, Orders, AOV, Delivery Rate with period-over-period delta |
| **Sales Trend** | Monthly Revenue / Orders / Profit line chart with toggle |
| **Regional Analysis** | Revenue by region (donut chart) + top cities bar chart |
| **Category Performance** | Revenue and profit margin by category |
| **Top Products** | Dynamic top-N products slider |
| **Payment Insights** | Order distribution by payment method |
| **SQL Explorer** | Run live SQL queries on the dataset with preset examples |
| **Filters** | Year, Region, Category, Order Status sidebar filters |
| **CSV Export** | Download filtered data or query results |

---

## 🛠️ Tech Stack

```
Python 3.11+
├── Pandas          — data loading, cleaning, transformation
├── Plotly Express  — interactive charts
├── Streamlit       — dashboard framework & deployment
└── SQLite          — in-memory SQL engine for query explorer
```

---

## 📁 Project Structure

```
ecommerce_analytics/
├── app.py                   # Main Streamlit dashboard
├── requirements.txt         # Python dependencies
├── data/
│   └── ecommerce_orders.csv # 5,000 order dataset (Indian e-commerce)
├── utils/
│   ├── data_loader.py       # CSV loader, SQLite writer, SQL runner
│   └── kpi.py               # KPI computation with delta vs prior period
└── .streamlit/
    └── config.toml          # Theme configuration
```

---

## 🚀 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/MdSham1403/ecommerce-analytics.git
cd ecommerce-analytics

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## ☁️ Deploy to Streamlit Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as entry point
4. Click **Deploy** — live in ~2 minutes

---

## 📈 Key Insights from the Data

- **Electronics** generates the highest revenue but lowest margin (~12%)
- **Beauty** category has the highest profit margin (~45%)
- **UPI** is the most popular payment method in India
- **South region** (Chennai, Bangalore) leads in order volume
- Revenue peaks in **Q4** (Oct–Dec) — festive season effect

---

## 🔍 SQL Explorer — Sample Queries

```sql
-- Top categories by revenue
SELECT category, SUM(revenue) AS total_revenue
FROM orders
GROUP BY category
ORDER BY total_revenue DESC;

-- Monthly trend
SELECT strftime('%Y-%m', order_date) AS month, SUM(revenue) AS revenue
FROM orders GROUP BY month ORDER BY month;

-- Return rate by category
SELECT category,
       ROUND(SUM(CASE WHEN order_status='Returned' THEN 1.0 ELSE 0 END)
             / COUNT(*) * 100, 1) AS return_rate_pct
FROM orders GROUP BY category;
```

---

## 👨‍💻 Author

**Mohamed Shameer**
- 📧 mdsham1403@gmail.com
- 🔗 [GitHub](https://github.com/MdSham1403)
- 💼 [LinkedIn](https://linkedin.com/in/[LinkedIn])

---

## 📄 License

MIT License — free to use and modify.
