import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import text
from io import BytesIO
from db_connection import engine
from queries import *
from logger_config import logger

st.set_page_config(page_title="CRM KPI Dashboard", layout="wide")

# --- Load data from DB ---
@st.cache_data
def load_dashboard_data():
    try:
        total_leads = pd.read_sql(TOTAL_LEADS, engine).iloc[0, 0]
        won_leads = pd.read_sql(WON_LEADS, engine).iloc[0, 0]
        revenue_df = pd.read_sql(REVENUE, engine)
        stage_df = pd.read_sql(PIPELINE_STAGE, engine)
        monthly_rev_df = pd.read_sql(MONTHLY_REVENUE, engine)

        # ✅ Remove duplicates (group by lead_id and sum)
        if "lead_id" in revenue_df.columns:
            revenue_df = revenue_df.groupby("lead_id", as_index=False).sum(numeric_only=True)

        total_revenue = revenue_df["amount_total"].sum() if not revenue_df.empty else 0
        avg_order_value = revenue_df["amount_total"].mean() if not revenue_df.empty else 0
        conversion_rate = round((won_leads / total_leads) * 100, 2) if total_leads else 0

        return {
            "total_leads": total_leads,
            "won_leads": won_leads,
            "conversion_rate": conversion_rate,
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "stage_df": stage_df,
            "monthly_rev_df": monthly_rev_df
        }
    except Exception as e:
        logger.exception("Dashboard data load failed: %s", e)
        st.error("❌ Could not load dashboard data.")
        return None


data = load_dashboard_data()
if not data:
    st.stop()

# --- KPI Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Leads", f"{data['total_leads']:,}")
col2.metric("Conversion Rate", f"{data['conversion_rate']}%")
col3.metric("Total Revenue", f"₹ {data['total_revenue']:,.2f}")
col4.metric("Avg Order Value", f"₹ {data['avg_order_value']:,.2f}")

st.markdown("---")

# --- Charts ---
col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Pipeline by Stage")
    st.bar_chart(data["stage_df"].set_index("stage")["cnt"])

with col2:
    st.subheader("💰 Monthly Revenue Trend")
    st.line_chart(data["monthly_rev_df"].set_index("month")["total"])

st.markdown("---")
st.subheader("📄 CRM Detailed Report")

# --- Load detailed CRM data ---
@st.cache_data
def load_crm_report():
    query = text("""
        SELECT l.id AS lead_id, l.name AS lead_name, u.login AS sales_person,
               s.name AS stage, COALESCE(so.amount_total,0) AS revenue
        FROM crm_lead l
        LEFT JOIN res_users u ON l.user_id = u.id
        LEFT JOIN crm_stage s ON l.stage_id = s.id
        LEFT JOIN sale_order so ON so.opportunity_id = l.id
    """)
    df = pd.read_sql(query, engine)
    if "lead_id" in df.columns:
        df = df.groupby("lead_id", as_index=False).agg({
            "lead_name": "first",
            "sales_person": "first",
            "stage": "first",
            "revenue": "sum"
        })
    # ✅ Capitalize all column names
    df.columns = [col.upper() for col in df.columns]
    return df


df = load_crm_report()
st.dataframe(df, use_container_width=True)

# --- Excel Export ---
def export_to_excel(df, data):
    """Generate Excel file with summary sheet using pandas only."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary Sheet
        summary = pd.DataFrame({
            "Metric": ["Total Leads", "Conversion Rate", "Total Revenue", "Avg Order Value"],
            "Value": [
                data['total_leads'],
                f"{data['conversion_rate']}%",
                f"₹ {data['total_revenue']:,.2f}",
                f"₹ {data['avg_order_value']:,.2f}"
            ]
        })
        summary.to_excel(writer, sheet_name="Summary", index=False)

        # Detailed Data Sheet
        df.to_excel(writer, sheet_name="CRM Report", index=False)
    return output.getvalue()


# --- Download Buttons ---
col_a, col_b = st.columns(2)

with col_a:
    st.download_button(
        "📥 Download Excel",
        data=export_to_excel(df, data),
        file_name="crm_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


