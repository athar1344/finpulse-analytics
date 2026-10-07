"""Reusable Plotly chart builders. Each function takes a filtered DataFrame
and returns a ready-to-render Plotly figure."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

MONTH_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def kpi_metric_card(label: str, value: float, prefix: str = "", suffix: str = "",
                     delta: float = None, color: str = "rgba(0, 104, 201, 0.25)") -> go.Figure:
    fig = go.Figure()
    indicator_kwargs = dict(
        value=value,
        number={"prefix": prefix, "suffix": suffix, "font": {"size": 26}},
        title={"text": label, "font": {"size": 15}},
        mode="number",
    )
    if delta is not None:
        indicator_kwargs["mode"] = "number+delta"
        indicator_kwargs["delta"] = {"reference": value - delta, "relative": False}
    fig.add_trace(go.Indicator(**indicator_kwargs))
    fig.update_layout(height=120, margin=dict(t=40, b=10, l=10, r=10))
    return fig


def monthly_trend_line(df: pd.DataFrame, group_col: str = "Scenario") -> go.Figure:
    melted = df.melt(
        id_vars=[group_col], value_vars=MONTH_ORDER, var_name="month", value_name="value"
    )
    agg = melted.groupby([group_col, "month"], as_index=False)["value"].sum()
    agg["month"] = pd.Categorical(agg["month"], categories=MONTH_ORDER, ordered=True)
    agg = agg.sort_values("month")
    fig = px.line(agg, x="month", y="value", color=group_col, markers=True, title="Monthly Trend")
    return fig


def weekly_trend_line(df: pd.DataFrame) -> go.Figure:
    melted = df.melt(id_vars=["Year"], value_vars=MONTH_ORDER, var_name="month", value_name="value")
    agg = melted.groupby("month", as_index=False)["value"].sum()
    agg["month"] = pd.Categorical(agg["month"], categories=MONTH_ORDER, ordered=True)
    agg = agg.sort_values("month")
    agg["cumulative"] = agg["value"].cumsum()
    fig = px.line(agg, x="month", y="cumulative", markers=True, title="Cumulative Trend (Proxy for Weekly)")
    return fig


def bar_chart_by_unit(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("business_unit", as_index=False)["annual_total"].sum()
    fig = px.bar(agg, x="business_unit", y="annual_total", text_auto=".2s",
                 title="Total by Business Unit", color="business_unit")
    return fig


def horizontal_bar_top10(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("Account", as_index=False)["annual_total"].sum()
    agg = agg.sort_values("annual_total", ascending=False).head(10)
    fig = px.bar(agg, x="annual_total", y="Account", orientation="h",
                 title="Top 10 Accounts by Value", text_auto=".2s")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def bottom10_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("Account", as_index=False)["annual_total"].sum()
    agg = agg.sort_values("annual_total", ascending=True).head(10)
    fig = px.bar(agg, x="annual_total", y="Account", orientation="h",
                 title="Bottom 10 Accounts by Value", text_auto=".2s",
                 color_discrete_sequence=["#FF2B2B"])
    fig.update_layout(yaxis={"categoryorder": "total descending"})
    return fig


def pie_chart_scenario_mix(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("Scenario", as_index=False)["annual_total"].sum()
    agg["annual_total"] = agg["annual_total"].abs()
    fig = px.pie(agg, names="Scenario", values="annual_total", title="Scenario Mix")
    return fig


def donut_chart_business_unit(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("business_unit", as_index=False)["annual_total"].sum()
    agg["annual_total"] = agg["annual_total"].abs()
    fig = px.pie(agg, names="business_unit", values="annual_total", hole=0.5,
                 title="Business Unit Share")
    return fig


def histogram_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(df, x="annual_total", nbins=30, title="Distribution of Annual Totals")
    return fig


def scatter_plot(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby(["Account", "business_unit"], as_index=False).agg(
        annual_total=("annual_total", "sum"), yoy_growth_pct=("yoy_growth_pct", "mean")
    )
    fig = px.scatter(agg, x="annual_total", y="yoy_growth_pct", color="business_unit",
                      hover_name="Account", title="Value vs YoY Growth")
    return fig


def box_plot(df: pd.DataFrame) -> go.Figure:
    fig = px.box(df, x="business_unit", y="annual_total", color="business_unit",
                 title="Spread of Annual Totals by Business Unit")
    return fig


def heatmap_month_by_unit(df: pd.DataFrame) -> go.Figure:
    agg = df.groupby("business_unit")[MONTH_ORDER].sum()
    fig = px.imshow(agg, labels=dict(x="Month", y="Business Unit", color="Value"),
                     title="Heatmap: Business Unit x Month", aspect="auto",
                     color_continuous_scale="Blues")
    return fig


def treemap_chart(df: pd.DataFrame) -> go.Figure:
    agg = df.copy()
    agg["annual_total_abs"] = agg["annual_total"].abs()
    agg = agg.groupby(["business_unit", "Account"], as_index=False)["annual_total_abs"].sum()
    agg = agg[agg["annual_total_abs"] > 0]
    fig = px.treemap(agg, path=["business_unit", "Account"], values="annual_total_abs",
                      title="Treemap: Business Unit -> Account")
    return fig


def budget_vs_actual_bar(df: pd.DataFrame) -> go.Figure:
    mask = df["Scenario"].isin(["Actuals", "Budget", "Forecast"])
    agg = df.loc[mask].groupby(["business_unit", "Scenario"], as_index=False)["annual_total"].sum()
    fig = px.bar(agg, x="business_unit", y="annual_total", color="Scenario", barmode="group",
                 title="Budget vs Forecast vs Actuals")
    return fig
