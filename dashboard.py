
import os

import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Ecommerce Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- DESIGN ----------
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }

        [data-testid="stSidebar"] {
            border-right: 1px solid rgba(128,128,128,0.2);
        }

        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 2px;
            font-size: 11px;
            font-weight: 700;
            color: #64748b;
        }

        .hero {
            padding: 24px 28px;
            border-radius: 18px;
            background: linear-gradient(120deg, #102a43, #1d4e89);
            color: white;
            margin-bottom: 24px;
        }

        .hero h1 {
            color: white;
            font-size: 32px;
            margin: 6px 0;
        }

        .hero p {
            color: #dbeafe;
            margin-bottom: 0;
        }

        div[data-testid="stMetric"] {
            background: var(--secondary-background-color);
            border: 1px solid rgba(128,128,128,0.18);
            padding: 18px 20px;
            border-radius: 14px;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 13px;
        }

        .section-note {
            color: #64748b;
            font-size: 13px;
            margin-top: -8px;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128,128,128,0.2);
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- DATA ----------
@st.cache_data(ttl=60)
def load_data():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ecommerce_project"),
        connection_timeout=10,
    )

    query = """
        SELECT
            `Order ID`,
            `Order Date`,
            `Customer Name`,
            Region,
            Category,
            `Sub-Category`,
            `Product Name`,
            Sales,
            Quantity,
            Discount,
            Profit
        FROM `sample - superstore`
    """

    try:
        df = pd.read_sql(query, connection)
    finally:
        connection.close()

    for col in ["Sales", "Profit", "Quantity", "Discount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Order Date"] = pd.to_datetime(
        df["Order Date"], errors="coerce"
    )

    return df


try:
    df = load_data()
except Exception as error:
    st.error("Unable to load your sales data.")
    st.code(str(error))
    st.stop()


# ---------- SIDEBAR FILTERS ----------
st.sidebar.markdown("## 📊 ECOMMERCE")
st.sidebar.caption("INTELLIGENCE PLATFORM")
st.sidebar.divider()
st.sidebar.markdown("### Filters")

valid_dates = df["Order Date"].dropna()

if valid_dates.empty:
    st.error("No valid order dates were found in the dataset.")
    st.stop()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(
        valid_dates.min().date(),
        valid_dates.max().date(),
    ),
    min_value=valid_dates.min().date(),
    max_value=valid_dates.max().date(),
)

