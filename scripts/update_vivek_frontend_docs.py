"""
Script to surgically update Vivek's Frontend deliverables and UI explanation across:
1. PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx
2. explaination.docx
3. END_USER_PRODUCT_GUIDE.docx

Keeps all other sections (P0-P8 backend, AI worker, DevOps, contracts, Saurav, Taranay, Rudra) 100% UNTOUCHED.
"""
import docx
from pathlib import Path

BASE_DIR = Path(r"e:\domain-agnostic-platform")

def update_kt_master():
    doc_path = BASE_DIR / "PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx"
    doc = docx.Document(str(doc_path))
    
    # 1. Update P259: Vivek's summary
    old_p259 = doc.paragraphs[259].text
    if "Vivek (Frontend Lead)" in old_p259:
        doc.paragraphs[259].text = (
            "• Vivek (Frontend Lead) — apps/web: Engineered complete Developer Cockpit UI overhaul: "
            "transitioned from heavy skeuomorphic/claymorphic 3D styling to a clean, minimal flat interface inspired by modern DevOps consoles. "
            "Architected default clean Light Mode with user-specific persistent Dark Mode preferences (stored per user email), "
            "built self-serve onboarding for students and indie developers with separate mandatory Gmail & Mobile Number fields, "
            "integrated 6-digit confirmation code (OTP) verification, implemented Super Admin User Directory modal, "
            "and enforced strict role-based access control (Super Admin vs Tenant SRE) with zero privilege escalation."
        )
        print("Updated KT Master P259 (Vivek Frontend Lead deliverable)")
    
    doc.save(str(doc_path))
    print("Saved PROJECT_KNOWLEDGE_TRANSFER_MASTER.docx")


def update_explaination():
    doc_path = BASE_DIR / "explaination.docx"
    doc = docx.Document(str(doc_path))
    
    # 1. Update P621: Vivek's summary in Phase P7
    if "Vivek (Frontend Lead)" in doc.paragraphs[621].text:
        doc.paragraphs[621].text = (
            "• Vivek (Frontend Lead): Overhauled Developer Cockpit UI in apps/web: transitioned from complex 3D claymorphic/skeuomorphic "
            "shadows to a crisp, minimal flat interface with default Light Mode, user-isolated permanent theme persistence (Light/Dark saved per user email), "
            "self-serve student/dev onboarding with mandatory Gmail and Mobile Number fields, 6-digit confirmation code (OTP) security gate, "
            "and a dedicated Super Admin User Directory modal."
        )
        print("Updated explaination.docx P621")

    # 2. Add / Update Viva Defense questions around P633
    # Check if Vivek UI viva questions already exist
    viva_exists = any("Why did Vivek choose a clean minimal Flat UI" in p.text for p in doc.paragraphs)
    if not viva_exists:
        # Insert viva questions right after P633
        p633 = doc.paragraphs[633]
        
        # Add question 1: Why clean flat UI instead of claymorphism?
        p_q1 = doc.paragraphs[633].insert_paragraph_before(
            "• Q: Why did Vivek choose a clean minimal Flat UI instead of heavy 3D claymorphic or skeuomorphic shadows?: "
            "Answer: Vivek designed the console for real-world SRE on-call engineers. Heavy 3D claymorphism and puffy multi-layer shadows "
            "cause visual fatigue and clutter critical telemetry during high-severity production outages. A flat, high-contrast interface "
            "(similar to Linear, Vercel, and GitHub) enables engineers to instantly scan alert details, read DeepSeek-R1 AI diagnoses, "
            "and authorize one-click hotfix remediations without distraction."
        )
        
        # Add question 2: Onboarding & OTP verification
        p_q2 = doc.paragraphs[633].insert_paragraph_before(
            "• Q: How does Vivek's frontend handle student and developer onboarding securely?: "
            "Answer: Vivek implemented a dual-mode authentication gateway. While Super Admin access is strictly reserved for the platform owner (Saurav), "
            "any student, indie developer, or client engineer can register via a self-serve onboarding portal. Both Gmail and Mobile Number "
            "are separate mandatory fields. To prevent bot registrations and fake accounts, Vivek integrated a 6-digit confirmation code (OTP) step "
            "that verifies contact credentials before launching their isolated tenant workspace."
        )
        
        # Add question 3: User-specific theme persistence
        p_q3 = doc.paragraphs[633].insert_paragraph_before(
            "• Q: How does Vivek's frontend handle theme preferences across multiple users?: "
            "Answer: The login portal is intentionally clean and neutral. Once a user logs in, the Cockpit defaults to a low-fatigue Light Mode. "
            "If an engineer (e.g., Rahul) toggles to Dark Mode in the top-right header, Vivek's engine maps that preference specifically to that user's "
            "email in persistent storage. When Rahul logs in again next time, his dark theme is automatically restored, while other users continue to receive "
            "their own individual theme preferences."
        )
        print("Added Vivek UI Architecture Viva Defense Q&A to explaination.docx")

    doc.save(str(doc_path))
    print("Saved explaination.docx")


def update_end_user_guide():
    doc_path = BASE_DIR / "END_USER_PRODUCT_GUIDE.docx"
    doc = docx.Document(str(doc_path))
    
    # Update P43: UI styling description
    if len(doc.paragraphs) > 43 and "Industrial Matte Obsidian UI" in doc.paragraphs[43].text:
        doc.paragraphs[43].text = (
            "• Modern Minimal Flat UI (Default Light Mode with User-Isolated Dark Toggle): "
            "Eliminated heavy 3D skeuomorphic and claymorphic complexity in favor of an ultra-clean, high-contrast modern interface "
            "inspired by leading developer platforms like Linear, Supabase, and Vercel. Operates in crisp Light Mode by default for daytime readability, "
            "with a top-right toggle to Dark Mode that permanently persists on a per-user account basis."
        )
        print("Updated END_USER_PRODUCT_GUIDE.docx P43")

    # Update P44: Authentication gate description
    if len(doc.paragraphs) > 44 and "Strict B2B Authentication Gate" in doc.paragraphs[44].text:
        doc.paragraphs[44].text = (
            "• Self-Serve Onboarding with Mandatory Gmail & Mobile Verification: "
            "External developers and students can register their own projects to monitor. Registration strictly enforces separate mandatory fields "
            "for Gmail and a 10-digit Mobile Number, protected by a 6-digit confirmation code (OTP) gate before workspace activation. "
            "Super Admin root access remains exclusively guarded for the platform owner (Saurav)."
        )
        print("Updated END_USER_PRODUCT_GUIDE.docx P44")

    doc.save(str(doc_path))
    print("Saved END_USER_PRODUCT_GUIDE.docx")


if __name__ == "__main__":
    update_kt_master()
    update_explaination()
    update_end_user_guide()
    print("All docs successfully updated for Vivek's Frontend scope!")

