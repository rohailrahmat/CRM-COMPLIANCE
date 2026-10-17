"""
PDF Generator Module using ReportLab
Generates formal, state-compliant Standard Operating Procedure (SOP) documentation packages for cannabis dispensaries.
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

DOCS_DIR = Path(__file__).parent.parent / "generated_docs"
DOCS_DIR.mkdir(exist_ok=True)

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that adds page numbers and running header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header (only on page 2+)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "CANNABIS STATE COMPLIANCE PROTOCOL — CONFIDENTIAL & PRIVILEGED")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 36, page_str)
        self.drawString(54, 36, "Verdant Compliance Automation System | Certified Cannabis SOP Series")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)

        self.restoreState()

def get_sop_templates(business_name: str, state: str, license_num: str):
    return {
        "Inventory Management SOP": {
            "code": "SOP-INV-001",
            "title": f"Metrc & Track-and-Trace Inventory Reconciliation SOP",
            "purpose": f"Establish mandatory daily, weekly, and monthly inventory counts, weight verifications, and electronic reporting into the state {state} track-and-trace system.",
            "sections": [
                ("1. Purpose & Scope", f"This Standard Operating Procedure applies to all inventory control specialists, managers, and vault agents at {business_name} operating under state license #{license_num}. It governs all intake, quarantine, tag attachment, package creation, and reconciliation."),
                ("2. Regulatory Compliance Authority", f"This protocol complies with statutory mandates outlined in {state} Cannabis Regulatory Agency regulations regarding chain-of-custody, RFID tag scanning, and diversion prevention."),
                ("3. Daily Intake & Receiving Procedures", "Upon receipt of licensed cannabis manifest:\n• Verify state-licensed transport manifests against physical delivery manifests.\n• Perform visual inspection for seal integrity, moisture, tamper evidence, and certificate of analysis (COA).\n• Scan Metrc / state RFID package tags immediately into inventory management within 2 hours of arrival."),
                ("4. Discrepancy & Quarantine Protocols", "Any physical weight or count discrepancy exceeding 1.0% must immediately trigger quarantine status. The Compliance Officer must be alerted within 2 hours, and an internal incident log logged within 24 hours."),
                ("5. Daily Cycle Counts & Close-of-Business Audit", "Every business day at closing, dual-authorized budtenders and managers conduct 100% drawer and safe cycle counts. Zero-variance sign-offs are submitted electronically.")
            ]
        },
        "Security & Video Surveillance SOP": {
            "code": "SOP-SEC-002",
            "title": f"Physical Security, Access Control & Surveillance Protocol",
            "purpose": f"Ensure continuous 24/7/365 multi-camera coverage, offsite retention, visitor logging, and rapid emergency panic response at {business_name}.",
            "sections": [
                ("1. Security Governance", f"This document establishes perimeter integrity, access badge protocols, and continuous recording requirements for {business_name} under license #{license_num}."),
                ("2. Surveillance Architecture & Storage", f"Surveillance cameras must record 24/7 at minimum 15 frames per second with full coverage of all point-of-sale areas, vault entrances, cultivation bays, customer check-in, and exterior loading zones. Footage is archived off-site for no less than 90 days as mandated by {state} law."),
                ("3. Limited Access Areas (LAA)", "Access to the inventory vault, safe deposit room, and server control rooms is strictly limited to badged authorized personnel. All visitor and contractor entries must be documented in the digital visitor register."),
                ("4. Alarm Systems & Duress Protocols", "Silent duress alarm stations are located at each POS register, back vault door, and manager office. Armed dispatch response is verified quarterly.")
            ]
        },
        "Cash Handling Procedures": {
            "code": "SOP-FIN-003",
            "title": f"Cash Handling, Anti-Diversion & Armored Transport Procedures",
            "purpose": f"Standardize retail drawer bank reconciliation, counterfeit detection, anti-money laundering compliance, and secure cash drop schedules.",
            "sections": [
                ("1. Operational Context", f"Due to federal banking limitations, cash controls at {business_name} require strict dual-custody verification and electronic audit logging."),
                ("2. Point of Sale Cash Limits", "Drawer banks are capped at $500 total cash. Whenever drawer balances exceed $1,000, budtenders must execute an immediate secure drop into the drop-safe."),
                ("3. End of Day Reconciliation", "End-of-shift audits require dual witness counting. All cash is reconciled against POS ledger reports and transferred to the UL-listed safe."),
                ("4. Armored Transport Protocol", "Cash pickups occur exclusively through licensed, insured armored courier vehicles with randomized pickup timing.")
            ]
        },
        "Employee Training Manual": {
            "code": "SOP-HR-004",
            "title": f"State-Mandated Responsible Cannabis Vendor & Staff Training Protocol",
            "purpose": f"Provide comprehensive training modules on customer age verification, impairment recognition, product packaging regulations, and workplace safety.",
            "sections": [
                ("1. Training Overview", f"All newly onboarded team members at {business_name} must complete 16 hours of structured compliance training prior to handling regulated products."),
                ("2. Age Verification Protocol", f"100% ID check requirement. No individual under 21 years of age (or valid medical cardholder for medical states) is permitted past the secure check-in vestibule."),
                ("3. Impairment Detection", "Prohibition of sale to visibly intoxicated or impaired customers. Staff are empowered to refuse service with management sign-off."),
                ("4. Health & Sanitation", "Handwashing requirements, clean-room PPE protocols, and hazardous chemical spill responses.")
            ]
        },
        "Incident Reporting SOP": {
            "code": "SOP-INC-005",
            "title": f"Incident Response, Regulatory Notification & Product Recall Plan",
            "purpose": f"Establish immediate response workflows for security intrusions, product recalls, pesticide contamination, and state agency reporting.",
            "sections": [
                ("1. Notification Thresholds", f"Any burglary, diversion, unexplained loss, or regulatory inquiry at {business_name} must be reported to the {state} regulatory authority within 24 hours."),
                ("2. Recall Execution", "In the event of a state-issued or internal recall, all affected lot tags must be quarantined in the POS system within 60 minutes. Push notifications are issued to registered purchase loyalty members if applicable."),
                ("3. Root Cause Analysis", "A formal CAPA (Corrective and Preventive Action) report must be completed within 5 business days of any reported incident.")
            ]
        }
    }

def generate_sop_pdf(sop_name: str, business_name: str, state: str, license_num: str, tier: str = "Complete") -> str:
    """Generates a polished compliance PDF and returns the file path."""
    templates = get_sop_templates(business_name, state, license_num)
    template = templates.get(sop_name, templates["Inventory Management SOP"])

    filename = f"{sop_name.replace(' ', '_')}_{business_name.replace(' ', '_')}_{state}.pdf"
    file_path = DOCS_DIR / filename

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#065F46"),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14
    )

    heading2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#065F46")
    )

    story = []

    # Header Badge / Organization
    org_table_data = [
        [
            Paragraph(f"<b>ORGANIZATION:</b> {business_name.upper()}", body_style),
            Paragraph(f"<b>DOCUMENT CODE:</b> {template['code']}", body_style)
        ],
        [
            Paragraph(f"<b>STATE JURISDICTION:</b> {state.upper()} CANNABIS AUTHORITY", body_style),
            Paragraph(f"<b>EFFECTIVE DATE:</b> {datetime.now().strftime('%B %d, %Y')}", body_style)
        ],
        [
            Paragraph(f"<b>FACILITY LICENSE #:</b> {license_num}", body_style),
            Paragraph(f"<b>COMPLIANCE PACKAGE:</b> {tier.upper()} TIER", body_style)
        ]
    ]

    org_table = Table(org_table_data, colWidths=[3.25 * inch, 3.25 * inch])
    org_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D1FAE5")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))

    story.append(org_table)
    story.append(Spacer(1, 16))

    # Main Title
    story.append(Paragraph(template['title'], title_style))
    story.append(Paragraph(f"Official Regulatory Standard Operating Procedure for {business_name}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#10B981"), spaceAfter=14))

    # Executive Summary / Purpose Box
    purpose_box_data = [
        [Paragraph(f"<b>EXECUTIVE PURPOSE:</b> {template['purpose']}", callout_style)]
    ]
    purpose_table = Table(purpose_box_data, colWidths=[6.5 * inch])
    purpose_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#34D399")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(purpose_table)
    story.append(Spacer(1, 14))

    # Sections
    for sec_title, sec_body in template['sections']:
        story.append(Paragraph(sec_title, heading2_style))
        for line in sec_body.split("\n"):
            story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 4))

    # Sign-off Approval Block
    story.append(Spacer(1, 14))
    story.append(Paragraph("6. Regulatory Approval & Executive Sign-Off", heading2_style))

    sign_data = [
        ["Title / Role", "Printed Name", "Signature", "Date"],
        ["Designated General Manager", "______________________", "______________________", "____/____/2026"],
        ["Compliance Officer", "______________________", "______________________", "____/____/2026"],
        ["Lead Inventory Controller", "______________________", "______________________", "____/____/2026"]
    ]
    sign_table = Table(sign_data, colWidths=[2.2 * inch, 1.8 * inch, 1.5 * inch, 1.0 * inch])
    sign_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(sign_table)

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    return str(file_path)

if __name__ == "__main__":
    path = generate_sop_pdf("Inventory Management SOP", "Highland Green Co.", "Colorado", "CO-402-00388")
    print(f"Generated test PDF: {path}")
