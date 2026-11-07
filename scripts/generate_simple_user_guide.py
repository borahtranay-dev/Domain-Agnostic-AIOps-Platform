"""
Script to generate an ultra-clean, simple, 2-3 page User Manual & Quickstart Guide
in English for end-users, developers, and SREs.
Generates:
1. USER_MANUAL_AND_QUICKSTART_GUIDE.docx
2. END_USER_PRODUCT_GUIDE.docx
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")


def create_user_guide(output_path: Path):
    doc = docx.Document()

    # Set 0.75 inch margins
    for s in doc.sections:
        s.top_margin = Inches(0.75)
        s.bottom_margin = Inches(0.75)
        s.left_margin = Inches(0.75)
        s.right_margin = Inches(0.75)

    def set_cell_bg(cell, hex_color):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'''
            <w:tcMar {nsdecls("w")}>
                <w:top w:w="{top}" w:type="dxa"/>
                <w:bottom w:w="{bottom}" w:type="dxa"/>
                <w:left w:w="{left}" w:type="dxa"/>
                <w:right w:w="{right}" w:type="dxa"/>
            </w:tcMar>
        ''')
        tcPr.append(tcMar)

    # Document Title Block
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    r_badge = title_p.add_run("AIOPS AUTONOMOUS SELF-HEALING PLATFORM\n")
    r_badge.font.name, r_badge.font.size, r_badge.font.bold = "Calibri", Pt(9.5), True
    r_badge.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)

    r_title = title_p.add_run("User Manual & Quickstart Guide")
    r_title.font.name, r_title.font.size, r_title.font.bold = "Calibri", Pt(22), True
    r_title.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

    subtitle_p = doc.add_paragraph()
    subtitle_p.paragraph_format.space_before = Pt(2)
    subtitle_p.paragraph_format.space_after = Pt(14)
    r_sub = subtitle_p.add_run("How to register, monitor your websites, configure alert webhooks, and experience automated AI root-cause self-healing in minutes.")
    r_sub.font.name, r_sub.font.size = "Calibri", Pt(11)
    r_sub.font.color.rgb = RGBColor(0x64, 0x74, 0x8B)

    # Callout Box: What is this platform?
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = tbl.cell(0, 0)
    c.width = Inches(7.0)
    set_cell_bg(c, "F0F9FF")
    set_cell_margins(c, top=140, bottom=140, left=180, right=180)
    cp = c.paragraphs[0]
    cp.paragraph_format.space_before = Pt(0)
    cp.paragraph_format.space_after = Pt(0)
    r1 = cp.add_run("💡 What Does This Platform Do?\n")
    r1.font.name, r1.font.size, r1.font.bold = "Calibri", Pt(10.5), True
    r1.font.color.rgb = RGBColor(0x03, 0x69, 0xA1)
    r2 = cp.add_run(
        "This platform is your 24x7 autonomous AI Site Reliability Engineer (SRE). "
        "It monitors your web applications, catches crashes or high-latency spikes, "
        "uses a DeepSeek-R1 AI diagnostic brain to pinpoint the root cause, and proposes "
        "instant, verified remediation fixes so your users never experience downtime."
    )
    r2.font.name, r2.font.size = "Calibri", Pt(10)
    r2.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name, r.font.size = "Calibri", Pt(10)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def step(number, title, desc):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Inches(0.2)
        r_num = p.add_run(f"Step {number}: {title}\n")
        r_num.font.name, r_num.font.size, r_num.font.bold = "Calibri", Pt(10.5), True
        r_num.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        r_desc = p.add_run(desc)
        r_desc.font.name, r_desc.font.size = "Calibri", Pt(9.5)
        r_desc.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
        return p

    # SECTION 1: GETTING STARTED
    h1("1. Account Creation & Secure Sign-In")
    body("Getting started takes less than 60 seconds with our zero-trust secure authentication gateway:")

    step("1.1", "Open the Cockpit in Your Browser", "Navigate to http://localhost:3000 (or your organization's deployment domain). You will be greeted by the enterprise Sign-In / Registration screen.")
    step("1.2", "Register a New Account", "Click the 'Register as New User' tab. Enter your Full Name, your personal/work Gmail address, your 10-digit Mobile Number, and create a password.")
    step("1.3", "Meet the 5-Point Password Security Invariant", "As you type your password, a real-time checklist turns green. Your password must contain: (1) At least 8 characters, (2) One uppercase letter [A-Z], (3) One lowercase letter [a-z], (4) One number [0-9], and (5) One special symbol (!@#$%^&*...).")
    step("1.4", "Verify via Gmail OTP", "Click 'Continue to Gmail Verification'. A 6-digit confirmation code is instantly dispatched to your Gmail inbox via Google's secure mail server. Enter the 6 digits and click 'Verify & Activate Account'.")
    step("1.5", "Sign In Anytime", "You can sign in using either your Gmail address or your Mobile Number, alongside your secure password.")

    # SECTION 2: ATTACHING WEBSITES
    h1("2. Attaching Your Website or Web Application for Monitoring")
    body("Once logged into the cockpit, you can attach any live website (like your Vercel/Netlify app) or local service in 3 clicks:")

    step("2.1", "Navigate to Monitored Services", "In the top navigation tabs, click 'Monitored Services'. You will see active platform clusters and an '➕ Attach Website / Service' button on the top right.")
    step("2.2", "Click '➕ Attach Website / Service'", "A clean modal popup will open requesting your website details.")
    step("2.3", "Fill Out Your Endpoint Details", "Enter: (1) Project / Website Name (e.g., 'Saurav Portfolio' or 'Online Store'), (2) Target URL (e.g., 'https://sauravk-dev.vercel.app/' or 'http://localhost:5000'), and (3) Monitoring Mode ('HTTP Health Ping').")
    step("2.4", "Click 'Attach & Start Monitoring'", "Your website immediately appears as an active monitoring card showing 'Healthy' status, real-time ping latency (e.g., 24ms), and 100% uptime. You can click 'Test Ping ⚡' at any time to verify real-time connectivity.")

    # SECTION 3: CONNECTING ERROR WEBHOOKS
    h1("3. How to Connect Real Crash Alerts (Webhook Ingestion)")
    body("To enable autonomous self-healing for your website, your app can notify the AIOps platform whenever an error or crash occurs:")

    # Code Box
    c_tbl = doc.add_table(rows=1, cols=1)
    c_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cc = c_tbl.cell(0, 0)
    cc.width = Inches(7.0)
    set_cell_bg(cc, "0F172A")
    set_cell_margins(cc, top=100, bottom=100, left=150, right=150)
    cp2 = cc.paragraphs[0]
    cp2.paragraph_format.space_before = Pt(0)
    cp2.paragraph_format.space_after = Pt(0)
    r_code_title = cp2.add_run("// Ingestion Endpoint: POST http://localhost:8000/api/v1/telemetry/ingest\n")
    r_code_title.font.name, r_code_title.font.size, r_code_title.font.bold = "Courier New", Pt(9), True
    r_code_title.font.color.rgb = RGBColor(0x38, 0xBD, 0xF8)
    r_code = cp2.add_run(
        'fetch("http://localhost:8000/api/v1/telemetry/ingest", {\n'
        '  method: "POST",\n'
        '  headers: { "Content-Type": "application/json" },\n'
        '  body: JSON.stringify({\n'
        '    service_id: "my-portfolio",\n'
        '    severity: "critical",\n'
        '    metric_name: "http_server_error_500",\n'
        '    message: "High unhandled error spike on production endpoint"\n'
        '  })\n'
        '});'
    )
    r_code.font.name, r_code.font.size = "Courier New", Pt(8.5)
    r_code.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)

    body("Whenever your app catches an exception, it dispatches this JSON payload. The platform immediately ingests it, correlates metrics, and triggers DeepSeek-R1 AI diagnosis.")

    # SECTION 4: AI SELF-HEALING IN ACTION
    h1("4. Experiencing AI Self-Healing in Action (Incident Drills)")
    body("You can observe the full autonomous self-healing pipeline live in the 'Incidents & Alerts' tab:")

    step("4.1", "Trigger a Synthetic Failure Drill", "Click the '⚡ Simulate Alert' button in the top navigation. The platform injects an operational failure alert (e.g., Database Connection Pool Saturation).")
    step("4.2", "Review AI Root-Cause Diagnosis", "Select the incident (e.g., INC-8921). In the center console, view the DeepSeek-R1 AI Worker diagnosis with its confidence score (e.g., 94%), identified root cause, and retrieved Runbook (RB-001).")
    step("4.3", "Approve Autonomous Remediation", "Click the green 'Approve Remediation' button. The platform executes the surgical fix (drains zombie connections, expands pool limits, or initiates rollback), verifies recovery, and marks the incident 'Resolved'.")

    # SECTION 5: ACCOUNT & SETTINGS
    h1("5. Password Changes & User Profile Settings")
    step("5.1", "Change Your Password", "Click the '⚙️ Settings' button in the top-right navbar and select the '🔒 Change Password' tab. Enter your current password, your new strong password, and click Save. The system immediately hashes the new password with irreversible SHA-256 and invalidates the old one.")
    step("5.2", "View Profile & RBAC Role", "Click '⚙️ Settings' -> '👤 Profile'. View your account name, verified Gmail address, assigned role (Platform Administrator or Member), and your active workspace.")
    step("5.3", "Theme Switcher", "Click the '☀️ Light Mode' / '🌙 Dark Mode' button in the top header. Your personal theme preference is saved specifically to your account.")

    # SUMMARY CHEAT SHEET TABLE
    h1("6. Quick Reference Cheat Sheet")
    table = doc.add_table(rows=5, cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Goal / Action", "Where to Go in UI", "What Happens"]
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        set_cell_bg(cell, "0F172A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(0), Pt(0)
        r = p.add_run(h)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(9.5), True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    rows_data = [
        ("Register / Sign In", "Login Screen", "Registers account with strong password & real Gmail OTP verification."),
        ("Monitor a Website", "Monitored Services -> ➕ Attach", "Adds live target card with ping latency, status, and uptime."),
        ("Test Self-Healing", "Incidents -> ⚡ Simulate Alert", "Simulates incident; AI diagnoses root cause; 1-click executes fix."),
        ("Update Password", "Top Navbar -> ⚙️ Settings", "Cryptographically replaces password hash; zero plaintext stored.")
    ]

    for row_idx, data in enumerate(rows_data, start=1):
        for col_idx, text in enumerate(data):
            cell = table.cell(row_idx, col_idx)
            set_cell_bg(cell, "F8FAFC" if row_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before, p.paragraph_format.space_after = Pt(0), Pt(0)
            r = p.add_run(text)
            r.font.name, r.font.size = "Calibri", Pt(8.5)
            r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    doc.save(str(output_path))
    print(f"Successfully generated clean user guide at: {output_path}")


if __name__ == "__main__":
    create_user_guide(BASE_DIR / "HOW_TO_USE_MY_APP.docx")

