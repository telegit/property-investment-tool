"""
Real Estate Investment Analyzer — Streamlit dashboard
Powered by real-estate-market-data.p.rapidapi.com
"""
import io
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from streamlit_echarts import st_echarts

from market_client import get_property_estimate

load_dotenv()

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Real Estate Analyzer",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Real Estate Investment Analyzer")
st.caption("Market valuations & investment metrics · Powered by RapidAPI")

# ---------------------------------------------------------------------------
# Sidebar — inputs
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Property Specs")

    zip_input = st.text_area(
        "Zip Code(s)",
        placeholder="One per line, e.g.\n78701\n90210\n10001",
        height=100,
    )

    bedrooms = st.slider("Bedrooms", min_value=1, max_value=6, value=3)
    bathrooms = st.slider("Bathrooms", min_value=1, max_value=5, value=2)
    sqft = st.slider("Square Footage", min_value=500, max_value=5000, value=1600, step=100)

    st.divider()
    analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
if not analyze_clicked:
    st.info("Enter one or more zip codes in the sidebar and click **Analyze**.")
    st.stop()

zip_codes = [z.strip() for z in zip_input.strip().splitlines() if z.strip()]
if not zip_codes:
    st.error("Please enter at least one zip code.")
    st.stop()

# ---------------------------------------------------------------------------
# Fetch data for each zip
# ---------------------------------------------------------------------------
results = []
errors = []

progress = st.progress(0, text="Fetching data...")
for i, zc in enumerate(zip_codes):
    try:
        data = get_property_estimate(zc, bedrooms, bathrooms, sqft)
        im = data.get("investment_metrics", {})
        results.append({
            "Zip Code": zc,
            "Est. Value ($)": data.get("estimated_value"),
            "Value Low ($)": data.get("value_range_low"),
            "Value High ($)": data.get("value_range_high"),
            "Gross Yield (%)": data.get("gross_yield_pct"),
            "Cap Rate (%)": im.get("cap_rate_pct"),
            "Cash-on-Cash (%)": im.get("cash_on_cash_return_pct"),
            "Monthly Cash Flow ($)": im.get("monthly_cash_flow"),
            "Monthly Rent ($)": im.get("estimated_monthly_rent"),
            "Monthly Mortgage ($)": im.get("monthly_mortgage"),
            "Down Payment ($)": im.get("down_payment_20pct"),
            "Investment Rating": im.get("investment_rating", ""),
            "Data Source": data.get("data_source", ""),
        })
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        errors.append(f"Zip {zc}: {e}")
    progress.progress((i + 1) / len(zip_codes), text=f"Fetched {zc}...")

progress.empty()

if errors:
    for err in errors:
        st.warning(err)

if not results:
    st.error("No data returned. Check your zip codes and API key.")
    st.stop()

df = pd.DataFrame(results)

# ---------------------------------------------------------------------------
# Metrics row (first zip or single result)
# ---------------------------------------------------------------------------
first = results[0]
col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Est. Value",
    f"${first['Est. Value ($)']:,.0f}" if first["Est. Value ($)"] else "N/A",
    help="Estimated market value for the specified property configuration in this zip code. "
         "Derived from comparable sales (comps) in the area.\n\n"
         "**Source:** Redfin MLS",
)
col2.metric(
    "Value Range",
    f"${first['Value Low ($)']:,.0f} – ${first['Value High ($)']:,.0f}"
    if first["Value Low ($)"] else "N/A",
    help="The low–high spread of estimated values based on comp variance in the zip code. "
         "A wider range indicates a less uniform market.\n\n"
         "**Calculation:** ±12% around the mid estimate\n"
         "**Source:** Redfin MLS",
)
col3.metric(
    "Cap Rate",
    f"{first['Cap Rate (%)']:.2f}%" if first["Cap Rate (%)"] else "N/A",
    help="Capitalization Rate — the unlevered (pre-financing) return on a property.\n\n"
         "**Calculation:** Net Operating Income ÷ Property Value\n"
         "where NOI = Annual Rent × (1 − Expense Ratio)\n\n"
         "Typical range: 3–6% in urban markets. Higher = better yield relative to price.\n\n"
         "**Source:** Derived from estimated rent and value",
)
col4.metric(
    "Monthly Cash Flow",
    f"${first['Monthly Cash Flow ($)']:+,.0f}" if first["Monthly Cash Flow ($)"] is not None else "N/A",
    help="Estimated monthly profit or loss after all costs.\n\n"
         "**Calculation:** Estimated Monthly Rent − Monthly Mortgage − Operating Expenses\n\n"
         "Assumes 20% down, 7% mortgage rate, 30-year loan, 40% expense ratio.\n"
         "Positive = cash-flow positive rental. Negative = out-of-pocket each month.\n\n"
         "**Source:** Derived from estimated rent and value",
)

st.divider()

