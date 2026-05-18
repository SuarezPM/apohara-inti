import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Apohara PROBANT — Cross-AI Code Verifier",
  description:
    "A different AI audits the code your AI just wrote. 9-vendor adversarial ensemble + INV-15 formal memory isolation.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-background text-foreground font-body">{children}</body>
    </html>
  );
}