categories = sorted(
    df["Category"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Product categories",
    categories,
    default=categories,
)

regions = sorted(
    df["Region"].dropna().unique().tolist()
)

selected_regions = st.sidebar.multiselect(
    "Regions",
    regions,
    default=regions,
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

filtered_df = df[
    df["Order Date"].dt.date.between(start_date, end_date)
    & df["Category"].isin(selected_categories)
    & df["Region"].isin(selected_regions)
].copy()

st.sidebar.divider()
st.sidebar.caption("Data source: MySQL · Sample Superstore")
st.sidebar.caption(
    f"Records selected: {len(filtered_df):,}"
)


# ---------- HEADER ----------
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow" style="color:#bfdbfe">
            BUSINESS PERFORMANCE OVERVIEW
        </div>
        <h1>Ecommerce Intelligence</h1>
        <p>
            Understand sales, monitor profitability, and discover
            opportunities for better business decisions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if filtered_df.empty:
    st.warning(
        "No records match these filters. Adjust the sidebar filters."
    )
    st.stop()


# ---------- KPI CARDS ----------
total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()
total_quantity = filtered_df["Quantity"].sum()

profit_margin = (
    total_profit / total_sales * 100
    if total_sales
    else 0
)

all_dataset_sales = df["Sales"].sum()

sales_share = (
    total_sales / all_dataset_sales * 100
    if all_dataset_sales
    else 0
)

st.markdown("### Performance at a glance")

st.markdown(
    '<p class="section-note">'
    "Metrics update when you change the filters."
    "</p>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Sales", f"{total_sales:,.2f}")
k2.metric("Total Profit", f"{total_profit:,.2f}")
k3.metric("Unique Orders", f"{total_orders:,}")
k4.metric("Profit Margin", f"{profit_margin:.2f}%")

st.caption(
    f"Quantity sold: {total_quantity:,.0f} · "
    f"Selected sales as a share of all dataset sales: "
    f"{sales_share:.1f}%"
)

st.divider()


# ---------- SALES & PROFIT CHARTS ----------
st.markdown("### Sales and profitability")

chart_left, chart_right = st.columns(2, gap="large")

with chart_left:
    st.markdown("**Sales by category**")

    category_sales = (
        filtered_df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=True)
    )

    fig_sales = px.bar(
        category_sales,
        x="Sales",
        y="Category",
        orientation="h",
        text_auto=",.0f",
        color="Sales",
        color_continuous_scale=["#bfdbfe", "#1d4ed8"],
    )

    fig_sales.update_layout(
        height=340,
        margin=dict(l=0, r=10, t=15, b=10),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Sales",
        yaxis_title="",
    )

    st.plotly_chart(
        fig_sales,
        use_container_width=True,
    )


with chart_right:
    st.markdown("**Profit by category**")

    category_profit = (
        filtered_df.groupby("Category", as_index=False)["Profit"]
        .sum()
        .sort_values("Profit", ascending=True)
    )

    fig_profit = px.bar(
        category_profit,
        x="Profit",
        y="Category",
        orientation="h",
        text_auto=",.0f",
        color="Profit",
        color_continuous_scale=[
            "#fca5a5",
            "#bbf7d0",
            "#15803d",
        ],
        color_continuous_midpoint=0,
    )

    fig_profit.update_layout(
        height=340,
        margin=dict(l=0, r=10, t=15, b=10),
        showlegend=False,
        coloraxis_showscale=False,
        xaxis_title="Profit",
        yaxis_title="",
    )

    st.plotly_chart(
        fig_profit,
        use_container_width=True,
    )


# ---------- MONTHLY TREND ----------
st.divider()
st.markdown("### Sales trend over time")

st.markdown(
    '<p class="section-note">'
    "Monthly sales and profit for the selected period."
    "</p>",
    unsafe_allow_html=True,
)

monthly_df = filtered_df.dropna(
    subset=["Order Date"]
).copy()

monthly_df["Month"] = (
    monthly_df["Order Date"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

monthly = (
    monthly_df.groupby("Month", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
    )
    .sort_values("Month")
    .reset_index(drop=True)
)


# ---------- MONTH-OVER-MONTH GROWTH ----------
monthly["Previous Month Sales"] = monthly["Sales"].shift(1)

previous_month_sales = monthly[
    "Previous Month Sales"
].where(
    monthly["Previous Month Sales"] != 0
)

monthly["Sales Growth (%)"] = (
    (
        monthly["Sales"]
        - monthly["Previous Month Sales"]
    )
    / previous_month_sales
    * 100
)

if not monthly.empty:
    fig_trend = go.Figure()

    fig_trend.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Sales"],
            name="Sales",
            mode="lines+markers",
            line=dict(color="#2563eb", width=3),
            hovertemplate=(
                "Month: %{x|%b %Y}"
                "<br>Sales: %{y:,.2f}<extra></extra>"
            ),
        )
    )

    fig_trend.add_trace(
        go.Scatter(
            x=monthly["Month"],
            y=monthly["Profit"],
            name="Profit",
            mode="lines+markers",
            line=dict(color="#16a34a", width=3),
            hovertemplate=(
                "Month: %{x|%b %Y}"
                "<br>Profit: %{y:,.2f}<extra></extra>"
            ),
        )
    )

    fig_trend.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=25, b=10),
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
        ),
        xaxis_title="Month",
        yaxis_title="Amount",
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True,
    )


# ---------- MONTH-OVER-MONTH SALES GROWTH ----------
st.markdown("### 📈 Month-over-Month Sales Growth")

st.markdown(
    '<p class="section-note">'
    "Compares each month's sales with the previous month "
    "within the selected date range."
    "</p>",
    unsafe_allow_html=True,
)

growth_months = monthly.dropna(
    subset=["Sales Growth (%)"]
)

if not growth_months.empty:
    latest_growth = growth_months.iloc[-1]
    growth_value = float(
        latest_growth["Sales Growth (%)"]
    )

    st.metric(
        label=(
            "Latest available monthly growth — "
            f"{latest_growth['Month']:%B %Y}"
        ),
        value=f"{growth_value:.2f}%",
        delta=f"{growth_value:.2f}%",
        help=(
            "Growth = (current month sales - previous month sales) "
            "/ previous month sales."
        ),
    )
