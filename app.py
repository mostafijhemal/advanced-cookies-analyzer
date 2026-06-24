import streamlit as st
from cookie_collector import get_cookies_from_site
from db_handler import init_db, insert_cookie, fetch_all_cookies, clear_database
import os
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
import base64
from st_aggrid import AgGrid, GridOptionsBuilder
import pdfkit
import concurrent.futures
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components

# Ensure DB exists
os.makedirs("output", exist_ok=True)
conn = init_db("output/cookies.db")

st.set_page_config(page_title="Advanced Cookies Analyzer", page_icon="🍪", layout="wide")
st.title("🍪 Advanced Cookies Analyzer Dashboard")

page = st.sidebar.radio("Navigation", ["📥 Input Websites", "📊 Analytics Dashboard"])
# --- System Settings & API Panel (Sidebar) ---
st.sidebar.markdown("---")
st.sidebar.header("⚙️ System Settings")

# 1. API Dashboard Button
st.sidebar.link_button("🌐 Open API Dashboard", "http://127.0.0.1:8000/docs", use_container_width=True)

# 2. Dynamic Scheduler Control
st.sidebar.subheader("⏱️ Scheduler Config")
import json
import os

# Load current config to show in UI
default_unit, default_val, default_day = "Minutes", 1, "Monday"
if os.path.exists("scheduler_config.json"):
    try:
        with open("scheduler_config.json", "r") as f:
            conf = json.load(f)
            default_unit = conf.get("unit", "minutes").capitalize()
            default_val = conf.get("interval", 1)
            default_day = conf.get("day", "monday").capitalize()
    except: pass

sched_unit = st.sidebar.selectbox("Run Every:", ["Minutes", "Hours", "Daily", "Weekly"], index=["Minutes", "Hours", "Daily", "Weekly"].index(default_unit))
sched_val = 1
sched_time = "00:00"
sched_day = "Monday"

if sched_unit in ["Minutes", "Hours"]:
    sched_val = st.sidebar.number_input("Interval value:", min_value=1, value=default_val)
elif sched_unit == "Daily":
    sched_time = st.sidebar.time_input("Time of day:").strftime("%H:%M")
elif sched_unit == "Weekly":
    sched_day = st.sidebar.selectbox("Day of the week:", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(default_day))
    sched_time = st.sidebar.time_input("Time of day:").strftime("%H:%M")

if st.sidebar.button("💾 Save Settings"):
    config = {"unit": sched_unit.lower(), "interval": sched_val, "time": sched_time, "day": sched_day.lower()}
    with open("scheduler_config.json", "w") as f:
        json.dump(config, f)
    st.sidebar.success(f"✅ Saved! Scheduler set to {sched_unit}.")

# --- 3. Database Management ---
st.sidebar.markdown("---")
st.sidebar.subheader("🗑️ Data Management")
if st.sidebar.button("⚠️ Clear All Historical Data", use_container_width=True, help="This will delete all scanned cookies permanently."):
    clear_database()
    st.sidebar.success("✅ Database cleared successfully! Refreshing...")
    st.rerun()

# --- Helper Function for Risk Scoring ---
def calculate_risk(row):
    if not row['ThirdParty']:
        return "Low Risk"
    elif row['ThirdParty'] and row['CookieType'] == "Persistent (> 1 Year)":
        return "High Risk"
    else:
        return "Medium Risk"

# --- Helper Function for Purpose Prediction ---
def predict_purpose(row):
    name = str(row['Name']).lower()
    domain = str(row['Domain']).lower()
    
    # Analytics Keywords
    if any(k in name for k in ['_ga', '_gid', 'stat']) or 'analytic' in domain:
        return "📊 Analytics & Tracking"
    # Advertising Keywords
    elif any(k in name for k in ['_fbp', 'ads', 'pixel', 'uuid']) or any(k in domain for k in ['facebook', 'doubleclick', 'ad']):
        return "🎯 Targeted Advertising"
    # Essential/Session Keywords
    elif any(k in name for k in ['session', 'csrf', 'auth', 'login', 'token']):
        return "🔒 Essential & Functional"
    else:
        return "⚙️ Uncategorized/Other"


