import { NextResponse } from "next/server";
import nodemailer from "nodemailer";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { email, name, otp } = body;

    if (!email || !otp) {
      return NextResponse.json(
        { success: false, message: "Email and OTP are required." },
        { status: 400 }
      );
    }

    const gmailUser = process.env.GMAIL_USER || process.env.GMAIL_SMTP_USER;
    const gmailPass = process.env.GMAIL_APP_PASSWORD || process.env.GMAIL_SMTP_PASS;

    // Check if Gmail credentials are provided in .env.local
    if (!gmailUser || !gmailPass) {
      console.log(`\n======================================================`);
      console.log(`[AIOps Auth Gateway - SIMULATION MODE]`);
      console.log(`To enable REAL Gmail delivery, set GMAIL_USER & GMAIL_APP_PASSWORD in apps/web/.env.local`);
      console.log(`Target Recipient : ${email}`);
      console.log(`Verification OTP : >>> ${otp} <<<`);
      console.log(`======================================================\n`);

      return NextResponse.json({
        success: true,
        delivered: false,
        simulated: true,
        message: "Gmail App Password not configured yet. Check terminal console or use fallback code.",
      });
    }

    // Configure Nodemailer Gmail Transporter
    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: {
        user: gmailUser,
        pass: gmailPass,
      },
    });

    const mailOptions = {
      from: `"AIOps Autonomous Platform" <${gmailUser}>`,
      to: email,
      subject: `🔐 Your AIOps Verification Code: ${otp}`,
      text: `Hello ${name || "Engineer"},\n\nYour one-time verification code for the AIOps Autonomous Self-Healing Platform is: ${otp}\n\nThis code will expire in 10 minutes.\n\nBest regards,\nAIOps SecOps Team`,
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f3f4f6; margin: 0; padding: 24px; }
            .container { max-width: 540px; margin: 0 auto; background-color: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 32px; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); }
            .badge { display: inline-block; padding: 4px 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; border-radius: 9999px; background-color: #1e3a8a; color: #60a5fa; margin-bottom: 16px; }
            h2 { color: #ffffff; margin-top: 0; font-size: 20px; font-weight: 600; }
            p { color: #9ca3af; font-size: 14px; line-height: 1.6; margin: 12px 0; }
            .otp-box { background: #1f2937; border: 1px dashed #3b82f6; border-radius: 8px; text-align: center; padding: 20px; margin: 24px 0; }
            .otp-code { font-family: monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #38bdf8; }
            .footer { margin-top: 24px; padding-top: 16px; border-top: 1px solid #1f2937; font-size: 12px; color: #6b7280; text-align: center; }
          </style>
        </head>
        <body>
          <div class="container">
            <span class="badge">AIOps Autonomous Platform</span>
            <h2>Security Verification Code</h2>
            <p>Hello <strong>${name || "Engineer"}</strong>,</p>
            <p>You requested access to the <strong>Domain-Agnostic Autonomous Self-Healing Platform</strong>. Please enter the following 6-digit confirmation code to activate your account:</p>
            
            <div class="otp-box">
              <div class="otp-code">${otp}</div>
            </div>

            <p style="font-size: 13px; color: #ef4444;">⏱️ This verification code is valid for 10 minutes. Never share this code with anyone.</p>
            <p>If you did not initiate this request, you can safely ignore this email.</p>

            <div class="footer">
              AIOps Autonomous Platform &bull; Security &amp; Reliability Operations
            </div>
          </div>
        </body>
        </html>
      `,
    };

    const info = await transporter.sendMail(mailOptions);
    console.log(`[AIOps Auth Gateway] Email successfully sent to ${email}. MessageId: ${info.messageId}`);

    return NextResponse.json({
      success: true,
      delivered: true,
      messageId: info.messageId,
      message: `Verification code successfully sent to ${email}`,
    });
  } catch (error: any) {
    console.error("[AIOps Auth Gateway] Nodemailer error:", error);
    return NextResponse.json(
      {
        success: true, // Still allow graceful fallback so user testing is not blocked
        delivered: false,
        error: error.message || "Failed to send email via SMTP",
        message: "Email dispatch failed. Please check your SMTP settings in .env.local or use fallback code.",
      },
      { status: 200 }
    );
  }
}