else:
    st.info(
        "Not enough monthly data to calculate growth. "
        "Select a date range containing at least two months."
    )

with st.expander("View monthly sales growth details"):
    growth_display = monthly[
        [
            "Month",
            "Sales",
            "Previous Month Sales",
            "Sales Growth (%)",
        ]
    ].copy()

    growth_display["Month"] = (
        growth_display["Month"].dt.strftime("%B %Y")
    )

    st.dataframe(
        growth_display.style.format(
            {
                "Sales": "{:,.2f}",
                "Previous Month Sales": "{:,.2f}",
                "Sales Growth (%)": "{:.2f}%",
            },
            na_rep="—",
        ),
        use_container_width=True,
        hide_index=True,
    )


# ---------- ADVANCED ANALYTICS ----------

st.divider()
st.markdown("## Advanced Business Analytics")


# 1. PRODUCT PROFITABILITY RANKINGS
st.markdown("### 🏆 Product Profitability Rankings")

product_rankings = (
    filtered_df.groupby("Product Name", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
    )
)

product_rankings["Profit Margin (%)"] = (
    product_rankings["Profit"]
    .div(product_rankings["Sales"].replace(0, float("nan")))
    .mul(100)
)

rank_left, rank_right = st.columns(2, gap="large")

with rank_left:
    st.markdown("**Top 10 Products by Profit**")

    top_products = product_rankings.nlargest(10, "Profit")

    fig_top = px.bar(
        top_products.sort_values("Profit"),
        x="Profit",
        y="Product Name",
        orientation="h",
        color="Profit",
        color_continuous_scale=["#bfdbfe", "#15803d"],
        title="Most Profitable Products",
    )
    fig_top.update_layout(
        height=450,
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_top, use_container_width=True)

with rank_right:
    st.markdown("**10 Lowest-Profit Products**")

    bottom_products = product_rankings.nsmallest(10, "Profit")

    fig_bottom = px.bar(
        bottom_products.sort_values("Profit"),
        x="Profit",
        y="Product Name",
        orientation="h",
        color="Profit",
        color_continuous_scale=["#dc2626", "#fecaca"],
        title="Lowest-Profit Products",
    )
    fig_bottom.update_layout(
        height=450,
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_bottom, use_container_width=True)

