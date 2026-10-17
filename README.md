# 🌿 Verdant | Cannabis Compliance CRM & Automation Platform

> An executive, full-stack CRM and compliance automation platform built for Cannabis Compliance Specialists, Consultants, and Dispensary Operators.

![Python](https://img.shields.io/badge/Python-3.11+-10B981?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat&logo=sqlite&logoColor=white)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF_Generator-059669?style=flat)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat)

---

## 🚀 Key Highlights & Capabilities

- **🎯 Executive Dashboard**: Real-time KPI hero cards (Leads, Outreach Dispatched, Response Rate, Calls Booked, Closed Revenue in USD & PKR), animated Chart.js pipeline funnel, and 90-day revenue trajectory curve.
- **🔍 Automated Lead Generator**: State registry extraction engine simulating high-fidelity dispensary lookups across Colorado (MED), California (DCC), Oregon (OLCC), Michigan (CRA), Washington (LCB), and Illinois (IDFPR) with instant CSV/JSON exports.
- **📧 Multi-Channel Outreach Automation**: Pre-configured, high-conversion pitch scripts (*LinkedIn Connect*, *72-Hour SOP Pitch*, *Cold Audit Email*, *Day-7 Follow-up*, *Closing Offer*) with dynamic merge tags (`{name}`, `{business_name}`, `{city}`, `{license_number}`, `{calendly_link}`) and simulated human-like delay intervals.
- **📞 Visual Sales Kanban Board**: 6-stage deal pipeline (`New Lead` ➔ `Contacted` ➔ `Responded` ➔ `Call Booked` ➔ `Proposal Sent` ➔ `Closed Won`) with HTML5 drag-and-drop, deal volume calculation, and celebration confetti.
- **📄 AI Standard Operating Procedure (SOP) Generator**: Built-in ReportLab document engine generating official, audit-ready compliance SOP PDFs with running headers, footers, licensing badges, and executive sign-off tables.
- **⚙️ Agency Settings & Data Controls**: Custom agency branding, Calendly strategy links, and local SQLite database backup/reset utilities.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11, [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/)
- **Database**: Local persistent SQLite (`cannabis_crm.db`) with schema migrations and automatic demo seeding
- **PDF Generation**: [ReportLab](https://www.reportlab.com/) vector document compiler
- **Frontend**: Vanilla ES6 JavaScript, HTML5 semantic structure, Chart.js 4.4, Canvas Confetti
- **Styling**: Curated Emerald / Slate dark glassmorphism design system (`frontend/css/style.css`) with Google Fonts (*Plus Jakarta Sans*, *Outfit*, *JetBrains Mono*)

---

## 📦 Project Structure

```
cannabis-crm-system/
├── backend/
│   ├── api.py              # FastAPI REST router & endpoint logic
│   ├── database.py         # SQLite persistence, schema, seed data & CRUD
│   └── pdf_generator.py    # ReportLab certified compliance SOP PDF compiler
├── frontend/
│   ├── css/
│   │   └── style.css       # Emerald glassmorphism responsive design system
│   ├── js/
│   │   ├── app.js          # App state, routing, modals & toast notifications
│   │   ├── dashboard.js    # KPIs, Chart.js visual graphs & activity stream
│   │   ├── leads.js        # Lead crawler, table filters & CSV/JSON export
│   │   ├── outreach.js     # Templates, variable merge & batch dispatcher
│   │   ├── pipeline.js     # Drag-and-drop Kanban sales board
│   │   ├── documents.js    # SOP generator & binary PDF download controller
│   │   └── settings.js     # Agency branding & database operations
│   ├── favicon.svg         # Emerald cannabis leaf vector favicon
│   └── index.html          # Single-page application root
├── generated_docs/         # Output directory for generated SOP PDF manuals
├── run.py                  # One-click startup launcher with auto-port discovery
├── server.py               # Standalone FastAPI server entry point
├── main.py                 # Streamlit alternative interface
├── lead_scraper.py         # Selenium dispensary scraper utility
├── linkedIn_bot.py         # Selenium automated LinkedIn outreach bot
├── requirements.txt        # Complete Python dependencies
└── README.md               # Documentation
```

---

## ⚡ Quick Start Guide

### 1. Clone the repository
```bash
git clone <your-repository-url>
cd cannabis-crm-system
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the application
```bash
python run.py
```

The launcher will automatically verify dependencies, initialize the local SQLite database with pre-seeded dispensary prospects, find an available port, launch the high-performance server, and open your web browser at:
- **Application Dashboard**: `http://127.0.0.1:8000`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

---

## 📜 License
This project is licensed under the MIT License.
