"""Data cleaning: missing values, duplicates, dtype correction, standardization."""
import numpy as np
import pandas as pd

import config


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
    for col in config.MONTH_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    text_cols = ["Account", "business_unit", "Currency", "Scenario"]
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


def standardize_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["business_unit"] = df["business_unit"].str.title()
    df["Scenario"] = df["Scenario"].str.title()
    df["Currency"] = df["Currency"].str.upper()
    df["Account"] = df["Account"].str.strip()
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[config.MONTH_COLUMNS] = df[config.MONTH_COLUMNS].fillna(0.0)
    df = df.dropna(subset=["Account", "business_unit", "Year", "Scenario"])
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=config.DEDUPE_KEYS, keep="last")
    removed = before - len(df)
    return df, removed


def remove_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df[df["Year"].notna()]
    df = df[(df["Year"] >= 2000) & (df["Year"] <= 2100)]
    df = df[df["Account"] != ""]
    df = df[df["business_unit"] != ""]
    return df


def clean_dataframe(df: pd.DataFrame) -> tuple:
    df = fix_data_types(df)
    df = standardize_text(df)
    df = handle_missing_values(df)
    df = remove_invalid_rows(df)
    df, duplicates_removed = remove_duplicates(df)
    return df.reset_index(drop=True), duplicates_removed
