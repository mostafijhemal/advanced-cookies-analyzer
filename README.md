🍪 Advanced Website Cookies Analyzer

An enterprise-grade, microservices-based web application designed to automatically scan, analyze, and audit website cookies. It serves as a comprehensive Cybersecurity, Privacy (GDPR/CCPA), and Data Exfiltration Auditing Tool.

Built with a Data-as-a-Service (DaaS) architecture, it includes a centralized interactive dashboard, a standalone REST API, and a dynamic background scheduler.

🚀 Key Features

🕵️ Intelligent Cookie Scraping: Uses Headless Selenium with Fake UserAgents to bypass bot detection and collect cookies securely. Supports single URL or Bulk Uploads (CSV/Excel).

🤖 AI-Powered Purpose Prediction: Automatically categorizes cookies (e.g., Analytics, Targeted Advertising, Essential) based on heuristic algorithms.

🛡️ Automated Security & GDPR Audit: * Session Hijacking Alert: Flags essential cookies missing Secure or HttpOnly flags.

Consent Violation: Detects marketing trackers injected without user consent.

💾 Payload & Data Exfiltration Analysis: Flags unusually large cookies (>1 KB) that might contain entire user profiles or tracking tokens.

🕸️ Interactive Network Graph: Visualizes cross-site tracking relationships between domains and third-party trackers using dynamic clustering (pyvis & networkx).

📊 Date-to-Date Comparison & Anomaly Detection: Compares historical scans to detect new trackers added or removed over time.

🗑️ Easy Data Management: Built-in "Clear Historical Data" functionality to reset the database with a single click for fresh auditing and testing environments.

📁 Professional Export: Generates multi-sheet Excel raw data files and Executive PDF Reports for management review.

🏗️ System Architecture (Microservices)

This project is decoupled into independent microservices for maximum scalability:

Frontend UI (app.py): An intuitive Streamlit dashboard for visual analytics and system configuration.

API Server (api.py): A FastAPI backend offering RESTful endpoints, allowing third-party developers to integrate the scanning engine into their own apps.

Dynamic Scheduler (scheduler.py): A background worker that listens for UI commands and runs automated bulk audits (Minutes, Hours, Daily, Weekly).

Central Orchestrator (run_all.py): A master script that spins up the UI, API, and Scheduler simultaneously with a single command.

🎯 Target Audience & Use Cases

Cybersecurity Analysts & Pen Testers: To identify session hijacking vulnerabilities and unusual data exfiltration payloads.

Data Privacy Officers (DPOs): To automate GDPR/CCPA compliance audits and generate executive PDF reports for management.

Software Developers: To utilize the REST API (api.py) as a plug-and-play microservice in their own cybersecurity products.

Digital Marketing & SEO Agencies: To reverse-engineer competitor websites and analyze their third-party advertising stacks.

⚙️ Installation & Setup

Prerequisites

Python 3.9 or higher

Chrome Browser (for Selenium WebDriver)

wkhtmltopdf (Required for PDF generation. Windows users must download and add it to their system PATH).

Step-by-Step Guide

Clone the repository:

git clone [https://github.com/yourusername/advanced-cookies-analyzer.git](https://github.com/yourusername/advanced-cookies-analyzer.git)
cd advanced-cookies-analyzer


Create and activate a virtual environment:

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate


Install the required dependencies:

pip install -r requirements.txt
pip install fastapi uvicorn pydantic schedule


Run the Complete System (Master Script):

python run_all.py


This single command will start the API on port 8000, the background Scheduler, and open the Streamlit UI on port 8501.

🌐 API Usage Example (DaaS)

Once the system is running, the API interactive documentation is available at: http://127.0.0.1:8000/docs

Trigger a Scan via Python:

import requests

api_url = "[http://127.0.0.1:8000/api/v1/scan](http://127.0.0.1:8000/api/v1/scan)"
payload = {"url": "[https://example.com](https://example.com)"}

response = requests.post(api_url, json=payload)
print(response.json())


📂 Project Structure

├── app.py                  # Main Streamlit User Interface
├── api.py                  # FastAPI Backend Server
├── scheduler.py            # Dynamic Background Task Runner
├── run_all.py              # Central Orchestrator Script
├── cookie_collector.py     # Selenium Headless Scraping Engine
├── db_handler.py           # SQLite Database Operations
├── requirements.txt        # Python Dependencies
├── scheduler_config.json   # Auto-generated config for Scheduler
└── output/                 # Directory for DB, HTML Graphs, and PDFs


⚠️ Disclaimer

This tool is developed for academic and ethical auditing purposes only. Users must ensure they have permission to scan and audit the target websites. The developer is not responsible for any misuse of this application.