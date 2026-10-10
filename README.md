# Ecommerce Intelligence Dashboard

An interactive e-commerce analytics dashboard built using Python, SQL, MySQL, and Streamlit to analyze sales, profitability, product performance, discount impact, and regional trends. Includes an AI-powered business insights assistant using a locally running Ollama model.

# Features

- Interactive KPI cards for total sales, total profit, unique orders, and profit margin.
- Dynamic filters for order date, category, and region.
- Sales and profit analysis by category.
- Monthly sales and profit trends.
- Month-over-month sales growth analysis.
- Product profitability analysis by category and sub-category.
- Top 10 and bottom 10 products by profit.
- Discount band impact analysis.
- Regional sales and profitability analysis.
- AI-powered business insights using Ollama.

# Technologies Used

- Python
- SQL
- MySQL
- Pandas
- Streamlit
- Plotly
- python-dotenv
- Ollama

# Business Questions

- Which categories generate the highest sales and profit?
- Which products and sub-categories are loss-making?
- How does profit margin vary across discount levels?
- Which regions perform best?
- How do sales and profit change over time?

# Key Findings

The analysis highlights differences in profitability across product categories, sub-categories, and discount levels. Some product groups show significantly lower margins at higher discount levels.

An association between discounts and profitability does not necessarily prove that discounts cause lower profits.

# Setup Instructions

## 1. Clone the Repository

    git clone https://github.com/Shan1034/ecommerce-intelligence.git

    cd ecommerce-intelligence

## 2. Create a Virtual Environment

    python -m venv .venv

Activate it on Windows:

    .venv\Scripts\Activate.ps1

## 3. Install Dependencies

    pip install -r requirements.txt

## 4. Configure MySQL

Create a file named `.env` in the project folder and add your database settings:

    DB_HOST=127.0.0.1
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=your_mysql_password
    DB_NAME=ecommerce_project

Replace the placeholder with your own MySQL password. Never upload real credentials.

Ensure MySQL is running and the required dataset has been imported into the database.

## 5. Configure the AI Assistant

Install Ollama and ensure the model configured in the application is available locally. Start the Ollama service before using the AI assistant.

## 6. Run the Dashboard

    streamlit run dashboard.py

# Limitations

- Dashboard results depend on the quality of the underlying dataset.
- The AI assistant requires a working local Ollama service.
- Findings reflect the dataset and filters selected.

# Future Improvements

- Sales forecasting.
- Customer segmentation.
- Automated business reports.
- Online deployment.

# Author

Shanmathi Prakash

Data Analyst | SQL | Python | MySQL | Data Visualization
