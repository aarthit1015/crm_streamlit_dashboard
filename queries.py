from sqlalchemy import text

from sqlalchemy import text

TOTAL_LEADS = text("SELECT COUNT(*) FROM crm_lead")
WON_LEADS = text("SELECT COUNT(*) FROM crm_lead WHERE stage_id IN (SELECT id FROM crm_stage WHERE name='Won')")
REVENUE = text("SELECT id as lead_id, amount_total FROM sale_order WHERE state='sale'")
PIPELINE_STAGE = text("""
    SELECT s.name AS stage, COUNT(l.id) AS cnt
    FROM crm_lead l
    JOIN crm_stage s ON l.stage_id = s.id
    GROUP BY s.name ORDER BY cnt DESC
""")
MONTHLY_REVENUE = text("""
    SELECT TO_CHAR(date_order, 'YYYY-MM') AS month, SUM(amount_total) AS total
    FROM sale_order
    WHERE state='sale'
    GROUP BY 1 ORDER BY 1
""")

# Report query (used for CSV, Excel, PDF)
REPORT_BASE = text("""
    SELECT l.id AS lead_id,l.name AS lead_name,u.login AS sales_person,
           s.name AS stage, COALESCE(so.amount_total,0) AS revenue
    FROM crm_lead l
    LEFT JOIN res_users u ON l.user_id = u.id
    LEFT JOIN crm_stage s ON l.stage_id = s.id
    LEFT JOIN sale_order so ON so.opportunity_id = l.id
""")
