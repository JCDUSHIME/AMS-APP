import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- Data Structures (In-memory storage for demo) ---
# Initialize session state for persistent data during a user session
if 'audit_engagements' not in st.session_state:
    st.session_state.audit_engagements = [] # List of dictionaries for audit engagements

if 'audit_findings' not in st.session_state:
    st.session_state.audit_findings = [] # List of dictionaries for audit findings

if 'corrective_actions' not in st.session_state:
    st.session_state.corrective_actions = [] # List of dictionaries for corrective actions

# --- Helper Functions ---
def generate_id(prefix, current_list):
    """Generates a unique ID based on existing items."""
    if not current_list:
        return f"{prefix}001"
    last_id = max([int(item['ID'][len(prefix):]) for item in current_list])
    return f"{prefix}{str(last_id + 1).zfill(3)}"

def add_audit_engagement(title, department, audit_type, auditors, auditees, start_date, end_date, audit_report_name=None, audit_report_data=None):
    engagement_id = generate_id("AE", st.session_state.audit_engagements)
    st.session_state.audit_engagements.append({
        "ID": engagement_id,
        "Title": title,
        "Department": department,
        "Audit Type": audit_type,
        "Auditor(s)": auditors,
        "Auditee(s)": auditees,
        "Start Date": start_date,
        "End Date": end_date,
        "Status": "Draft",
        "Audit Report Name": audit_report_name,
        "Audit Report Data": audit_report_data
    })
    st.success(f"Audit Engagement '{title}' created with ID: {engagement_id}")

def add_audit_finding(audit_engagement_id, category, description, risk_level, root_cause, recommendation, evidence_name=None, evidence_data=None):
    finding_id = generate_id("F", st.session_state.audit_findings)
    st.session_state.audit_findings.append({
        "ID": finding_id,
        "Audit Engagement ID": audit_engagement_id,
        "Category": category,
        "Description": description,
        "Evidence Name": evidence_name,
        "Evidence Data": evidence_data,
        "Risk Level": risk_level,
        "Root Cause": root_cause,
        "Recommendation": recommendation,
        "Status": "Open"
    })
    st.success(f"Audit Finding '{finding_id}' added to Engagement {audit_engagement_id}")
    return finding_id # Return the ID to link with corrective action

def add_corrective_action(finding_id, responsible_person, action_description, due_date, follow_up_evidence_name=None, follow_up_evidence_data=None):
    action_id = generate_id("CA", st.session_state.corrective_actions)
    st.session_state.corrective_actions.append({
        "ID": action_id,
        "Finding ID": finding_id,
        "Responsible Person": responsible_person,
        "Action Description": action_description,
        "Due Date": due_date,
        "Status": "Pending",
        "Follow-Up Evidence Name": follow_up_evidence_name,
        "Follow-Up Evidence Data": follow_up_evidence_data
    })
    st.success(f"Corrective Action '{action_id}' added for Finding {finding_id}")

# --- Streamlit UI ---
st.set_page_config(layout="wide", page_title="Audit Management System Demo")

st.title("🛡️ Internal Audit Management System Demo")
st.markdown("---")

