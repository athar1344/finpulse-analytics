"""Feature engineering: totals, margins, YoY growth, variance."""
import numpy as np
import pandas as pd

import config


def add_annual_total(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["annual_total"] = df[config.MONTH_COLUMNS].sum(axis=1)
    return df


def add_quarter_totals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Q1"] = df[["Jan", "Feb", "Mar"]].sum(axis=1)
    df["Q2"] = df[["Apr", "May", "Jun"]].sum(axis=1)
    df["Q3"] = df[["Jul", "Aug", "Sep"]].sum(axis=1)
    df["Q4"] = df[["Oct", "Nov", "Dec"]].sum(axis=1)
    return df


def add_variance_flag(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_actual"] = df["Scenario"].str.lower() == "actuals"
    df["is_budget_or_forecast"] = df["Scenario"].str.lower().isin(["budget", "forecast"])
    return df


def add_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["Account", "business_unit", "Scenario", "Year"])["annual_total"]
        .sum()
        .reset_index()
        .sort_values(["Account", "business_unit", "Scenario", "Year"])
    )
    grouped["prior_year_total"] = grouped.groupby(
        ["Account", "business_unit", "Scenario"]
    )["annual_total"].shift(1)
    grouped["yoy_growth_pct"] = np.where(
        (grouped["prior_year_total"].notna()) & (grouped["prior_year_total"] != 0),
        (grouped["annual_total"] - grouped["prior_year_total"]) / grouped["prior_year_total"].abs() * 100,
        np.nan,
    )
    merge_cols = ["Account", "business_unit", "Scenario", "Year", "yoy_growth_pct"]
    return df.merge(grouped[merge_cols], on=["Account", "business_unit", "Scenario", "Year"], how="left")


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_annual_total(df)
    df = add_quarter_totals(df)
    df = add_variance_flag(df)
    df = add_yoy_growth(df)
    return df
