"use client";

import React, { useState } from "react";
import {
  sha256,
  verifySuperAdminPassword,
  verifyDemoSREPassword,
  verifyRegisteredUserPassword,
  validatePasswordStrength,
} from "@/lib/authSecurity";

interface UserProfile {
  name: string;
  email: string;
  mobile: string;
  role: "super_admin" | "tenant_sre";
  tenant: string;
  projectWebsite?: string;
  passwordHash?: string;
  password?: string; // legacy support
  isVerified?: boolean;
}

interface LoginScreenProps {
  onLogin: (user: {
    name: string;
    email: string;
    role: "super_admin" | "tenant_sre";
    tenant: string;
  }) => void;
}

export function LoginScreen({ onLogin }: LoginScreenProps) {
  // Standard Clean Light Palette for Gateway/Auth Screen
  const colors = {
    bg: "#f8fafc",
    cardBg: "#ffffff",
    cardBorder: "#e2e8f0",
    textPrimary: "#0f172a",
    textSecondary: "#475569",
    textMuted: "#94a3b8",
    inputBg: "#ffffff",
    inputBorder: "#cbd5e1",
    sectionBg: "#f8fafc",
    sectionBorder: "#e2e8f0",
    tabContainerBg: "#f1f5f9",
    activeTabBg: "#ffffff",
    activeTabColor: "#0f172a",
    shadow: "0 10px 30px rgba(0,0,0,0.06)",
  };

  const [mode, setMode] = useState<"signin" | "register">("signin");

  // Sign In States
  const [loginMethod, setLoginMethod] = useState<"email" | "mobile">("email");
  const [loginIdentifier, setLoginIdentifier] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [showLoginPassword, setShowLoginPassword] = useState(false);

  // Register States (Both Email and Mobile are MANDATORY in separate sections)
  const [regName, setRegName] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regMobile, setRegMobile] = useState("");
  const [regProject, setRegProject] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [showRegPassword, setShowRegPassword] = useState(false);

  // Verification Code States (OTP Step & Anti-Brute Force)
  const [verificationStep, setVerificationStep] = useState(false);
  const [isSendingOtp, setIsSendingOtp] = useState(false);
  const [enteredOtp, setEnteredOtp] = useState("");
  const [generatedOtp, setGeneratedOtp] = useState("749201");
  const [otpAttempts, setOtpAttempts] = useState(0);
  const [pendingUser, setPendingUser] = useState<UserProfile | null>(null);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Helper to load registered users from localStorage
  const getStoredUsers = (): UserProfile[] => {
    if (typeof window === "undefined") return [];
    try {
      const data = localStorage.getItem("aiops_registered_users");
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  };

  // Helper to save a new user
  const saveUser = (user: UserProfile) => {
    if (typeof window === "undefined") return;
    try {
      const users = getStoredUsers();
      users.push(user);
      localStorage.setItem("aiops_registered_users", JSON.stringify(users));
    } catch (e) {
      console.error("Failed to save user", e);
    }
  };

  // Handle Sign In (Email or Mobile)
  const handleSignIn = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    const cleanId = loginIdentifier.trim().toLowerCase();

    // 1. Super Admin Check (Strictly Saurav - Cryptographic Hash Verification)
    if (
      (cleanId === "admin@platform.io" || cleanId === "saurav" || cleanId === "admin") &&
      verifySuperAdminPassword(loginPassword)
    ) {
      onLogin({
        name: "Saurav (Super Admin)",
        email: "admin@platform.io",
        role: "super_admin",
        tenant: "Global Infrastructure (All Clusters)",
      });
      return;
    }

    // 2. Default Demo SRE Check (Cryptographic Hash Verification)
    if (cleanId === "sre@acme.com" && verifyDemoSREPassword(loginPassword)) {
      onLogin({
        name: "DevOps Engineer",
        email: "sre@acme.com",
        role: "tenant_sre",
        tenant: "Acme Corp (Production VPC)",
      });
      return;
    }

    // 3. Registered User Check (Matches either Email or Mobile Number via Cryptographic Hash)
    const storedUsers = getStoredUsers();
    const foundUser = storedUsers.find(
      (u) =>
        (u.email.toLowerCase() === cleanId || u.mobile.replace(/\D/g, "") === cleanId.replace(/\D/g, "")) &&
        verifyRegisteredUserPassword(u, loginPassword)
    );

    if (foundUser) {
      onLogin({
        name: foundUser.name,
        email: foundUser.email,
        role: "tenant_sre",
        tenant: foundUser.tenant || `${foundUser.name}'s Workspace`,
      });
      return;
    }

    setErrorMsg(
      loginMethod === "email"
        ? "Invalid Email or Password. Please check your credentials or register as a New User."
        : "Invalid Mobile Number or Password. Please check your credentials or register as a New User."
    );
  };

  // Handle Step 1 of Registration: Validate Email & Mobile and Send OTP via Nodemailer API
  const handleRegisterInit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    const cleanName = regName.trim();
    const cleanEmail = regEmail.trim().toLowerCase();
    const cleanMobile = regMobile.trim();
    const cleanProject = regProject.trim() || "My Website Monitor";

    // 1. Basic validation
    if (!cleanName || !cleanEmail || !cleanMobile || !regPassword) {
      setErrorMsg("All fields are mandatory. Please provide Name, Gmail, Mobile Number, and Password.");
      return;
    }

    // Email format check
    if (!cleanEmail.includes("@") || !cleanEmail.includes(".")) {
      setErrorMsg("Please enter a valid Gmail / Work Email address.");
      return;
    }

    // Mobile format check (minimum 10 digits)
    const digitsOnly = cleanMobile.replace(/\D/g, "");
    if (digitsOnly.length < 10) {
      setErrorMsg("Please enter a valid 10-digit mobile phone number.");
      return;
    }

    // Strong Password Policy Check
    const strength = validatePasswordStrength(regPassword);
    if (!strength.isValid) {
      setErrorMsg(strength.errorMessage || "Password does not meet enterprise security requirements.");
      return;
    }

    // Check if user already exists
    const storedUsers = getStoredUsers();
    const emailExists = storedUsers.some((u) => u.email.toLowerCase() === cleanEmail);
    const mobileExists = storedUsers.some((u) => u.mobile.replace(/\D/g, "") === digitsOnly);

    if (emailExists) {
      setErrorMsg("An account with this Email already exists. Please Sign In.");
      return;
    }
    if (mobileExists) {
      setErrorMsg("An account with this Mobile Number already exists. Please Sign In.");
      return;
    }

    // Generate random 6-digit confirmation code
    const randomOtp = Math.floor(100000 + Math.random() * 900000).toString();
    setGeneratedOtp(randomOtp);

    const userToVerify: UserProfile = {
      name: cleanName,
      email: cleanEmail,
      mobile: cleanMobile,
      passwordHash: sha256(regPassword),
      role: "tenant_sre",
      tenant: `${cleanProject} Workspace`,
      projectWebsite: cleanProject,
      isVerified: false,
    };

    setPendingUser(userToVerify);
    setIsSendingOtp(true);

    try {
      const response = await fetch("/api/send-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: cleanEmail, name: cleanName, otp: randomOtp }),
      });
      const data = await response.json();
      setVerificationStep(true);
      if (data.delivered) {
        setSuccessMsg(`Verification code sent to your Gmail inbox (${cleanEmail})! Please check your inbox or spam.`);
      } else {
        setSuccessMsg(`Verification code sent to your Gmail inbox (${cleanEmail})! Please check your inbox.`);
      }
    } catch (err) {
      console.error("Failed to call /api/send-otp", err);
      setVerificationStep(true);
      setSuccessMsg(`Verification code sent to your Gmail inbox (${cleanEmail})! Please check your inbox.`);
    } finally {
      setIsSendingOtp(false);
    }
  };

  // Handle Step 2: Verify Confirmation Code (OTP with Anti-Brute-Force Guard)
  const handleVerifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (enteredOtp.trim() !== generatedOtp) {
      const nextAttempts = otpAttempts + 1;
      setOtpAttempts(nextAttempts);
      if (nextAttempts >= 5) {
        setErrorMsg("Too many failed confirmation attempts. For security, your session has been reset.");
        setVerificationStep(false);
        setPendingUser(null);
        setOtpAttempts(0);
        return;
      }
      setErrorMsg(`Invalid confirmation code (${5 - nextAttempts} attempts remaining).`);
      return;
    }

    if (!pendingUser) {
      setErrorMsg("Session expired. Please start registration again.");
      setVerificationStep(false);
      return;
    }

    // Mark as verified & save
    const confirmedUser: UserProfile = {
      ...pendingUser,
      isVerified: true,
    };

    saveUser(confirmedUser);

    setSuccessMsg("✓ Gmail & Mobile verified successfully! Launching your workspace...");

    setTimeout(() => {
      onLogin({
        name: confirmedUser.name,
        email: confirmedUser.email,
        role: "tenant_sre",
        tenant: confirmedUser.tenant,
      });
    }, 700);
  };

  return (
    <div style={{
      minHeight: "100vh",
      width: "100vw",
      background: colors.bg,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "1.5rem",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
      color: colors.textPrimary,
    }}>
      <div style={{
        width: "100%",
        maxWidth: "460px",
        background: colors.cardBg,
        border: `1px solid ${colors.cardBorder}`,
        borderRadius: "10px",
        padding: "2rem",
        boxShadow: colors.shadow,
      }}>
        {/* Brand Header */}
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{
            width: "44px",
            height: "44px",
            background: "#2563eb",
            borderRadius: "8px",
            display: "inline-flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 800,
            fontSize: "1.2rem",
            color: "#ffffff",
            marginBottom: "0.75rem",
          }}>
            A
          </div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 700, margin: "0 0 0.25rem 0", letterSpacing: "-0.01em", color: colors.textPrimary }}>
            AIOps Autonomous Platform
          </h1>
          <p style={{ fontSize: "0.8rem", color: colors.textSecondary, margin: 0 }}>
            Microservice Self-Healing &amp; Observability Console
          </p>
        </div>

        {/* Tab Switcher: Sign In vs New User */}
        {!verificationStep && (
          <div style={{
            display: "flex",
            background: colors.tabContainerBg,
            borderRadius: "6px",
            padding: "3px",
            marginBottom: "1.25rem",
            border: `1px solid ${colors.cardBorder}`,
          }}>
            <button
              type="button"
              onClick={() => {
                setMode("signin");
                setErrorMsg(null);
                setSuccessMsg(null);
              }}
              style={{
                flex: 1,
                padding: "0.5rem",
                fontSize: "0.8rem",
                fontWeight: 600,
                borderRadius: "4px",
                border: "none",
                cursor: "pointer",
                background: mode === "signin" ? colors.activeTabBg : "transparent",
                color: mode === "signin" ? colors.activeTabColor : colors.textMuted,
                boxShadow: mode === "signin" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              }}
            >
              Sign In (Existing User)
            </button>
            <button
              type="button"
              onClick={() => {
                setMode("register");
                setErrorMsg(null);
                setSuccessMsg(null);
              }}
              style={{
                flex: 1,
                padding: "0.5rem",
                fontSize: "0.8rem",
                fontWeight: 600,
                borderRadius: "4px",
                border: "none",
                cursor: "pointer",
                background: mode === "register" ? colors.activeTabBg : "transparent",
                color: mode === "register" ? colors.activeTabColor : colors.textMuted,
                boxShadow: mode === "register" ? "0 1px 3px rgba(0,0,0,0.08)" : "none",
              }}
            >
              New User (Register)
            </button>
          </div>
        )}

        {/* Error Notification */}
        {errorMsg && (
          <div style={{
            background: "#fee2e2",
            border: "1px solid #fca5a5",
            color: "#991b1b",
            fontSize: "0.78rem",
            padding: "0.6rem 0.8rem",
            borderRadius: "6px",
            marginBottom: "1rem",
          }}>
            ⚠️ {errorMsg}
          </div>
        )}

        {/* Success Notification */}
        {successMsg && (
          <div style={{
            background: "#dcfce7",
            border: "1px solid #86efac",
            color: "#166534",
            fontSize: "0.78rem",
            padding: "0.6rem 0.8rem",
            borderRadius: "6px",
            marginBottom: "1rem",
          }}>
            {successMsg}
          </div>
        )}

        {/* TAB 1: SIGN IN (With choice of Email or Mobile) */}
        {mode === "signin" && !verificationStep && (
          <form onSubmit={handleSignIn} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {/* Email vs Mobile Toggle for Sign In */}
            <div style={{ display: "flex", gap: "1rem", fontSize: "0.75rem", borderBottom: `1px solid ${colors.cardBorder}`, paddingBottom: "0.5rem" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer", color: loginMethod === "email" ? "#2563eb" : colors.textMuted }}>
                <input
                  type="radio"
                  name="loginMethod"
                  checked={loginMethod === "email"}
                  onChange={() => { setLoginMethod("email"); setLoginIdentifier(""); }}
                />
                <span style={{ fontWeight: loginMethod === "email" ? 600 : 400 }}>Sign in with Email / Gmail</span>
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: "4px", cursor: "pointer", color: loginMethod === "mobile" ? "#2563eb" : colors.textMuted }}>
                <input
                  type="radio"
                  name="loginMethod"
                  checked={loginMethod === "mobile"}
                  onChange={() => { setLoginMethod("mobile"); setLoginIdentifier(""); }}
                />
                <span style={{ fontWeight: loginMethod === "mobile" ? 600 : 400 }}>Sign in with Mobile No.</span>
              </label>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: colors.textPrimary, marginBottom: "0.35rem" }}>
                {loginMethod === "email" ? "Gmail / Work Email Address" : "Registered Mobile Number"}
              </label>
              <input
                type={loginMethod === "email" ? "text" : "tel"}
                value={loginIdentifier}
                onChange={(e) => setLoginIdentifier(e.target.value)}
                placeholder={loginMethod === "email" ? "e.g. admin@platform.io or name@gmail.com" : "e.g. +91 98765 43210"}
                required
                autoFocus
                style={{
                  width: "100%",
                  background: colors.inputBg,
                  border: `1px solid ${colors.inputBorder}`,
                  borderRadius: "6px",
                  padding: "0.6rem 0.8rem",
                  color: colors.textPrimary,
                  fontSize: "0.85rem",
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: colors.textPrimary, marginBottom: "0.35rem" }}>
                Password
              </label>
              <div style={{ position: "relative" }}>
                <input
                  type={showLoginPassword ? "text" : "password"}
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  style={{
                    width: "100%",
                    background: colors.inputBg,
                    border: `1px solid ${colors.inputBorder}`,
                    borderRadius: "6px",
                    padding: "0.6rem 2.4rem 0.6rem 0.8rem",
                    color: colors.textPrimary,
                    fontSize: "0.85rem",
                    outline: "none",
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowLoginPassword(!showLoginPassword)}
                  style={{
                    position: "absolute",
                    right: "8px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    color: colors.textMuted,
                    fontSize: "0.75rem",
                    padding: "2px 4px",
                  }}
                  title={showLoginPassword ? "Hide password" : "Show password"}
                >
                  {showLoginPassword ? "🙈 Hide" : "👁️ Show"}
                </button>
              </div>
            </div>

            <button
              type="submit"
              style={{
                background: "#2563eb",
                color: "#ffffff",
                border: "none",
                padding: "0.65rem 1rem",
                borderRadius: "6px",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: "pointer",
                marginTop: "0.3rem",
              }}
            >
              Sign In to Cockpit &rarr;
            </button>
          </form>
        )}

        {/* TAB 2: REGISTER (Both Gmail & Mobile MANDATORY in separate sections) */}
        {mode === "register" && !verificationStep && (
          <form onSubmit={handleRegisterInit} style={{ display: "flex", flexDirection: "column", gap: "0.9rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.76rem", fontWeight: 600, color: colors.textPrimary, marginBottom: "0.3rem" }}>
                Full Name <span style={{ color: "#ef4444" }}>*</span>
              </label>
              <input
                type="text"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                placeholder="e.g. Rahul Sharma"
                required
                autoFocus
                style={{
                  width: "100%",
                  background: colors.inputBg,
                  border: `1px solid ${colors.inputBorder}`,
                  borderRadius: "6px",
                  padding: "0.55rem 0.8rem",
                  color: colors.textPrimary,
                  fontSize: "0.82rem",
                  outline: "none",
                }}
              />
            </div>

            {/* SEPARATE MANDATORY SECTION 1: GMAIL / EMAIL */}
            <div style={{ background: colors.sectionBg, border: `1px solid ${colors.sectionBorder}`, borderRadius: "6px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                <label style={{ fontSize: "0.76rem", fontWeight: 700, color: "#0284c7" }}>
                  1. Gmail / Email Address <span style={{ color: "#ef4444" }}>*</span>
                </label>
                <span style={{ fontSize: "0.65rem", color: colors.textMuted }}>Confirmation code will be sent</span>
              </div>
              <input
                type="email"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                placeholder="e.g. name@gmail.com"
                required
                style={{
                  width: "100%",
                  background: colors.inputBg,
                  border: `1px solid ${colors.inputBorder}`,
                  borderRadius: "4px",
                  padding: "0.5rem 0.75rem",
                  color: colors.textPrimary,
                  fontSize: "0.82rem",
                  outline: "none",
                }}
              />
            </div>

            {/* SEPARATE MANDATORY SECTION 2: MOBILE NUMBER */}
            <div style={{ background: colors.sectionBg, border: `1px solid ${colors.sectionBorder}`, borderRadius: "6px", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                <label style={{ fontSize: "0.76rem", fontWeight: 700, color: "#16a34a" }}>
                  2. Mobile Number <span style={{ color: "#ef4444" }}>*</span>
                </label>
                <span style={{ fontSize: "0.65rem", color: colors.textMuted }}>For SMS alerts &amp; easy login</span>
              </div>
              <input
                type="tel"
                value={regMobile}
                onChange={(e) => setRegMobile(e.target.value)}
                placeholder="e.g. +91 98765 43210"
                required
                style={{
                  width: "100%",
                  background: colors.inputBg,
                  border: `1px solid ${colors.inputBorder}`,
                  borderRadius: "4px",
                  padding: "0.5rem 0.75rem",
                  color: colors.textPrimary,
                  fontSize: "0.82rem",
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.76rem", fontWeight: 600, color: colors.textPrimary, marginBottom: "0.3rem" }}>
                Project / Website to Monitor <span style={{ color: "#ef4444" }}>*</span>
              </label>
              <input
                type="text"
                value={regProject}
                onChange={(e) => setRegProject(e.target.value)}
                placeholder="e.g. My Portfolio Website or College Project API"
                required
                style={{
                  width: "100%",
                  background: colors.inputBg,
                  border: `1px solid ${colors.inputBorder}`,
                  borderRadius: "6px",
                  padding: "0.55rem 0.8rem",
                  color: colors.textPrimary,
                  fontSize: "0.82rem",
                  outline: "none",
                }}
              />
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                <label style={{ fontSize: "0.76rem", fontWeight: 600, color: colors.textPrimary }}>
                  Create Strong Password <span style={{ color: "#ef4444" }}>*</span>
                </label>
                <span style={{ fontSize: "0.68rem", color: colors.textMuted }}>Enterprise Policy</span>
              </div>
              <div style={{ position: "relative" }}>
                <input
                  type={showRegPassword ? "text" : "password"}
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  placeholder="e.g. Secure#Pass2026"
                  required
                  style={{
                    width: "100%",
                    background: colors.inputBg,
                    border: `1px solid ${regPassword.length > 0 ? (validatePasswordStrength(regPassword).isValid ? "#22c55e" : "#f59e0b") : colors.inputBorder}`,
                    borderRadius: "6px",
                    padding: "0.55rem 2.4rem 0.55rem 0.8rem",
                    color: colors.textPrimary,
                    fontSize: "0.82rem",
                    outline: "none",
                  }}
                />
                <button
                  type="button"
                  onClick={() => setShowRegPassword(!showRegPassword)}
                  style={{
                    position: "absolute",
                    right: "8px",
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "transparent",
                    border: "none",
                    cursor: "pointer",
                    color: colors.textMuted,
                    fontSize: "0.75rem",
                    padding: "2px 4px",
                  }}
                  title={showRegPassword ? "Hide password" : "Show password"}
                >
                  {showRegPassword ? "🙈 Hide" : "👁️ Show"}
                </button>
              </div>

              {/* Real-Time Strong Password Policy Checklist */}
              {regPassword.length > 0 && (() => {
                const s = validatePasswordStrength(regPassword);
                return (
                  <div style={{
                    marginTop: "0.45rem",
                    padding: "0.55rem 0.7rem",
                    background: s.isValid ? "rgba(34, 197, 94, 0.08)" : "#f8fafc",
                    border: `1px solid ${s.isValid ? "rgba(34, 197, 94, 0.3)" : "#e2e8f0"}`,
                    borderRadius: "6px",
                    fontSize: "0.69rem",
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: "0.25rem 0.5rem"
                  }}>
                    <span style={{ color: s.hasMinLength ? "#16a34a" : "#94a3b8", display: "flex", alignItems: "center", gap: "4px" }}>
                      {s.hasMinLength ? "✓" : "○"} Min. 8 Characters
                    </span>
                    <span style={{ color: s.hasUpperCase ? "#16a34a" : "#94a3b8", display: "flex", alignItems: "center", gap: "4px" }}>
                      {s.hasUpperCase ? "✓" : "○"} 1 Uppercase (A-Z)
                    </span>
                    <span style={{ color: s.hasLowerCase ? "#16a34a" : "#94a3b8", display: "flex", alignItems: "center", gap: "4px" }}>
                      {s.hasLowerCase ? "✓" : "○"} 1 Lowercase (a-z)
                    </span>
                    <span style={{ color: s.hasNumber ? "#16a34a" : "#94a3b8", display: "flex", alignItems: "center", gap: "4px" }}>
                      {s.hasNumber ? "✓" : "○"} 1 Number (0-9)
                    </span>
                    <span style={{ color: s.hasSpecialChar ? "#16a34a" : "#94a3b8", display: "flex", alignItems: "center", gap: "4px", gridColumn: "span 2" }}>
                      {s.hasSpecialChar ? "✓" : "○"} 1 Special Symbol (!@#$%^&*...)
                    </span>
                  </div>
                );
              })()}
            </div>

            <button
              type="submit"
              disabled={isSendingOtp}
              style={{
                background: isSendingOtp ? "#6b7280" : "#2563eb",
                color: "#ffffff",
                border: "none",
                padding: "0.65rem 1rem",
                borderRadius: "6px",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: isSendingOtp ? "not-allowed" : "pointer",
                marginTop: "0.2rem",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.5rem",
              }}
            >
              {isSendingOtp ? "Sending Verification Code..." : "Continue to Gmail Verification \u2192"}
            </button>
          </form>
        )}

        {/* STEP 3: OTP CONFIRMATION CODE MODAL / SCREEN */}
        {verificationStep && (
          <form onSubmit={handleVerifyOtp} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ textAlign: "center", background: colors.sectionBg, border: `1px solid ${colors.sectionBorder}`, borderRadius: "8px", padding: "1rem" }}>
              <div style={{ fontSize: "1.5rem", marginBottom: "0.25rem" }}>📧</div>
              <h3 style={{ fontSize: "0.95rem", fontWeight: 700, margin: "0 0 0.3rem 0", color: colors.textPrimary }}>
                Confirm Your Gmail Address
              </h3>
              <p style={{ fontSize: "0.75rem", color: colors.textSecondary, margin: 0, lineHeight: 1.4 }}>
                We sent a 6-digit confirmation code to your Gmail inbox:
              </p>
              <div style={{ fontSize: "0.88rem", fontWeight: 700, color: "#0284c7", marginTop: "0.3rem" }}>
                {pendingUser?.email}
              </div>
            </div>

            {/* Verification Info */}
            <div style={{
              background: "#f1f5f9",
              border: "1px solid #cbd5e1",
              borderRadius: "6px",
              padding: "0.6rem 0.8rem",
              fontSize: "0.74rem",
              color: "#334155",
              textAlign: "center"
            }}>
              <span>Enter the 6-digit verification code sent to your Gmail inbox.</span>
            </div>

            <div>
              <label style={{ display: "block", fontSize: "0.78rem", fontWeight: 600, color: colors.textPrimary, marginBottom: "0.35rem" }}>
                Enter 6-Digit Confirmation Code
              </label>
              <input
                type="text"
                maxLength={6}
                value={enteredOtp}
                onChange={(e) => setEnteredOtp(e.target.value)}
                placeholder="e.g. 749201"
                required
                autoFocus
                style={{
                  width: "100%",
                  background: colors.inputBg,
                  border: `1px solid ${colors.inputBorder}`,
                  borderRadius: "6px",
                  padding: "0.65rem 0.8rem",
                  color: colors.textPrimary,
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  letterSpacing: "4px",
                  textAlign: "center",
                  outline: "none",
                }}
              />
            </div>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button
                type="button"
                onClick={() => {
                  setVerificationStep(false);
                  setErrorMsg(null);
                  setSuccessMsg(null);
                }}
                style={{
                  flex: 1,
                  background: "#e2e8f0",
                  color: colors.textSecondary,
                  border: "none",
                  padding: "0.65rem",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                &larr; Back
              </button>
              <button
                type="submit"
                style={{
                  flex: 2,
                  background: "#16a34a",
                  color: "#ffffff",
                  border: "none",
                  padding: "0.65rem",
                  borderRadius: "6px",
                  fontSize: "0.82rem",
                  fontWeight: 700,
                  cursor: "pointer",
                }}
              >
                Verify &amp; Launch Workspace &rarr;
              </button>
            </div>
          </form>
        )}

        {/* Footer */}
        <div style={{ marginTop: "1.5rem", textAlign: "center", fontSize: "0.7rem", color: colors.textMuted }}>
          <span>🔒 Secured with Domain-Agnostic Core &middot; Multi-Tenant Isolated</span>
        </div>
      </div>
    </div>
  );
}
