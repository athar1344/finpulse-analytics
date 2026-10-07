"""Sidebar navigation and interactive filter widgets."""
import pandas as pd
import streamlit as st


def sidebar_navigation() -> str:
    st.sidebar.title("FinPulse Analytics")
    page = st.sidebar.radio(
        "Navigate",
        ["Overview", "Trends", "Composition", "Distribution", "Data Explorer"],
    )
    st.sidebar.markdown("---")
    return page


def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    years = sorted(df["Year"].dropna().unique().tolist())
    selected_years = st.sidebar.multiselect("Year", years, default=years)

    units = sorted(df["business_unit"].dropna().unique().tolist())
    selected_units = st.sidebar.multiselect("Business Unit", units, default=units)

    scenarios = sorted(df["Scenario"].dropna().unique().tolist())
    selected_scenarios = st.sidebar.multiselect("Scenario", scenarios, default=scenarios)

    search_term = st.sidebar.text_input("Search Account")

    filtered = df.copy()
    if selected_years:
        filtered = filtered[filtered["Year"].isin(selected_years)]
    if selected_units:
        filtered = filtered[filtered["business_unit"].isin(selected_units)]
    if selected_scenarios:
        filtered = filtered[filtered["Scenario"].isin(selected_scenarios)]
    if search_term:
        filtered = filtered[filtered["Account"].str.contains(search_term, case=False, na=False)]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"{len(filtered):,} rows match current filters")

    return filtered
