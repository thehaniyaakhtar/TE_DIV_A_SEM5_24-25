import streamlit as st
import requests
import matplotlib.pyplot as plt
import datetime
import numpy as np

# Custom CSS for Background Image and Styling
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #0f2027, #203a43, #2c5364),
                    url('https://source.unsplash.com/1600x900/?finance,stock,market');
        background-size: cover;
        background-attachment: fixed;
        color: white;
    }
    h1, h2, h3, h4 {
        font-family: 'Arial', sans-serif;
        color: #f5f5f5;
        text-align: center;
    }
    .sidebar .sidebar-content {
        background-color: rgba(0, 0, 0, 0.8);
        padding: 10px;
        border-radius: 10px;
    }
    .stButton button {
        background-color: #1f77b4;
        color: white;
        border-radius: 10px;
    }
    .stCheckbox span {
        color: white;
    }
    .stPlotlyChart {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True
)

# API URL for fetching mutual fund data
MF_API_BASE_URL = "https://api.mfapi.in/mf"

# Fund categories based on risk level, fund type, and NAV performance
funds = {
    "Low Risk": ["118266", "118274"],     # Replace with actual Low Risk Fund IDs
    "Medium Risk": ["118291", "120503"],  # Replace with actual Medium Risk Fund IDs
    "High Risk": ["120500", "120504"],    # Replace with actual High Risk Fund IDs
    "Equity": ["120516", "120517"],       # Replace with actual Equity Fund IDs
    "Debt": ["120518", "120519"],         # Replace with actual Debt Fund IDs
    "Top Performers": ["120520", "120521"], # Replace with actual Top Performer Fund IDs
    "Moderate Performers": ["120522", "120523"] # Replace with actual Moderate Performer Fund IDs
}

# Fetch detailed mutual fund data from API
def fetch_fund_data(fund_id):
    try:
        response = requests.get(f"{MF_API_BASE_URL}/{fund_id}")
        if response.status_code == 200:
            fund_data = response.json()
            if fund_data and 'meta' in fund_data:
                return {
                    "name": fund_data["meta"]["scheme_name"],
                    "fund_type": fund_data["meta"]["scheme_type"],
                    "fund_category": fund_data["meta"]["scheme_category"],
                    "NAV": float(fund_data["data"][0]["nav"])
                }
            else:
                st.error("Fund data not available.")
        else:
            st.error(f"Error fetching data for fund ID: {fund_id}")
    except Exception as e:
        st.error(f"An error occurred while fetching fund data: {e}")
    return None

# Fetch historical NAV data for a fund
def fetch_fund_history(fund_id):
    try:
        response = requests.get(f"{MF_API_BASE_URL}/{fund_id}")
        if response.status_code == 200:
            fund_data = response.json()
            if fund_data and 'data' in fund_data:
                return [
                    {"date": item["date"], "nav": float(item["nav"])}
                    for item in fund_data["data"]
                ]
            else:
                st.error("Historical data not available.")
        else:
            st.error(f"Error fetching historical data for fund ID: {fund_id}")
    except Exception as e:
        st.error(f"An error occurred while fetching historical data: {e}")
    return []

# Display fund details based on the fund ID provided by the user
def display_fund_details(fund_id):
    fund_data = fetch_fund_data(fund_id)
    if fund_data:
        st.write(f"**Fund Provider**: {fund_data['name']} (ID: {fund_id})")
        st.write(f"**Type**: {fund_data['fund_type']}")
        st.write(f"**Category**: {fund_data['fund_category']}")
        st.write(f"**Current NAV**: ₹{fund_data['NAV']}")
        return True
    else:
        st.error("Invalid fund ID or data not available.")
        return False

# Show NAV graph with options for trend, growth, and average
def show_all_fund_graphs(fund_id):
    history = fetch_fund_history(fund_id)
    if not history:
        return

    dates = [datetime.datetime.strptime(item["date"], "%d-%m-%Y") for item in history]
    navs = [item["nav"] for item in history]

    st.write("### NAV History")
    plt.figure(figsize=(10, 5))
    plt.plot(dates, navs, label="NAV", color="blue", marker="o")
    plt.title(f"NAV History for Fund ID: {fund_id}")
    plt.xlabel("Date")
    plt.ylabel("NAV (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    st.write("### 10-day Moving Average NAV")
    plt.figure(figsize=(10, 5))
    moving_avg = np.convolve(navs, np.ones(10)/10, mode='valid')
    plt.plot(dates[len(dates) - len(moving_avg):], moving_avg, label="10-day Moving Avg", color="green", marker="o")
    plt.title(f"10-day Moving Average NAV for Fund ID: {fund_id}")
    plt.xlabel("Date")
    plt.ylabel("NAV (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    st.write("### NAV Growth Percentage")
    plt.figure(figsize=(10, 5))
    initial_nav = navs[0]
    growth = [(nav - initial_nav) / initial_nav * 100 for nav in navs]
    plt.plot(dates, growth, label="Growth %", color="orange", marker="o")
    plt.title(f"Growth Percentage for Fund ID: {fund_id}")
    plt.xlabel("Date")
    plt.ylabel("Growth (%)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

    st.write("### Average NAV")
    plt.figure(figsize=(10, 5))
    average_nav = np.mean(navs)
    plt.axhline(y=average_nav, color='red', linestyle='--', label=f'Average NAV: ₹{average_nav:.2f}')
    plt.plot(dates, navs, label="NAV", color="blue", marker="o")
    plt.title(f"Average NAV for Fund ID: {fund_id}")
    plt.xlabel("Date")
    plt.ylabel("NAV (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.legend()
    st.pyplot(plt)

# Main function to display the Streamlit interface
def main():
    st.title("Mutual Funds Portal")

    # Create a list for available mutual funds
    fund_data_list = []
    for category, fund_ids in funds.items():
        for fund_id in fund_ids:
            fund_data = fetch_fund_data(fund_id)
            if fund_data:
                provider_name = fund_data['name'].split()[0]
                fund_data_list.append(f"{provider_name} (ID: {fund_id})")

    if not fund_data_list:
        st.warning("No mutual funds available.")
    else:
        selected_fund = st.selectbox(
            "Select a Mutual Fund to view details and graphs", 
            options=fund_data_list
        )

    custom_fund_id = st.text_input("Or enter a Fund ID")

    fund_id = None
    if selected_fund:
        fund_id = selected_fund.split("ID: ")[1].strip(')')
    elif custom_fund_id:
        fund_id = custom_fund_id.strip()

    if fund_id:
        if display_fund_details(fund_id):
            st.write("Displaying all graphs for the selected mutual fund...")
            show_all_fund_graphs(fund_id)

if __name__ == "__main__":
    main()
