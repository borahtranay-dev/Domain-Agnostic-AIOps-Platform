"""
Script to append Enterprise Authentication, Password Security & Gmail Gateway
to PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx and explaination.docx.

Strictly appends to the end of both documents, preserving all historical content.
"""
import docx
from docx.shared import Inches, Pt, RGBColor
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")
KT_MASTER_PATH = BASE_DIR / "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx"
EXPLAIN_PATH = BASE_DIR / "explaination.docx"


def append_security_to_kt_master():
    if not KT_MASTER_PATH.exists():
        print(f"Skipping {KT_MASTER_PATH}, not found")
        return

    doc = docx.Document(str(KT_MASTER_PATH))

    # Check if already added
    for p in doc.paragraphs:
        if "ENTERPRISE SECURITY & AUTHENTICATION SPECIFICATION" in p.text:
            print("Security section already in KT Master. Skipping duplicate append.")
            return

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return p

    def body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name, r.font.size = "Calibri", Pt(10.5)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def bullet(prefix, text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.left_indent = Inches(0.25)
        r1 = p.add_run(prefix + ": ")
        r1.font.name, r1.font.size, r1.font.bold = "Calibri", Pt(10), True
        r1.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        r2 = p.add_run(text)
        r2.font.name, r2.font.size = "Calibri", Pt(10)
        r2.font.color.rgb = RGBColor(0x47, 0x55, 0x69)
        return p

    h1("ENTERPRISE SECURITY & AUTHENTICATION SPECIFICATION")
    body("This section specifies the production-grade zero-trust identity and credential management architecture implemented across the AIOps platform web cockpit and backend gateways.")

    h2("1. Zero Plaintext Passwords & Irreversible SHA-256 Cryptographic Hashing")
    body("Plaintext passwords never exist in source code, server logs, or persistent browser storage. All password credentials undergo irreversible SHA-256 cryptographic hashing prior to persistence and verification.")
    bullet("Algorithm", "Synchronous SHA-256 cryptographic digest implemented in pure TypeScript/JavaScript without external client dependencies.")
    bullet("Initial Seed Security", "Default administrative credentials exist in code solely as mathematical hashes (e.g., hash 240be518fabd2... for initial seed).")
    bullet("Active Override", "Upon initial login, the platform owner executes a self-serve password change. The new SHA-256 hash immediately replaces the initial hash, rendering default credentials permanently invalid.")

    h2("2. Enterprise Strong Password Policy Invariants")
    body("User registration and password modification enforce strict entropy checks via the validatePasswordStrength policy validator:")
    bullet("Minimum Length", "Passwords must contain a minimum of 8 characters.")
    bullet("Character Diversity", "Must contain at least 1 uppercase letter (A-Z), 1 lowercase letter (a-z), 1 numeric digit (0-9), and 1 special symbol (!@#$%^&*...).")
    bullet("Real-Time Visual Guidance", "A reactive UI checklist provides immediate feedback to eliminate registration rejection loops.")

    h2("3. Anti-Brute-Force & Session Protection")
    bullet("Rate Limiting", "Sliding-window IP and token-based rate limiting on all backend API routes (Phase P9).")
    bullet("OTP Lockout", "Strict 5-attempt threshold on 6-digit confirmation codes. Exceeding 5 failed entries terminates the pending session and invalidates the generated code.")

    h2("4. Official Google SMTP Email Dispatch Gateway")
    body("Account activation leverages direct SMTP dispatch via Google's official mail servers rather than third-party middleman relays:")
    bullet("Next.js Server API Route", "apps/web/src/app/api/send-otp/route.ts connects directly to smtp.gmail.com over TLS.")
    bullet("Credential Isolation", "Credentials (GMAIL_USER and GMAIL_APP_PASSWORD) are restricted to .env.local, strictly ignored by source control (.gitignore).")
    bullet("Dual Dispatch Safety", "If credentials are not yet configured on a staging instance, the engine prints the OTP to the server console and activates testing fallback, ensuring testing flows are never blocked.")

    h2("5. Single Super Admin Guarantee & Privilege Escalation Prevention")
    body("Super Admin capabilities are strictly restricted to the platform owner (admin@platform.io). External user self-registration is permanently clamped to role tenant_sre, making client-side privilege escalation architecturally impossible.")

    doc.save(str(KT_MASTER_PATH))
    print(f"Successfully appended Security Specification to {KT_MASTER_PATH}")


def append_security_to_explain():
    if not EXPLAIN_PATH.exists():
        print(f"Skipping {EXPLAIN_PATH}, not found")
        return

    doc = docx.Document(str(EXPLAIN_PATH))

    for p in doc.paragraphs:
        if "AUTHENTICATION, PASSWORD SECURITY & GMAIL GATEWAY EXPLANATION" in p.text:
            print("Security section already in Explain doc. Skipping duplicate append.")
            return

    def h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(22)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(16), True
        r.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)
        return p

    def h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.font.name, r.font.size, r.font.bold = "Calibri", Pt(13), True
        r.font.color.rgb = RGBColor(0x02, 0x84, 0xC7)
        return p

    def body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name, r.font.size = "Calibri", Pt(10.5)
        r.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def qa(q, a):
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(f"Q: {q}")
        r_q.font.name, r_q.font.size, r_q.font.bold = "Calibri", Pt(10.5), True
        r_q.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A)

        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_before = Pt(1)
        p_a.paragraph_format.space_after = Pt(6)
        r_a = p_a.add_run(f"Answer: {a}")
        r_a.font.name, r_a.font.size = "Calibri", Pt(10)
        r_a.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    h1("AUTHENTICATION, PASSWORD SECURITY & GMAIL GATEWAY EXPLANATION")
    body("Simple, comprehensive answers for oral examinations, project reviews, and viva defense regarding authentication, credential hashing, and email delivery.")

    h2("Viva Questions & Explanations: Authentication & Credential Privacy")

    qa(
        "Why does your platform not store plaintext passwords, and how does SHA-256 protect user accounts?",
        "Storing plaintext passwords creates catastrophic vulnerability: if source code or browser storage is inspected, all credentials leak. We use SHA-256 (Secure Hash Algorithm 256-bit), which is a mathematical one-way cryptographic hash function. Even if an attacker reads the hash, it is computationally impossible to reverse-engineer the original plaintext password. When a user logs in, we hash their input and compare hashes."
    )

    qa(
        "How do you ensure the Super Admin account cannot be hijacked after deployment?",
        "The Super Admin role is hardcoded to Saurav's identifier (admin@platform.io). Initially, a default hash exists. Upon first deployment, the Super Admin uses the 'Change Password' feature in the top navigation bar. This generates a brand new SHA-256 hash that permanently overrides the default hash. From that point forward, the default password is dead, and only the Super Admin knows the active credentials."
    )

    qa(
        "Can a normal registering user elevate themselves to become a Super Admin?",
        "No. Privilege escalation is prevented at the schema and route levels. The registration handler in LoginScreen.tsx hardcodes the assigned role to 'tenant_sre' and forces their tenant scope to their dedicated workspace. External users can never assign themselves the 'super_admin' role."
    )

    qa(
        "How is the 6-digit confirmation code protected against brute-force attacks?",
        "The OTP verification component implements an active anti-brute-force guard: users are limited to a maximum of 5 attempts. If an automated script or bot attempts 5 incorrect codes, the session is wiped, pending registration is cancelled, and the code is invalidated."
    )

    qa(
        "Why did you use Google's official SMTP rather than third-party email APIs?",
        "Third-party transactional services (e.g., Twilio, SendGrid) introduce external SaaS dependencies, subscription costs, and data-relay risks. By utilizing Google's direct SMTP service (smtp.gmail.com) with a 16-character Google App Password, emails are dispatched directly from Google's secure mail infrastructure directly to the user's inbox without intermediary data brokers."
    )

    doc.save(str(EXPLAIN_PATH))
    print(f"Successfully appended Security Q&A to {EXPLAIN_PATH}")


if __name__ == "__main__":
    append_security_to_kt_master()
    append_security_to_explain()