# Navigation
menu = ["Dashboard", "Audit Engagements", "Audit Findings", "Corrective Actions"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Dashboard":
    st.subheader("Audit Overview Dashboard")

    # KPIs
    col1, col2, col3 = st.columns(3)

    with col1:
        total_audits = len(st.session_state.audit_engagements)
        completed_audits = sum(1 for ae in st.session_state.audit_engagements if ae['Status'] == 'Completed')
        st.metric(label="Total Audits", value=total_audits)
        st.metric(label="Audits Completed", value=completed_audits)

    with col2:
        total_findings = len(st.session_state.audit_findings)
        closed_findings = sum(1 for f in st.session_state.audit_findings if f['Status'] == 'Closed')
        if total_findings > 0:
            percent_closed = (closed_findings / total_findings) * 100
        else:
            percent_closed = 0
        st.metric(label="Total Findings", value=total_findings)
        st.metric(label="% Findings Closed", value=f"{percent_closed:.1f}%")

    with col3:
        overdue_actions = sum(1 for ca in st.session_state.corrective_actions if ca['Status'] not in ['Verified', 'Closed'] and ca['Due Date'] < datetime.now().date())
        st.metric(label="Overdue Corrective Actions", value=overdue_actions)

    st.markdown("---")
    st.subheader("Recent Activities")

    # Display recent engagements
    if st.session_state.audit_engagements:
        st.write("#### Latest Audit Engagements")
        df_engagements = pd.DataFrame(st.session_state.audit_engagements)
        st.dataframe(df_engagements.tail(5).set_index('ID'))
    else:
        st.info("No audit engagements created yet.")

    # Display recent findings
    if st.session_state.audit_findings:
        st.write("#### Latest Audit Findings")
        df_findings = pd.DataFrame(st.session_state.audit_findings)
        st.dataframe(df_findings.tail(5).set_index('ID'))
    else:
        st.info("No audit findings created yet.")


elif choice == "Audit Engagements":
    st.subheader("Manage Audit Engagements")

    tab1, tab2 = st.tabs(["Create New Engagement", "View All Engagements"])

    with tab1:
        st.write("### New Audit Engagement")
        with st.form("new_audit_engagement_form", clear_on_submit=True):
            ae_title = st.text_input("Engagement Title", placeholder="e.g., Annual IT Security Audit")
            ae_department = st.text_input("Department", placeholder="e.g., Finance, IT, Operations")
            ae_audit_type = st.selectbox("Audit Type", ["Compliance", "IT", "Operational", "Financial", "Other"])
            ae_auditors = st.text_input("Auditor(s) (comma-separated)", placeholder="e.g., John Doe, Jane Smith")
            ae_auditees = st.text_input("Auditee(s) (comma-separated)", placeholder="e.g., Emily White, Robert Green")
            ae_start_date = st.date_input("Start Date", datetime.now().date())
            ae_end_date = st.date_input("End Date", datetime.now().date() + timedelta(days=30))
            ae_report_file = st.file_uploader("Upload Final Audit Report (Optional)", type=["pdf", "docx", "xlsx"])

            submitted_ae = st.form_submit_button("Create Audit Engagement")
            if submitted_ae:
                report_name = ae_report_file.name if ae_report_file else None
                report_data = ae_report_file.getvalue() if ae_report_file else None
                if ae_title and ae_department and ae_auditors:
                    add_audit_engagement(ae_title, ae_department, ae_audit_type, ae_auditors, ae_auditees,
                                         ae_start_date, ae_end_date, report_name, report_data)
                else:
                    st.error("Please fill in all required fields (Title, Department, Auditors).")

    with tab2:
        st.write("### All Audit Engagements")
        if st.session_state.audit_engagements:
            df_engagements = pd.DataFrame(st.session_state.audit_engagements)
            df_engagements_display = df_engagements.drop(columns=['Audit Report Data'], errors='ignore') # Don't display raw file data
            st.dataframe(df_engagements_display.set_index('ID'))

            st.write("#### Update Engagement Status")
            engagement_ids = [ae['ID'] for ae in st.session_state.audit_engagements]
            if engagement_ids:
                selected_ae_id = st.selectbox("Select Engagement to Update", engagement_ids, key="update_ae_select")
                new_status = st.selectbox("New Status", ["Draft", "In Progress", "Completed", "Cancelled"], key="new_ae_status")
                if st.button("Update Engagement Status", key="update_ae_button"):
                    for ae in st.session_state.audit_engagements:
                        if ae['ID'] == selected_ae_id:
                            ae['Status'] = new_status
                            st.success(f"Status of Engagement {selected_ae_id} updated to {new_status}")
                            st.rerun() # Rerun to refresh the dataframe
                            break
            else:
                st.info("No engagements to update.")
        else:
            st.info("No audit engagements created yet.")

elif choice == "Audit Findings":
    st.subheader("Manage Audit Findings")

    tab1, tab2 = st.tabs(["Create New Finding", "View All Findings"])

    with tab1:
        st.write("### New Audit Finding")
        if not st.session_state.audit_engagements:
            st.warning("Please create an Audit Engagement first before adding findings.")
        else:
            with st.form("new_audit_finding_form", clear_on_submit=True):
                available_engagements = {ae['ID']: f"{ae['ID']} - {ae['Title']}" for ae in st.session_state.audit_engagements}
                selected_engagement_display = st.selectbox("Link to Audit Engagement", list(available_engagements.values()))
                selected_engagement_id = [k for k, v in available_engagements.items() if v == selected_engagement_display][0] if selected_engagement_display else None

                find_category = st.selectbox("Category", ["Major", "Minor", "Observation", "OFI"])
                find_description = st.text_area("Finding Details", placeholder="Detailed description of the finding.")
                find_evidence_file = st.file_uploader("Upload Supporting Evidence (Optional)", type=["pdf", "jpg", "png", "jpeg"])
                find_risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])
                find_root_cause = st.text_area("Root Cause", placeholder="What led to this finding?")
                find_recommendation = st.text_area("Recommendation", placeholder="Suggested corrective action.")

                submitted_find = st.form_submit_button("Create Audit Finding")
                if submitted_find:
                    evidence_name = find_evidence_file.name if find_evidence_file else None
                    evidence_data = find_evidence_file.getvalue() if find_evidence_file else None
                    if selected_engagement_id and find_description and find_risk_level:
                        add_audit_finding(selected_engagement_id, find_category, find_description, find_risk_level,
                                          find_root_cause, find_recommendation, evidence_name, evidence_data)
                    else:
                        st.error("Please fill in all required fields (Engagement, Description, Risk Level).")

    with tab2:
        st.write("### All Audit Findings")
        if st.session_state.audit_findings:
            df_findings = pd.DataFrame(st.session_state.audit_findings)
            df_findings_display = df_findings.drop(columns=['Evidence Data'], errors='ignore')
            st.dataframe(df_findings_display.set_index('ID'))

            st.write("#### Update Finding Status")
            finding_ids = [f['ID'] for f in st.session_state.audit_findings]
            if finding_ids:
                selected_finding_id = st.selectbox("Select Finding to Update", finding_ids, key="update_find_select")
                new_finding_status = st.selectbox("New Status", ["Open", "Closed"], key="new_find_status")
                if st.button("Update Finding Status", key="update_find_button"):
                    for f in st.session_state.audit_findings:
                        if f['ID'] == selected_finding_id:
                            f['Status'] = new_finding_status
                            st.success(f"Status of Finding {selected_finding_id} updated to {new_finding_status}")
                            st.rerun()
                            break
            else:
                st.info("No findings to update.")
        else:
            st.info("No audit findings created yet.")