# ---------------------------------------------------------------------------
# ECharts — Value Range Comparison (grouped bar)
# ---------------------------------------------------------------------------
_vc1, _vc2 = st.columns([8, 1])
_vc1.subheader("Estimated Value Comparison")
with _vc2.popover("ℹ️"):
    st.markdown(
        "**Estimated Value Comparison**\n\n"
        "Compares property value estimates across zip codes for the same bedroom/bath/sqft configuration.\n\n"
        "- 🟢 **Low Estimate** — 10th-percentile comp value in the zip\n"
        "- 🔵 **Mid Estimate** — median estimated market value\n"
        "- 🔴 **High Estimate** — 90th-percentile comp value in the zip\n\n"
        "**Calculation:** Comparable sales (comps) filtered by bed/bath/sqft proximity\n\n"
        "**Source:** Redfin MLS via RapidAPI"
    )

zips = df["Zip Code"].tolist()
est_vals = df["Est. Value ($)"].fillna(0).tolist()
low_vals = df["Value Low ($)"].fillna(0).tolist()
high_vals = df["Value High ($)"].fillna(0).tolist()

value_chart = {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
    "legend": {"data": ["Low Estimate", "Mid Estimate", "High Estimate"]},
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": {"type": "category", "data": zips},
    "yAxis": {"type": "value", "name": "Value ($)", "axisLabel": {"formatter": "${value}"}},
    "series": [
        {
            "name": "Low Estimate",
            "type": "bar",
            "data": low_vals,
            "itemStyle": {"color": "#91CC75"},
        },
        {
            "name": "Mid Estimate",
            "type": "bar",
            "data": est_vals,
            "itemStyle": {"color": "#006AFF"},
        },
        {
            "name": "High Estimate",
            "type": "bar",
            "data": high_vals,
            "itemStyle": {"color": "#EE6666"},
        },
    ],
}
st_echarts(options=value_chart, height="350px")

# ---------------------------------------------------------------------------
# ECharts — Investment Metrics (Cap Rate + Cash-on-Cash)
# ---------------------------------------------------------------------------
if len(df) > 1:
    _mc1, _mc2 = st.columns([8, 1])
    _mc1.subheader("Investment Metrics by Zip")
    with _mc2.popover("ℹ️"):
        st.markdown(
            "**Investment Metrics by Zip**\n\n"
            "Compares two key return metrics side-by-side across zip codes.\n\n"
            "**Cap Rate (%)**\n"
            "Unlevered return — ignores financing. Best for comparing markets apples-to-apples.\n"
            "Formula: `NOI ÷ Property Value`\n"
            "where `NOI = Annual Rent × (1 − 0.40 expense ratio)`\n\n"
            "**Cash-on-Cash Return (%)**\n"
            "Levered return — accounts for your actual cash invested (down payment).\n"
            "Formula: `Annual Cash Flow ÷ Down Payment`\n"
            "Negative values mean the property costs money each month after financing.\n\n"
            "**Assumptions:** 20% down · 7.0% mortgage rate · 30-year loan · 40% expense ratio\n\n"
            "**Source:** Derived from estimated rent and value · Redfin MLS"
        )

    cap_rates = df["Cap Rate (%)"].fillna(0).tolist()
    coc = df["Cash-on-Cash (%)"].fillna(0).tolist()

    metrics_chart = {
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["Cap Rate (%)", "Cash-on-Cash (%)"]},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": {"type": "category", "data": zips},
        "yAxis": {"type": "value", "name": "%"},
        "series": [
            {
                "name": "Cap Rate (%)",
                "type": "bar",
                "data": cap_rates,
                "itemStyle": {"color": "#FAC858"},
            },
            {
                "name": "Cash-on-Cash (%)",
                "type": "bar",
                "data": coc,
                "itemStyle": {"color": "#73C0DE"},
            },
        ],
    }
    st_echarts(options=metrics_chart, height="300px")

st.divider()

# ---------------------------------------------------------------------------
# Investment Rating summary
# ---------------------------------------------------------------------------
_rc1, _rc2 = st.columns([8, 1])
_rc1.subheader("Investment Ratings")
with _rc2.popover("ℹ️"):
    st.markdown(
        "**Investment Ratings**\n\n"
        "A summary rating and gross yield for each zip code.\n\n"
        "**Investment Rating** — qualitative label derived from cash flow:\n"
        "- ✅ Positive Cash Flow — rent covers all costs\n"
        "- ⚠️ Negative Cash Flow — out-of-pocket monthly after financing\n"
        "- Other tiers may appear based on cap rate thresholds\n\n"
        "**Gross Yield (%)**\n"
        "Pre-expense rental income relative to property value. Higher = more raw income per dollar invested.\n"
        "Formula: `Annual Rent ÷ Property Value × 100`\n\n"
        "**Source:** Derived from estimated rent and value · Redfin MLS"
    )
rating_cols = st.columns(len(df))
for col, row in zip(rating_cols, results):
    col.metric(
        label=f"Zip {row['Zip Code']}",
        value=row["Investment Rating"],
        delta=f"Yield {row['Gross Yield (%)']:.1f}%" if row["Gross Yield (%)"] else None,
    )

st.divider()

# ---------------------------------------------------------------------------
# Data table + CSV export
# ---------------------------------------------------------------------------
st.subheader("Full Results")
st.dataframe(df, use_container_width=True, hide_index=True)

csv_buffer = io.StringIO()
df.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download CSV",
    data=csv_buffer.getvalue(),
    file_name=f"real_estate_analysis_{bedrooms}bd_{bathrooms}ba_{sqft}sqft.csv",
    mime="text/csv",
)
