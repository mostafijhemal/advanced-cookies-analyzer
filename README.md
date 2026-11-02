<div align="center">

# 🍪 Advanced Cookies Analyzer

<p align="center">
  <b>A comprehensive, automated web-based tool and security scanner for scraping, inspecting, and analyzing browser cookies.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/Selenium-WebDriver-43B02A?style=flat-square&logo=selenium&logoColor=white" alt="Selenium">
  <img src="https://img.shields.io/badge/Security-Audit-orange?style=flat-square" alt="Security">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License">
</p>

</div>

<br>

<details>
  <summary><b>✨ Table of Contents</b></summary>
  <br>
  <ul>
    <li><a href="#-about-the-project">About the Project</a></li>
    <li><a href="#-key-features--modules">Key Features & Modules</a></li>
    <li><a href="#-technology-stack">Technology Stack</a></li>
    <li><a href="#-installation--setup">Installation & Setup</a></li>
    <li><a href="#-usage-guide">Usage Guide</a></li>
    <li><a href="#-contributing--authors">Contributing & Authors</a></li>
  </ul>
</details>

---

## 🚀 About the Project

**Advanced Cookies Analyzer** is designed to audit, extract, and analyze HTTP cookies across web targets. In modern web development and cybersecurity, tracking cookies, insecure flags, and third-party intrusions pose severe privacy and compliance risks. This tool automates the extraction and categorization of cookies, checks security constraints (such as `Secure`, `HttpOnly`, and `SameSite` configurations), and helps evaluate web security posture efficiently.

---

## 🛠️ Key Features & Modules

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>1. Automated Cookie Scraper</h3>
      <ul>
        <li><b>Dynamic Extraction:</b> Leverages automated browser drivers to capture runtime cookies.</li>
        <li><b>Batch Target Processing:</b> Reads URLs directly from configuration and text files.</li>
      </ul>
    </td>
    <td width="50%" valign="top">
      <h3>2. Security & Compliance Analysis</h3>
      <ul>
        <li><b>Flag Inspection:</b> Identifies missing security attributes like <code>HttpOnly</code> and <code>Secure</code>.</li>
        <li><b>Tracker Detection:</b> Cross-references discovered cookies against known tracking lists.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top" colspan="2">
      <h3>3. Structured Reporting</h3>
      <ul>
        <li><b>Database Export:</b> Compiles scraped cookie data into structured spreadsheet formats (`.xlsx` / CSV).</li>
        <li><b>TLS/Security Verification:</b> Inspects associated transport layer security configurations.</li>
      </ul>
    </td>
  </tr>
</table>

---

## 🧰 Technology Stack

* **Language:** Python
* **Automation & Scraping:** Selenium WebDriver, Requests
* **Data Processing:** Pandas, OpenPyXL
* **Reporting & CLI:** PrettyTable

---

## ⚙️ Installation & Setup

Follow these steps to set up and run the analyzer locally:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/mostafijhemal/advanced-cookies-analyzer.git
   cd advanced-cookies-analyzer
   ```

2. **Install Dependencies:**
   Ensure you have Python installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Target URLs:**
   Add your target domains or URLs into the designated input text file (e.g., `URLS.txt`).

---

## 🚀 Usage Guide

Run the primary cookie scraping and analysis script:
```bash
python cookie-scraper.py
```

* **Data Output:** Scraped cookie records and security metrics will be compiled and saved into the output database spreadsheet (`cookie-db.xlsx`).

---

## 👥 Authors & Contributors

<div align="center">

| Name | Role / Profile |
| :--- | :--- |
| **Md. Mostafijur Rahman** | Author & Maintainer — [GitHub Profile](https://github.com/mostafijhemal) |

<p><b>Department of Computer Science and Engineering</b><br>
JahangirNagar University, Dhaka, Bangladesh</p>

<p><b>Supervisor: Md. Rafsan Jani</b> (Associate Professor, Department of CSE)</p>

</div>