elif choice == "Corrective Actions":
    st.subheader("Manage Corrective Actions")

    tab1, tab2 = st.tabs(["Create New Corrective Action", "View All Corrective Actions"])

    with tab1:
        st.write("### New Corrective Action")
        if not st.session_state.audit_findings:
            st.warning("Please create an Audit Finding first before adding corrective actions.")
        else:
            with st.form("new_corrective_action_form", clear_on_submit=True):
                available_findings = {f['ID']: f"{f['ID']} - {f['Description']}" for f in st.session_state.audit_findings}
                selected_finding_display = st.selectbox("Link to Audit Finding", list(available_findings.values()))
                selected_finding_id = [k for k, v in available_findings.items() if v == selected_finding_display][0] if selected_finding_display else None

                ca_responsible_person = st.text_input("Responsible Person")
                ca_description = st.text_area("Action Description", placeholder="Specific steps to correct/prevent the finding.")
                ca_due_date = st.date_input("Due Date", datetime.now().date() + timedelta(days=14))
                ca_follow_up_file = st.file_uploader("Upload Follow-Up Evidence (Optional)", type=["pdf", "jpg", "png", "jpeg"])

                submitted_ca = st.form_submit_button("Create Corrective Action")
                if submitted_ca:
                    follow_up_name = ca_follow_up_file.name if ca_follow_up_file else None
                    follow_up_data = ca_follow_up_file.getvalue() if ca_follow_up_file else None
                    if selected_finding_id and ca_responsible_person and ca_description and ca_due_date:
                        add_corrective_action(selected_finding_id, ca_responsible_person, ca_description,
                                              ca_due_date, follow_up_name, follow_up_data)
                    else:
                        st.error("Please fill in all required fields (Finding, Responsible Person, Description, Due Date).")

    with tab2:
        st.write("### All Corrective Actions")
        if st.session_state.corrective_actions:
            df_actions = pd.DataFrame(st.session_state.corrective_actions)
            df_actions_display = df_actions.drop(columns=['Follow-Up Evidence Data'], errors='ignore')
            st.dataframe(df_actions_display.set_index('ID'))

            st.write("#### Update Corrective Action Status")
            action_ids = [ca['ID'] for ca in st.session_state.corrective_actions]
            if action_ids:
                selected_ca_id = st.selectbox("Select Action to Update", action_ids, key="update_ca_select")
                new_ca_status = st.selectbox("New Status", ["Pending", "In Progress", "Verified", "Closed"], key="new_ca_status")
                if st.button("Update Corrective Action Status", key="update_ca_button"):
                    for ca in st.session_state.corrective_actions:
                        if ca['ID'] == selected_ca_id:
                            ca['Status'] = new_ca_status
                            st.success(f"Status of Action {selected_ca_id} updated to {new_ca_status}")
                            st.rerun()
                            break
            else:
                st.info("No corrective actions to update.")
        else:
            st.info("No corrective actions created yet.")