with st.expander("View complete product profitability rankings"):
    st.dataframe(
        product_rankings.sort_values("Profit", ascending=False).style.format(
            {
                "Sales": "{:,.2f}",
                "Profit": "{:,.2f}",
                "Quantity": "{:,.0f}",
                "Profit Margin (%)": "{:.2f}%",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# 2. DISCOUNT IMPACT ANALYSIS
st.divider()
st.markdown("### 🏷️ Discount Impact Analysis")
st.caption(
    "Compare profit margins across discount bands. "
    "These comparisons show associations, not proof that discounts caused losses."
)

discount_df = filtered_df.copy()

discount_df["Discount Band"] = pd.cut(
    discount_df["Discount"],
    bins=[-0.001, 0, 0.10, 0.20, 0.30, float("inf")],
    labels=[
        "No discount",
        "1–10%",
        "11–20%",
        "21–30%",
        "Above 30%",
    ],
    include_lowest=True,
)

discount_summary = (
    discount_df.groupby("Discount Band", observed=False, as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Records=("Discount", "size"),
    )
)

discount_summary["Profit Margin (%)"] = (
    discount_summary["Profit"]
    .div(discount_summary["Sales"].replace(0, float("nan")))
    .mul(100)
)

discount_left, discount_right = st.columns(2, gap="large")

with discount_left:
    fig_discount_profit = px.bar(
        discount_summary,
        x="Discount Band",
        y="Profit",
        color="Profit",
        color_continuous_scale=["#dc2626", "#fca5a5", "#15803d"],
        title="Profit by Discount Band",
    )
    fig_discount_profit.update_layout(
        height=370,
        xaxis_title="Discount",
        yaxis_title="Profit",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_discount_profit, use_container_width=True)

with discount_right:
    fig_discount_margin = px.bar(
        discount_summary,
        x="Discount Band",
        y="Profit Margin (%)",
        color="Profit Margin (%)",
        color_continuous_scale=["#dc2626", "#fca5a5", "#15803d"],
        title="Profit Margin by Discount Band",
    )
    fig_discount_margin.update_layout(
        height=370,
        xaxis_title="Discount",
        yaxis_title="Profit Margin (%)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_discount_margin, use_container_width=True)

st.dataframe(
    discount_summary.style.format(
        {
            "Sales": "{:,.2f}",
            "Profit": "{:,.2f}",
            "Quantity": "{:,.0f}",
            "Records": "{:,.0f}",
            "Profit Margin (%)": "{:.2f}%",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

loss_discount_bands = discount_summary[
    discount_summary["Profit"] < 0
]

if not loss_discount_bands.empty:
    st.warning(
        "Some discount bands have negative total profit. "
        "Review product mix, costs, order size and discount policy "
        "before deciding what changes to make."
    )


# 3. REGIONAL PERFORMANCE
st.divider()
st.markdown("### 🌍 Regional Performance")

region_summary = (
    filtered_df.groupby("Region", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
    )
)

region_summary["Profit Margin (%)"] = (
    region_summary["Profit"]
    .div(region_summary["Sales"].replace(0, float("nan")))
    .mul(100)
)

region_left, region_right = st.columns(2, gap="large")

with region_left:
    fig_region_sales = px.bar(
        region_summary.sort_values("Sales"),
        x="Sales",
        y="Region",
        orientation="h",
        color="Sales",
        color_continuous_scale=["#bfdbfe", "#1d4ed8"],
        title="Sales by Region",
    )
    fig_region_sales.update_layout(
        height=350,
        xaxis_title="Sales",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_region_sales, use_container_width=True)

with region_right:
    fig_region_margin = px.bar(
        region_summary.sort_values("Profit Margin (%)"),
        x="Profit Margin (%)",
        y="Region",
        orientation="h",
        color="Profit Margin (%)",
        color_continuous_scale=["#fecaca", "#15803d"],
        title="Profit Margin by Region",
    )
    fig_region_margin.update_layout(
        height=350,
        xaxis_title="Profit Margin (%)",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_region_margin, use_container_width=True)

st.markdown("**Regional comparison**")

st.dataframe(
    region_summary.sort_values("Profit", ascending=False).style.format(
        {
            "Sales": "{:,.2f}",
            "Profit": "{:,.2f}",
            "Quantity": "{:,.0f}",
            "Orders": "{:,.0f}",
            "Profit Margin (%)": "{:.2f}%",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

# ---------- PRODUCT PROFITABILITY ----------
st.divider()
st.markdown("### Product profitability")

st.markdown(
    '<p class="section-note">'
    "Find products contributing to profit and products "
    "that may need investigation."
    "</p>",
    unsafe_allow_html=True,
)

product_summary = (
    filtered_df.groupby(
        ["Category", "Sub-Category"],
        as_index=False,
    )
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Average_Discount=("Discount", "mean"),
    )
)

product_summary["Profit Margin (%)"] = (
    product_summary["Profit"]
    .div(
        product_summary["Sales"].replace(
            0, float("nan")
        )
    )
    .mul(100)
).fillna(0)

product_summary = product_summary.sort_values("Profit")

st.dataframe(
    product_summary.rename(
        columns={
            "Sub-Category": "Sub-category",
            "Average_Discount": "Average Discount",
        }
    ).style.format(
        {
            "Sales": "{:,.2f}",
            "Profit": "{:,.2f}",
            "Quantity": "{:,.0f}",
            "Average Discount": "{:.1%}",
            "Profit Margin (%)": "{:.2f}%",
        }
    ).map(
        lambda value: (
            "color: #dc2626; font-weight: bold"
            if isinstance(value, (int, float)) and value < 0
            else ""
        ),
        subset=["Profit"],
    ),
    use_container_width=True,
    hide_index=True,
)

loss_products = product_summary[
    product_summary["Profit"] < 0
]

if not loss_products.empty:
    st.warning(
        f"{len(loss_products)} sub-categories have negative "
        "total profit under the selected filters. Investigate "
        "them before making pricing or discount decisions."
    )


# ---------- AI BUSINESS INSIGHTS ----------
st.divider()
st.markdown("### ✨ AI Business Insights")

st.markdown(
    "Ask questions about the sales and profitability in your "
    "currently selected dataset. Answers are generated locally by Ollama."
)

ai_category = (
    filtered_df.groupby("Category", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
    )
)

ai_category["Profit Margin (%)"] = (
    ai_category["Profit"]
    / ai_category["Sales"].replace(0, float("nan"))
    * 100
).fillna(0)

ai_subcategory = (
    filtered_df.groupby(
        ["Category", "Sub-Category"],
        as_index=False,
    )
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Average_Discount=("Discount", "mean"),
    )
    .sort_values("Profit")
)

ai_top_products = (
    filtered_df.groupby(
        "Product Name",
        as_index=False,
    )
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
    )
    .sort_values("Profit", ascending=False)
    .head(10)
)

ai_loss_products = (
    filtered_df.groupby(
        "Product Name",
        as_index=False,
    )
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
    )
    .query("Profit < 0")
    .sort_values("Profit")
    .head(10)
)

data_context = f"""
ECOMMERCE DATA SUMMARY

Selected date range: {start_date} to {end_date}
Selected categories: {", ".join(selected_categories)}
Selected regions: {", ".join(selected_regions)}
Rows analyzed: {len(filtered_df)}

KEY METRICS
Total sales: {total_sales:.2f}
Total profit: {total_profit:.2f}
Unique orders: {total_orders}
Total quantity: {total_quantity}
Profit margin: {profit_margin:.2f}%

SALES AND PROFIT BY CATEGORY
{ai_category.round(2).to_string(index=False)}

PROFITABILITY BY SUB-CATEGORY
{ai_subcategory.round(2).to_string(index=False)}

TOP 10 PRODUCTS BY PROFIT
{ai_top_products.round(2).to_string(index=False)}

PRODUCTS WITH THE LARGEST LOSSES
{ai_loss_products.round(2).to_string(index=False)}

MONTHLY SALES AND GROWTH
{monthly.round(2).to_string(index=False)}
"""

if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []

# Show previous messages.
for message in st.session_state.ai_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.caption("Suggested questions")

suggestion_columns = st.columns(3)

suggestions = [
    "Which category is the most profitable?",
    "Which products are making losses?",
    "What should the business investigate to improve profit?",
]

for column, suggestion in zip(
    suggestion_columns,
    suggestions,
):
    with column:
        if st.button(
            suggestion,
            key=f"suggestion_{suggestion}",
            use_container_width=True,
        ):
            st.session_state["pending_ai_question"] = suggestion

user_question = st.chat_input(
    "Ask a question about your ecommerce data..."
)

if user_question:
    st.session_state["pending_ai_question"] = user_question

pending_question = st.session_state.pop(
    "pending_ai_question",
    None,
)

if pending_question:
    st.session_state.ai_messages.append(
        {
            "role": "user",
            "content": pending_question,
        }
    )

    with st.chat_message("user"):
        st.markdown(pending_question)

    conversation = [
        {
            "role": "system",
            "content": (
                "You are an ecommerce business analyst. Answer using "
                "the actual figures in the supplied data summary. "
                "Do not invent data or claim to have analyzed individual "
                "records beyond the summary. If the summary does not "
                "contain enough detail, say so. Distinguish observed "
                "patterns from proven causes. Give practical, clearly "
                "explained recommendations. Do not assume a currency "
                "symbol.\n\nDATA CONTEXT:\n" + data_context
            ),
        }
    ]

    conversation.extend(
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in st.session_state.ai_messages[-8:]
    )

    with st.chat_message("assistant"):
        with st.spinner("Analyzing your business data..."):
            try:
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "qwen2.5:3b",
                        "messages": conversation,
                        "stream": False,
                    },
                    timeout=180,
                )

                response.raise_for_status()

                answer = response.json()["message"]["content"]
                st.markdown(answer)

                st.session_state.ai_messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except requests.exceptions.ConnectionError:
                st.error(
                    "Cannot connect to Ollama. Check that Ollama is "
                    "running and its local API is available."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The AI took too long to respond. Try a shorter "
                    "question or try again."
                )

            except requests.exceptions.HTTPError as error:
                st.error(
                    f"Ollama returned an HTTP error: {error}"
                )

            except (KeyError, ValueError) as error:
                st.error(
                    f"Could not read the AI response: {error}"
                )

            except Exception as error:
                st.error(f"AI request failed: {error}")


st.caption("Ecommerce Intelligence · Portfolio project")

   