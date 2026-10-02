import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AIOps Self-Healing Platform | Developer Cockpit",
  description: "Domain-Agnostic AIOps Self-Healing Platform — Developer Cockpit Foundation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
