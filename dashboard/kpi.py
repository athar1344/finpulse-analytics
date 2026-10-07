"""KPI calculations derived from the filtered dataset."""
import numpy as np
import pandas as pd


def total_sales(df: pd.DataFrame) -> float:
    return df.loc[(df["Account"] == "Sales") & (df["Scenario"] == "Actuals"), "annual_total"].sum()


def total_expenses(df: pd.DataFrame) -> float:
    mask = (df["Account"] != "Sales") & (df["Scenario"] == "Actuals")
    return abs(df.loc[mask, "annual_total"].sum())


def net_margin_pct(df: pd.DataFrame) -> float:
    sales = total_sales(df)
    expenses = total_expenses(df)
    if sales == 0:
        return 0.0
    return (sales - expenses) / sales * 100


def budget_variance_pct(df: pd.DataFrame) -> float:
    actual = df.loc[(df["Account"] == "Sales") & (df["Scenario"] == "Actuals"), "annual_total"].sum()
    budget = df.loc[(df["Account"] == "Sales") & (df["Scenario"] == "Budget"), "annual_total"].sum()
    if budget == 0:
        return 0.0
    return (actual - budget) / abs(budget) * 100


def top_business_unit(df: pd.DataFrame) -> str:
    mask = (df["Account"] == "Sales") & (df["Scenario"] == "Actuals")
    if not mask.any():
        return "N/A"
    grouped = df.loc[mask].groupby("business_unit")["annual_total"].sum()
    if grouped.empty:
        return "N/A"
    return grouped.idxmax()


def avg_yoy_growth(df: pd.DataFrame) -> float:
    mask = (df["Account"] == "Sales") & (df["Scenario"] == "Actuals")
    values = df.loc[mask, "yoy_growth_pct"].dropna()
    if values.empty:
        return 0.0
    return values.mean()


def compute_all_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_sales": total_sales(df),
        "total_expenses": total_expenses(df),
        "net_margin_pct": net_margin_pct(df),
        "budget_variance_pct": budget_variance_pct(df),
        "top_business_unit": top_business_unit(df),
        "avg_yoy_growth": avg_yoy_growth(df),
    }