# --- Page 1: Website Input (With Multithreading & Progress Bar) ---
if page == "📥 Input Websites":
    st.header("🔗 Enter Website URLs for Bulk Scanning")
    
    # --- NEW: Custom Data Source Support (CSV/Excel) ---
    st.markdown("#### 📂 Option 1: Upload CSV or Excel File")
    uploaded_file = st.file_uploader("Upload a file containing URLs (URLs should be in the first column)", type=["csv", "xlsx"])
    file_urls = []
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_upload = pd.read_csv(uploaded_file)
            else:
                df_upload = pd.read_excel(uploaded_file)
            
            # URL Collections from the first column
            first_col = df_upload.columns[0]
            file_urls = df_upload[first_col].dropna().astype(str).tolist()
            st.success(f"✅ Successfully extracted {len(file_urls)} URLs from the uploaded file.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.markdown("#### ✍️ Option 2: Manual Input")
    website_input = st.text_area("Type or paste Website URLs manually (one per line)", height=150, placeholder="https://example.com\nhttps://cnn.com")

    if st.button("Start Intelligent Scan"):
        manual_urls = [w.strip() for w in website_input.splitlines() if w.strip()]
        # Removes duplicate URLs from the file and manual input
        websites = list(set(file_urls + manual_urls)) 
        
        if not websites:
            st.warning("⚠️ Please enter at least one website or upload a valid CSV/Excel file.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            completed = 0
            # Using ThreadPoolExecutor for faster concurrent scanning
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {executor.submit(get_cookies_from_site, site): site for site in websites}
                
                for future in concurrent.futures.as_completed(future_to_url):
                    site = future_to_url[future]
                    try:
                        cookies = future.result()
                        for cookie in cookies:
                            insert_cookie(conn, site, cookie)
                        completed += 1
                        progress_bar.progress(completed / len(websites))
                        status_text.success(f"✅ Successfully scanned: {site} ({len(cookies)} cookies)")
                    except Exception as e:
                        completed += 1
                        progress_bar.progress(completed / len(websites))
                        status_text.error(f"❌ Failed to scan {site}: {e}")
            
            st.balloons()
            st.success("🎉 Bulk scanning completed successfully!")

# --- Page 2: Analytics & Reports ---
elif page == "📊 Analytics Dashboard":
    st.header("🧠 Advanced AI & Analytics Dashboard")
    rows = fetch_all_cookies()

    if not rows:
        st.info("No data available. Please scan some websites first.")
    else:
        df = pd.DataFrame(rows, columns=[
            "Website", "Name", "Value", "Domain", "Path", "Expiry", "Secure", "HttpOnly", "ScanDate"
        ])

        # --- Data Enrichment ---
        df['ThirdParty'] = df.apply(lambda r: str(r['Domain']).replace('.', '') not in r['Website'], axis=1)
        df['ExpiryDate'] = pd.to_datetime(df['Expiry'], unit='s', errors='coerce')
        df['ScanDate'] = pd.to_datetime(df['ScanDate'])
        df['ScanDay'] = df['ScanDate'].dt.date
        
        # Risk & Purpose Predictions
        current_time = datetime.now()
        df['CookieType'] = df['ExpiryDate'].apply(
            lambda x: "Session" if pd.isnull(x) else ("Persistent (> 1 Year)" if (x - current_time).days > 365 else "Persistent (< 1 Year)")
        )
        df['RiskLevel'] = df.apply(calculate_risk, axis=1)
        df['PredictedPurpose'] = df.apply(predict_purpose, axis=1) # New AI Predictor

        # --- Top Summary Metrics (Executive Summary) ---
        st.markdown("### 📌 Executive Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Cookies", len(df))
        col2.metric("3rd-Party Trackers", int(df['ThirdParty'].sum()))
        col3.metric("Secure Cookies", int(df['Secure'].sum()))
        col4.metric("High Risk Cookies", len(df[df['RiskLevel'] == 'High Risk']))
        col5.metric("Unique Domains", df['Domain'].nunique())
        
        st.markdown("---") 

        # --- Dashboard Tabs ---
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Purpose Prediction", 
            "📈 Trends & Comparison", 
            "🕸️ Network Graph", 
            "🛡️ GDPR & Security Audit",
            "💾 Payload Analysis"
        ])

        # TAB 1: Purpose Prediction
        with tab1:
            st.markdown("### 🤖 Cookie Purpose Prediction")
            st.write("Using heuristic algorithms to predict why each cookie was injected into the browser.")
            
            purpose_counts = df['PredictedPurpose'].value_counts().reset_index()
            purpose_counts.columns = ['Purpose', 'Count']
            fig_purpose = px.pie(purpose_counts, values='Count', names='Purpose', hole=0.3, title="Predicted Cookie Purposes")
            st.plotly_chart(fig_purpose, use_container_width=True)

        # TAB 2: Comparative Analysis & Anomaly Detection
        with tab2:
            st.markdown("### 📊 Historical Scan Trends")
            
            # Group by scan day to see trends
            daily_trend = df.groupby('ScanDay').size().reset_index(name='Total Cookies')
            fig_trend = px.line(daily_trend, x='ScanDay', y='Total Cookies', markers=True, title="Cookies Over Time")
            st.plotly_chart(fig_trend, use_container_width=True)

            # --- NEW: Date-to-Date Comparison Feature ---
            st.markdown("---")
            st.markdown("### 🗓️ Date-to-Date Deep Comparison")
            st.write("Compare how cookie and tracker behaviors have changed between two specific dates.")
            
            # Get unique dates for the dropdown
            unique_dates = df['ScanDay'].unique()
            
            if len(unique_dates) >= 2:
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    date_a = st.selectbox("Select Baseline Date (Date A)", sorted(unique_dates))
                with col_d2:
                    # Default to the most recent date
                    date_b = st.selectbox("Select Comparison Date (Date B)", sorted(unique_dates, reverse=True))
                
                if date_a and date_b:
                    # Filter data for selected dates
                    df_a = df[df['ScanDay'] == date_a]
                    df_b = df[df['ScanDay'] == date_b]
                    
                    # Calculate Metrics
                    total_a = len(df_a)
                    total_b = len(df_b)
                    diff_total = total_b - total_a
                    
                    # Tracker Analysis using Set Operations
                    trackers_a = set(df_a[df_a['ThirdParty']]['Domain'])
                    trackers_b = set(df_b[df_b['ThirdParty']]['Domain'])
                    
                    new_trackers = trackers_b - trackers_a
                    removed_trackers = trackers_a - trackers_b
                    
                    # Visualizing the Metrics
                    st.markdown("#### 📈 Comparison Overview")
                    c1, c2, c3 = st.columns(3)
                    
                    # Delta shows the difference (Up arrow = increased, Down arrow = decreased)
                    c1.metric(label=f"Total Cookies (vs Date A)", value=total_b, delta=diff_total)
                    c2.metric(label="New Trackers Added", value=len(new_trackers), delta=len(new_trackers), delta_color="inverse")
                    c3.metric(label="Trackers Removed", value=len(removed_trackers), delta=-len(removed_trackers), delta_color="normal")
                    
                    # Detailed breakdown of changes
                    if new_trackers:
                        st.error(f"⚠️ **Security Alert:** {len(new_trackers)} New Third-Party Trackers Found on Date B:\n\n" + ", ".join(new_trackers))
                    if removed_trackers:
                        st.success(f"✅ **Privacy Improved:** {len(removed_trackers)} Trackers Removed since Date A:\n\n" + ", ".join(removed_trackers))
                    
                    if not new_trackers and not removed_trackers:
                        st.info("⚖️ No changes in third-party trackers between these two dates.")
            else:
                st.info("💡 **Tip:** You need to scan websites on at least two different dates to unlock the Date-to-Date Comparison feature.")

            # --- Anomaly Detection ---
            st.markdown("---")
            st.markdown("### 🚨 Anomaly Detection Alerts")
            avg_cookies = daily_trend['Total Cookies'].mean()
            latest_scan_cookies = daily_trend['Total Cookies'].iloc[-1]
            
            if latest_scan_cookies > (avg_cookies * 1.5): # 50% spike
                st.error(f"⚠️ **Anomaly Detected:** The latest scan found {latest_scan_cookies} cookies, which is significantly higher than the historical average of {int(avg_cookies)}.")
            else:
                st.success(f"✅ **Status Normal:** Current cookie volume ({latest_scan_cookies}) is within normal historical ranges (Avg: {int(avg_cookies)}).")

        # TAB 3: Domain Clustering (Interactive Network Graph)
        with tab3:
            st.markdown("### 🕸️ Interactive Cross-Site Tracking Network")
            st.write("Visualizing how third-party trackers (Red Dots) are connected across your scanned websites (Green Stars). You can drag and zoom the nodes!")
            
            trackers_df = df[df['ThirdParty']]
            
            if not trackers_df.empty:
                # Create a Pyvis network graph
                net = Network(height="500px", width="100%", bgcolor="#0e1117", font_color="white", notebook=False)
                net.repulsion(node_distance=150, central_gravity=0.2, spring_length=100) # Physics engine
                
                websites = trackers_df['Website'].unique()
                for site in websites:
                    # Add Website node (Center)
                    net.add_node(site, label=site, title=f"Website: {site}", color="#00ff1e", size=25, shape="star")
                    
                    # Find trackers for this site
                    site_trackers = trackers_df[trackers_df['Website'] == site]['Domain'].unique()
                    for tracker in site_trackers:
                        # Add Tracker node
                        net.add_node(tracker, label=tracker, title=f"Tracker: {tracker}", color="#ff4b4b", size=15, shape="dot")
                        # Add Edge linking website and tracker
                        net.add_edge(site, tracker, color="#555555", width=1.5)
                
                # Save and display in Streamlit
                try:
                    path = "output/network_graph.html"
                    net.save_graph(path)
                    HtmlFile = open(path, 'r', encoding='utf-8')
                    source_code = HtmlFile.read() 
                    components.html(source_code, height=510)
                except Exception as e:
                    st.error(f"Could not render network graph: {e}")
            else:
                st.info("💡 Scan more websites with third-party cookies to build the network graph.")

        # TAB 4: GDPR & Security Audit
        with tab4:
            st.markdown("### 🛡️ GDPR Compliance & Security Audit")
            st.write("Automated scanning for privacy law violations and session security vulnerabilities.")

            # --- 1. Session Hijacking Risk (Security Audit) ---
            st.markdown("#### 🚨 Security Vulnerability: Session Hijacking")
            # Searching essentials cookie where no flag about Secure বা HttpOnly 
            vuln_cookies = df[(df['PredictedPurpose'] == "🔒 Essential & Functional") & 
                              ((df['Secure'] == False) | (df['HttpOnly'] == False))]
            
            if not vuln_cookies.empty:
                st.error(f"**Vulnerability Found:** {len(vuln_cookies)} essential/session cookies are missing 'Secure' or 'HttpOnly' flags. This makes them highly vulnerable to Cross-Site Scripting (XSS) and Man-in-the-Middle (MITM) attacks.")
                st.dataframe(vuln_cookies[['Website', 'Name', 'Domain', 'Secure', 'HttpOnly']], use_container_width=True)
            else:
                st.success("✅ **Security Passed:** All essential and session cookies have proper 'Secure' and 'HttpOnly' flags.")

            # --- 2. Simulated GDPR Consent Violation (Privacy Audit) ---
            st.markdown("#### ⚖️ Privacy Law: GDPR Consent Audit")
            st.write("Under GDPR/CCPA, marketing and tracking cookies cannot be set before explicit user consent. Since our scanner acts as a first-time visitor (no consent given), the following cookies represent potential legal violations.")
            
            # Third-party marketing and tracking cookies
            gdpr_violations = df[(df['ThirdParty'] == True) & 
                                 (df['PredictedPurpose'].isin(["🎯 Targeted Advertising", "📊 Analytics & Tracking"]))]
            
            if not gdpr_violations.empty:
                st.warning(f"**Potential GDPR Violation:** {len(gdpr_violations)} third-party tracking/marketing cookies were injected automatically without user consent.")
                st.dataframe(gdpr_violations[['Website', 'Name', 'Domain', 'PredictedPurpose']], use_container_width=True)
            else:
                st.success("✅ **Privacy Passed:** No unauthorized marketing or tracking cookies were detected on initial load.")

        # TAB 5: Payload Size & Data Exfiltration Analysis
        with tab5:
            st.markdown("### 💾 Cookie Payload & Data Exfiltration Analysis")
            st.write("Analyzing the size of data stored by cookies. Unusually large cookies (>1 KB) might contain entire user profiles, browsing histories, or tracking tokens.")

            # Calculate Payload Size in Bytes
            df['PayloadSizeBytes'] = df['Value'].apply(lambda x: len(str(x).encode('utf-8')) if pd.notnull(x) else 0)
            
            st.markdown("#### 📦 Top 10 Largest Cookies by Data Size")
            largest_cookies = df.nlargest(10, 'PayloadSizeBytes')[['Website', 'Name', 'Domain', 'PayloadSizeBytes', 'PredictedPurpose']]
            
            # Interactive Bar Chart for Payload Sizes
            if not largest_cookies.empty:
                fig_payload = px.bar(
                    largest_cookies, 
                    x='Name', 
                    y='PayloadSizeBytes', 
                    color='Domain', 
                    hover_data=['Website', 'PredictedPurpose'],
                    title="Largest Cookie Payloads (in Bytes)",
                    labels={'PayloadSizeBytes': 'Size in Bytes', 'Name': 'Cookie Name'}
                )
                st.plotly_chart(fig_payload, use_container_width=True)

            # Warning for Massive Cookies (Greater than 1 KB / 1024 Bytes)
            st.markdown("#### 🚨 Massive Payload Alerts")
            massive_cookies = df[df['PayloadSizeBytes'] > 1024]
            
            if not massive_cookies.empty:
                st.error(f"⚠️ **Heavy Payload Alert:** Found {len(massive_cookies)} cookies larger than 1 KB (1024 bytes). These cookies are unusually large and may be storing extensive behavioral data or encrypted user profiles.")
                st.dataframe(massive_cookies[['Website', 'Name', 'Domain', 'PayloadSizeBytes', 'PredictedPurpose']], use_container_width=True)
            else:
                st.success("✅ **Normal Payloads:** No unusually large cookies (> 1 KB) detected. Data size is within standard tracking limits.")

        # --- Advanced Data Grid ---
        st.markdown("---")
        st.markdown("### 🔍 Advanced Threat Explorer")
        gb = GridOptionsBuilder.from_dataframe(df[['Website', 'Name', 'Domain', 'PredictedPurpose', 'RiskLevel', 'CookieType']])
        gb.configure_default_column(filter=True, sortable=True)
        gb.configure_column("RiskLevel", cellStyle={'color': 'white', 'backgroundColor': '#ff4b4b'}, header_name="Risk")
        grid_options = gb.build()
        AgGrid(df, gridOptions=grid_options, fit_columns_on_grid_load=True, height=400)

