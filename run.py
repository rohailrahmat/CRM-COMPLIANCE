"""
Cannabis CRM & Compliance Automation System
Unified One-Click Application Launcher
"""

import sys
import os
import socket
import webbrowser
import time
from pathlib import Path

def find_available_port(start_port=8000, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    os.chdir(Path(__file__).parent)
    
    print("\n" + "="*68)
    print("[*] VERDANT CANNABIS CRM & COMPLIANCE AUTOMATION PLATFORM (v2.0)")
    print("="*68)
    print("Checking dependencies...")

    try:
        import fastapi
        import uvicorn
        import reportlab
        import pydantic
        print("[OK] Core dependencies verified (FastAPI, Uvicorn, ReportLab, Pydantic)")
    except ImportError as e:
        print(f"[!] Missing dependency: {e}")
        print("Please run: python -m pip install fastapi uvicorn reportlab pydantic")
        sys.exit(1)

    # Initialize Database
    from backend.database import init_db
    init_db()
    print("[OK] Local SQLite database verified and pre-seeded (cannabis_crm.db)")

    port = find_available_port(8000)
    url = f"http://127.0.0.1:{port}"

    print(f"\n[+] Starting High-Performance Application Server on {url} ...")
    print(f"[*] Access the Professional Dashboard: {url}")
    print(f"[*] Interactive Swagger API Documentation: {url}/docs")
    print("="*68 + "\n")

    # Launch browser after a short delay
    def open_browser():
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:
            pass

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=port, log_level="info", reload=False)

if __name__ == "__main__":
    main()
