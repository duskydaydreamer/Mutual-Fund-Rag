import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mutual Fund FAQ Assistant",
  description:
    "A facts-only assistant for source-backed information about mutual fund schemes on Groww.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