# --- Advanced Export Options ---
        st.markdown("---")
        st.markdown("### 📁 Export Historical & Professional Reports")
        
        # --- NEW: Historical Data Filter ---
        st.write("🗓️ **Filter data by date range before exporting:**")
        if not df.empty:
            df['ScanDate'] = pd.to_datetime(df['ScanDate'])
            min_date = df['ScanDate'].min().date()
            max_date = df['ScanDate'].max().date()
        else:
            min_date = datetime.today().date()
            max_date = datetime.today().date()
        
        # Date Picker
        date_range = st.date_input("Select Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            # Filter Dataframe by selected dates
            export_df = df[(df['ScanDate'].dt.date >= start_date) & (df['ScanDate'].dt.date <= end_date)]
        else:
            export_df = df.copy()
            start_date, end_date = min_date, max_date
            
        st.info(f"📊 Ready to export {len(export_df)} records based on your selected date range.")
        
        if not export_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Multi-Sheet Excel Export (using export_df)
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    summary_df = pd.DataFrame({
                        "Metric": ["Total Cookies", "3rd-Party Trackers", "High Risk Cookies", "Secure Cookies"],
                        "Value": [len(export_df), int(export_df['ThirdParty'].sum()), len(export_df[export_df['RiskLevel'] == 'High Risk']), int(export_df['Secure'].sum())]
                    })
                    summary_df.to_excel(writer, sheet_name='Dashboard Summary', index=False)
                    export_df[export_df['RiskLevel'] == 'High Risk'].to_excel(writer, sheet_name='High Risk Cookies', index=False)
                    export_df.to_excel(writer, sheet_name='Raw Data', index=False)
                
                st.download_button(
                    label="📊 Download Filtered Excel Report",
                    data=excel_buffer.getvalue(),
                    file_name=f"Historical_Cookie_Report_{start_date}_to_{end_date}.xlsx",
                    mime="application/vnd.ms-excel"
                )

            with col2:
                # Automated PDF Generation (using export_df)
                if st.button("📄 Generate Executive PDF Report"):
                    with st.spinner("Generating PDF... Please wait."):
                        html_content = f"""
                        <html>
                        <head>
                            <style>
                                body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
                                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                                h2 {{ color: #e74c3c; margin-top: 30px; }}
                                .summary-box {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; font-size: 16px; }}
                                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 12px; }}
                                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                                th {{ background-color: #34495e; color: white; }}
                            </style>
                        </head>
                        <body>
                            <h1>🛡️ Historical Privacy & Security Audit Report</h1>
                            <p><b>Data Date Range:</b> {start_date} to {end_date}</p>
                            
                            <div class="summary-box">
                                <h3>Executive Summary</h3>
                                <ul>
                                    <li><b>Total Cookies Analyzed:</b> {len(export_df)}</li>
                                    <li><b>3rd-Party Trackers:</b> {int(export_df['ThirdParty'].sum())}</li>
                                    <li><b>High Risk Cookies:</b> {len(export_df[export_df['RiskLevel'] == 'High Risk'])}</li>
                                </ul>
                            </div>

                            <h2>High Risk & Vulnerable Cookies</h2>
                            {export_df[export_df['RiskLevel'] == 'High Risk'][['Website', 'Name', 'Domain', 'PredictedPurpose']].head(10).to_html(index=False) if not export_df[export_df['RiskLevel'] == 'High Risk'].empty else "<p>No High Risk cookies found.</p>"}
                            
                            <h2>Top Cross-Site Trackers</h2>
                            {export_df[export_df['ThirdParty']]['Domain'].value_counts().head(5).reset_index().rename(columns=dict(count='Total Injections', Domain='Tracker Domain')).to_html(index=False)}
                        </body>
                        </html>
                        """
                        
                        pdf_file_path = "output/Executive_Audit_Report.pdf"
                        try:
                            pdfkit.from_string(html_content, pdf_file_path)
                            with open(pdf_file_path, "rb") as f:
                                b64 = base64.b64encode(f.read()).decode("utf-8")
                                href = f'<a href="data:application/pdf;base64,{b64}" download="Historical_Audit_{start_date}_to_{end_date}.pdf">📥 Click Here to Download PDF Report</a>'
                                st.markdown(href, unsafe_allow_html=True)
                                st.success("✅ PDF generated successfully!")
                        except Exception as e:
                            st.error(f"PDF generation failed: {e}")

        st.markdown("---")
        st.info("💡 **Pro Tip:** Download the PDF for a quick executive summary and keep the Excel file for deep raw-data analysis.")