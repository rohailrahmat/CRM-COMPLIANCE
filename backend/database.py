"""
Database module for Cannabis CRM & Compliance System
SQLite persistence with pre-seeded demo records and full CRUD operations.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent.parent / "cannabis_crm.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Leads table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name TEXT NOT NULL,
        license_number TEXT,
        license_type TEXT DEFAULT 'Retail',
        owner_name TEXT,
        city TEXT,
        state TEXT,
        phone TEXT,
        email TEXT,
        linkedin TEXT,
        status TEXT DEFAULT 'new',
        deal_value INTEGER DEFAULT 997,
        notes TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # Activities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        activity_type TEXT NOT NULL,
        description TEXT NOT NULL,
        timestamp TEXT,
        FOREIGN KEY (lead_id) REFERENCES leads (id) ON DELETE CASCADE
    )
    """)

    # Settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Documents generated table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        doc_type TEXT NOT NULL,
        business_name TEXT NOT NULL,
        state TEXT,
        license_number TEXT,
        tier TEXT,
        file_path TEXT,
        created_at TEXT
    )
    """)

    conn.commit()

    # Seed initial data if empty
    cursor.execute("SELECT COUNT(*) FROM leads")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_sample_data(cursor)
        conn.commit()

    # Seed default settings if empty
    cursor.execute("SELECT COUNT(*) FROM settings")
    s_count = cursor.fetchone()[0]
    if s_count == 0:
        default_settings = {
            "specialist_name": "Compliance Specialist",
            "business_brand": "Verdant Compliance Solutions",
            "specialist_email": "compliance@verdant-ops.com",
            "specialist_phone": "+1 (720) 489-2210",
            "calendly_link": "https://calendly.com/cannabis-compliance-demo",
            "linkedin_url": "https://linkedin.com/company/verdant-compliance",
            "wise_account": "billing@verdant-ops.com",
            "auto_followup": "true",
            "followup_days": "3",
            "daily_outreach_limit": "25",
            "delay_seconds": "15"
        }
        for k, v in default_settings.items():
            cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, v))
        conn.commit()

    conn.close()

def seed_sample_data(cursor):
    now = datetime.now()
    sample_leads = [
        ("Emerald Peak Dispensary", "CO-402-00192", "Retail", "Marcus Vance", "Denver", "Colorado", "+1-303-555-0144", "marcus@emeraldpeakdispensary.com", "linkedin.com/in/marcusvance", "closed", 1497, (now - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Highland Green Co.", "CO-402-00388", "Retail", "Elena Rostova", "Boulder", "Colorado", "+1-303-555-0198", "elena@highlandgreenco.com", "linkedin.com/in/elenarostova", "call_booked", 997, (now - timedelta(days=8)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Silver State Botanicals", "CO-402-00512", "Medical & Retail", "David Kim", "Colorado Springs", "Colorado", "+1-719-555-0112", "dkim@silverstatebotanicals.com", "linkedin.com/in/davidkim-cannabis", "proposal_sent", 997, (now - timedelta(days=6)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Golden Leaf Collective", "CA-C10-0000481", "Retail", "Sarah Jenkins", "Oakland", "California", "+1-510-555-0177", "sjenkins@goldenleafcollective.com", "linkedin.com/in/sarahjenkins-ca", "responded", 997, (now - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Pacific Coast Remedies", "CA-C10-0000892", "Retail", "Mateo Morales", "San Diego", "California", "+1-619-555-0133", "mmorales@pacificcoastremedies.com", "linkedin.com/in/mateomorales", "contacted", 497, (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Redwood Wellness Dispensary", "CA-C10-0001205", "Medical", "Claire Thorne", "Eureka", "California", "+1-707-555-0165", "claire@redwoodwellness.org", "linkedin.com/in/clairethorne", "new", 997, (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Mile High CannaLab", "CO-403-00078", "Cultivation & Retail", "Travis Scott", "Aurora", "Colorado", "+1-720-555-0182", "travis@milehighcannalab.com", "linkedin.com/in/travisscott-co", "new", 1497, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Sierra Foothills Herbal", "CA-C10-0002140", "Retail", "Hannah Abbott", "Sacramento", "California", "+1-916-555-0149", "hannah@sierraherbal.com", "linkedin.com/in/hannahabbott", "closed", 997, (now - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Front Range Flora", "CO-402-00844", "Retail", "Lucas Meyer", "Fort Collins", "Colorado", "+1-970-555-0121", "lucas@frontrangeflora.com", "linkedin.com/in/lucasmeyer", "responded", 497, (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Bay Area Green Solutions", "CA-C10-0003011", "Retail & Delivery", "Alicia Zhang", "San Francisco", "California", "+1-415-555-0199", "alicia@baygreensolutions.com", "linkedin.com/in/aliciazhang-sf", "contacted", 1497, (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Cascade Valley Herbals", "OR-MED-00912", "Retail", "Gavin Reed", "Portland", "Oregon", "+1-503-555-0142", "gavin@cascadevalleyherbals.com", "linkedin.com/in/gavinreed-or", "new", 997, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Great Lakes Herbal Co.", "MI-AU-R-000412", "Retail", "DeAndre Washington", "Ann Arbor", "Michigan", "+1-734-555-0188", "deandre@greatlakesherbal.com", "linkedin.com/in/deandrewashington", "contacted", 997, (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Windy City Botanicals", "IL-DISP-000841", "Medical & Adult-Use", "Victoria Rossi", "Chicago", "Illinois", "+1-312-555-0176", "vrossi@windycitybotanicals.com", "linkedin.com/in/victoriarossi", "proposal_sent", 1497, (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
        ("Olympic Green Guild", "WA-RET-001290", "Retail", "Jordan Blake", "Seattle", "Washington", "+1-206-555-0130", "jordan@olympicgreenguild.com", "linkedin.com/in/jordanblake-wa", "call_booked", 997, (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")),
    ]

    for lead in sample_leads:
        cursor.execute("""
        INSERT INTO leads (business_name, license_number, license_type, owner_name, city, state, phone, email, linkedin, status, deal_value, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (lead[0], lead[1], lead[2], lead[3], lead[4], lead[5], lead[6], lead[7], lead[8], lead[9], lead[10], lead[11], lead[11]))

    # Seed initial activities
    sample_activities = [
        (1, "deal_closed", "Closed Complete Compliance Package ($1,497) with Emerald Peak Dispensary", (now - timedelta(days=12)).strftime("%Y-%m-%d %H:%M:%S")),
        (8, "deal_closed", "Closed Starter SOP Package ($997) with Sierra Foothills Herbal", (now - timedelta(days=15)).strftime("%Y-%m-%d %H:%M:%S")),
        (2, "call_booked", "Compliance audit call booked with Elena Rostova for tomorrow 2:00 PM MST", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")),
        (3, "proposal_sent", "Sent 15-SOP Package & Metrc compliance proposal to Silver State Botanicals", (now - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")),
        (4, "responded", "Sarah Jenkins replied: 'Very interested in 72hr delivery timeframe. What states?'", (now - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")),
        (13, "proposal_sent", "Delivered proposal ($1,497) to Windy City Botanicals (Illinois)", (now - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S")),
    ]

    for act in sample_activities:
        cursor.execute("""
        INSERT INTO activities (lead_id, activity_type, description, timestamp)
        VALUES (?, ?, ?, ?)
        """, (act[0], act[1], act[2], act[3]))

# ----------------- CRUD Functions -----------------

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status != 'new'")
    messages_sent = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status IN ('responded', 'call_booked', 'proposal_sent', 'closed')")
    responses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads WHERE status IN ('call_booked', 'proposal_sent', 'closed')")
    calls_booked = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), COALESCE(SUM(deal_value), 0) FROM leads WHERE status = 'closed'")
    closed_row = cursor.fetchone()
    deals_closed = closed_row[0]
    revenue_usd = closed_row[1]
    usd_to_pkr = 279
    revenue_pkr = revenue_usd * usd_to_pkr

    # Stage breakdown
    cursor.execute("SELECT status, COUNT(*) FROM leads GROUP BY status")
    stages_count = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    response_rate = round((responses / messages_sent * 100), 1) if messages_sent > 0 else 0.0

    return {
        "total_leads": total_leads,
        "messages_sent": messages_sent,
        "responses": responses,
        "response_rate": response_rate,
        "calls_booked": calls_booked,
        "deals_closed": deals_closed,
        "revenue_usd": revenue_usd,
        "revenue_pkr": revenue_pkr,
        "stages": {
            "new": stages_count.get("new", 0),
            "contacted": stages_count.get("contacted", 0),
            "responded": stages_count.get("responded", 0),
            "call_booked": stages_count.get("call_booked", 0),
            "proposal_sent": stages_count.get("proposal_sent", 0),
            "closed": stages_count.get("closed", 0),
        }
    }

def get_all_leads(status_filter: Optional[str] = None, state_filter: Optional[str] = None, search: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM leads WHERE 1=1"
    params = []

    if status_filter and status_filter != "all":
        query += " AND status = ?"
        params.append(status_filter)

    if state_filter and state_filter != "all":
        query += " AND state = ?"
        params.append(state_filter)

    if search:
        query += " AND (business_name LIKE ? OR owner_name LIKE ? OR city LIKE ? OR license_number LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s, s])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    leads = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return leads

def add_lead(lead_data: Dict[str, Any]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO leads (business_name, license_number, license_type, owner_name, city, state, phone, email, linkedin, status, deal_value, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_data.get("business_name", "Untitled Dispensary"),
        lead_data.get("license_number", ""),
        lead_data.get("license_type", "Retail"),
        lead_data.get("owner_name", "Unknown"),
        lead_data.get("city", ""),
        lead_data.get("state", "Colorado"),
        lead_data.get("phone", ""),
        lead_data.get("email", ""),
        lead_data.get("linkedin", ""),
        lead_data.get("status", "new"),
        lead_data.get("deal_value", 997),
        lead_data.get("notes", ""),
        now_str,
        now_str
    ))
    new_id = cursor.lastrowid

    # Log activity
    cursor.execute("""
    INSERT INTO activities (lead_id, activity_type, description, timestamp)
    VALUES (?, 'created', ?, ?)
    """, (new_id, f"Added prospect {lead_data.get('business_name')}", now_str))

    conn.commit()
    conn.close()
    return new_id

def update_lead_status(lead_id: int, new_status: str, notes: Optional[str] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("SELECT business_name, status FROM leads WHERE id = ?", (lead_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    old_status = row["status"]
    b_name = row["business_name"]

    cursor.execute("""
    UPDATE leads SET status = ?, updated_at = ? WHERE id = ?
    """, (new_status, now_str, lead_id))

    # Activity description
    stage_names = {
        "new": "New Lead",
        "contacted": "Contacted",
        "responded": "Responded",
        "call_booked": "Call Booked",
        "proposal_sent": "Proposal Sent",
        "closed": "Deal Closed"
    }
    desc = f"Moved {b_name} from {stage_names.get(old_status, old_status)} to {stage_names.get(new_status, new_status)}"
    if notes:
        desc += f" — Note: {notes}"

    cursor.execute("""
    INSERT INTO activities (lead_id, activity_type, description, timestamp)
    VALUES (?, 'stage_changed', ?, ?)
    """, (lead_id, desc, now_str))

    conn.commit()
    conn.close()
    return True

def delete_lead(lead_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    cursor.execute("DELETE FROM activities WHERE lead_id = ?", (lead_id,))
    conn.commit()
    conn.close()
    return True

def batch_outreach(lead_ids: List[int], template_type: str, delay_sec: int = 1) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    contacted_count = 0

    for lid in lead_ids:
        cursor.execute("SELECT business_name, owner_name, status FROM leads WHERE id = ?", (lid,))
        row = cursor.fetchone()
        if row:
            cursor.execute("UPDATE leads SET status = 'contacted', updated_at = ? WHERE id = ?", (now_str, lid))
            cursor.execute("""
            INSERT INTO activities (lead_id, activity_type, description, timestamp)
            VALUES (?, 'message_sent', ?, ?)
            """, (lid, f"Sent automated {template_type} to {row['owner_name']} ({row['business_name']})", now_str))
            contacted_count += 1

    conn.commit()
    conn.close()
    return {
        "success": True,
        "contacted": contacted_count,
        "timestamp": now_str
    }

def get_recent_activities(limit: int = 15) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, l.business_name, l.owner_name
    FROM activities a
    LEFT JOIN leads l ON a.lead_id = l.id
    ORDER BY a.id DESC LIMIT ?
    """, (limit,))
    activities = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return activities

def get_settings() -> Dict[str, str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}
    conn.close()
    return settings

def update_settings(settings_dict: Dict[str, str]) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    for k, v in settings_dict.items():
        cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (k, str(v)))
    conn.commit()
    conn.close()
    return True

def reset_database() -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activities")
    cursor.execute("DELETE FROM documents")
    cursor.execute("DELETE FROM leads")
    seed_sample_data(cursor)
    conn.commit()
    conn.close()
    return True

# Initialize on import
init_db()
