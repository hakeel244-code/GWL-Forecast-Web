import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="AI Groundwater Forecast",
    page_icon="💧",
    layout="wide"
)

# Title
st.title("💧 AI-Based Groundwater Level Forecasting")
st.subheader("Machine Learning-Based Groundwater Forecasting — 2026")
st.write("Select a monitoring station to explore its predicted groundwater levels.")

# Data location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Find the forecast CSV files
def find_file(filename):
    possible_paths = [
        os.path.join(BASE_DIR, "GWL_ML_outputs", filename),
        os.path.join(BASE_DIR, filename)
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

# Load station summary
summary_path = find_file("forecast_2026_station_summary.csv")

if summary_path is None:
    st.error(
        "Station summary file not found. "
        "Please check that forecast_2026_station_summary.csv "
        "is inside the project folder or GWL_ML_outputs folder."
    )
    st.stop()

summary = pd.read_csv(summary_path)

# Load monthly forecasts
monthly_path = find_file("forecast_2026_monthly_by_station.csv")

if monthly_path is None:
    st.error("Monthly forecast CSV file was not found.")
    st.stop()

monthly = pd.read_csv(monthly_path)

# Sidebar
st.sidebar.header("Forecast Settings")

districts = sorted(summary["district"].dropna().astype(str).unique())

selected_district = st.sidebar.selectbox(
    "Select District",
    ["All Districts"] + districts
)

filtered = summary.copy()

if selected_district != "All Districts":
    filtered = filtered[
        filtered["district"].astype(str) == selected_district
    ]

stations = sorted(filtered["station"].dropna().astype(str).unique())

if not stations:
    st.warning("No stations found for this district.")
    st.stop()

selected_station = st.sidebar.selectbox(
    "Select Monitoring Station",
    stations
)

# Selected station information
station = summary[
    summary["station"].astype(str) == selected_station
].iloc[0]

st.header(f"📍 {selected_station}")
st.write(f"**District:** {station['district']}")

# Forecast summary
col1, col2, col3 = st.columns(3)

col1.metric(
    "Mean Predicted Depth",
    f"{station['pred_mean_2026']:.2f} m"
)

col2.metric(
    "Minimum Predicted Depth",
    f"{station['pred_min_2026']:.2f} m"
)

col3.metric(
    "Maximum Predicted Depth",
    f"{station['pred_max_2026']:.2f} m"
)

# Trend and reliability
col4, col5 = st.columns(2)

col4.metric(
    "Groundwater Trend",
    str(station["trend"])
)

col5.metric(
    "Forecast Reliability",
    str(station["reliability"])
)

st.info(
    "Groundwater depth is measured in metres below ground level (m bgl). "
    "A larger value means the water table is deeper."
)

# Monthly forecast
st.header("📊 Monthly Groundwater Forecast — 2026")

station_monthly = monthly[
    monthly["station"].astype(str) == selected_station
].copy()

if station_monthly.empty:
    st.warning("No monthly forecasts available for this station.")
else:
    if "month" in station_monthly.columns:
        month_names = {
            1: "January", 2: "February", 3: "March",
            4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September",
            10: "October", 11: "November", 12: "December"
        }

        station_monthly["Month"] = station_monthly["month"].map(
            lambda x: month_names.get(int(x), str(x))
            if pd.notna(x) else ""
        )

        station_monthly["Month"] = pd.Categorical(
            station_monthly["Month"],
            categories=list(month_names.values()),
            ordered=True
        )

        station_monthly = station_monthly.sort_values("Month")

    fig = px.line(
        station_monthly,
        x="Month",
        y="pred_dtw_mbgl",
        markers=True,
        title=f"Predicted Groundwater Depth: {selected_station}",
        labels={
            "Month": "Month",
            "pred_dtw_mbgl": "Depth (m below ground level)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Forecast Table")
    st.dataframe(
        station_monthly,
        use_container_width=True,
        hide_index=True
    )

    # Download selected station forecast
    st.download_button(
        "📥 Download Monthly Forecast",
        data=station_monthly.to_csv(index=False).encode("utf-8"),
        file_name="groundwater_monthly_forecast_2026.csv",
        mime="text/csv"
    )

# Station summary
st.header("📋 Groundwater Station Summary")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    "📥 Download Station Summary",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="groundwater_station_summary_2026.csv",
    mime="text/csv"
)

# Footer
st.divider()

st.caption(
    "AI-Based Groundwater Level Forecasting Project | 2026. "
    "Forecasts are estimates and should be validated with field measurements."
)
