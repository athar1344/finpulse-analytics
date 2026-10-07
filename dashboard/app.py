"""FinPulse Analytics - Streamlit entrypoint."""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import streamlit as st

import config
from automation.refresh import run_refresh
from automation.report_generator import generate_all_reports
from dashboard import charts, kpi
from dashboard.filters import render_filters, sidebar_navigation

st.set_page_config(page_title="FinPulse Analytics", page_icon="📊", layout="wide")


@st.cache_data(ttl=300)
def load_processed_data() -> pd.DataFrame:
    if not os.path.exists(config.PROCESSED_FILE_PATH):
        return pd.DataFrame()
    return pd.read_csv(config.PROCESSED_FILE_PATH)


def render_overview(df: pd.DataFrame):
    st.subheader("Key Performance Indicators")
    kpis = kpi.compute_all_kpis(df)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.plotly_chart(charts.kpi_metric_card("Total Sales", kpis["total_sales"], prefix="$"),
                         use_container_width=True)
    with col2:
        st.plotly_chart(charts.kpi_metric_card("Total Expenses", kpis["total_expenses"], prefix="$"),
                         use_container_width=True)
    with col3:
        st.plotly_chart(charts.kpi_metric_card("Net Margin", kpis["net_margin_pct"], suffix="%"),
                         use_container_width=True)
    with col4:
        st.plotly_chart(charts.kpi_metric_card("Budget Variance", kpis["budget_variance_pct"], suffix="%"),
                         use_container_width=True)
    with col5:
        st.plotly_chart(charts.kpi_metric_card("Avg YoY Growth", kpis["avg_yoy_growth"], suffix="%"),
                         use_container_width=True)
    with col6:
        st.metric("Top Business Unit", kpis["top_business_unit"])

    st.markdown("---")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(charts.bar_chart_by_unit(df), use_container_width=True)
    with right:
        st.plotly_chart(charts.budget_vs_actual_bar(df), use_container_width=True)

    left2, right2 = st.columns(2)
    with left2:
        st.plotly_chart(charts.horizontal_bar_top10(df), use_container_width=True)
    with right2:
        st.plotly_chart(charts.bottom10_chart(df), use_container_width=True)


def render_trends(df: pd.DataFrame):
    st.subheader("Trend Analysis")
    st.plotly_chart(charts.monthly_trend_line(df), use_container_width=True)
    st.plotly_chart(charts.weekly_trend_line(df), use_container_width=True)
    st.plotly_chart(charts.heatmap_month_by_unit(df), use_container_width=True)


def render_composition(df: pd.DataFrame):
    st.subheader("Composition")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(charts.pie_chart_scenario_mix(df), use_container_width=True)
    with right:
        st.plotly_chart(charts.donut_chart_business_unit(df), use_container_width=True)
    st.plotly_chart(charts.treemap_chart(df), use_container_width=True)


def render_distribution(df: pd.DataFrame):
    st.subheader("Distribution")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(charts.histogram_distribution(df), use_container_width=True)
    with right:
        st.plotly_chart(charts.box_plot(df), use_container_width=True)
    st.plotly_chart(charts.scatter_plot(df), use_container_width=True)


def render_data_explorer(df: pd.DataFrame):
    st.subheader("Data Explorer")
    st.dataframe(df, use_container_width=True, height=500)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download Filtered Data (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_financial_data.csv",
            mime="text/csv",
        )
    with col2:
        if st.button("Generate Excel + PDF + CSV Reports"):
            with st.spinner("Generating reports..."):
                paths = generate_all_reports(df)
            st.success("Reports generated in the reports/ directory")
            st.json(paths)


def main():
    st.title("📊 FinPulse Analytics")
    st.caption("Automated financial dashboard — Business Understanding → Automation → Reporting")

    with st.sidebar:
        if st.button("🔄 Refresh Data (scan data/raw)"):
            with st.spinner("Running ingestion pipeline..."):
                result = run_refresh()
            st.cache_data.clear()
            st.toast(f"Refresh: {result['status']}")

    page = sidebar_navigation()

    df = load_processed_data()
    if df.empty:
        st.warning(
            "No processed data found. Drop a source file into `data/raw/` and click "
            "'Refresh Data' in the sidebar, or run `python automation/refresh.py`."
        )
        st.stop()

    filtered = render_filters(df)
    if filtered.empty:
        st.info("No rows match the current filters.")
        st.stop()

    if page == "Overview":
        render_overview(filtered)
    elif page == "Trends":
        render_trends(filtered)
    elif page == "Composition":
        render_composition(filtered)
    elif page == "Distribution":
        render_distribution(filtered)
    elif page == "Data Explorer":
        render_data_explorer(filtered)


if __name__ == "__main__":
    main()
