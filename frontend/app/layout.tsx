import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import { Providers } from "./providers";
import "./styles/globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const display = Playfair_Display({ subsets: ["latin"], variable: "--font-display" });

export const metadata: Metadata = {
  title: "AI Maternal & Fetal Monitor",
  description: "AI-driven maternal and fetal monitoring system",
  viewport: "width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes",
  icons: {
    icon: [{ url: "/favicon.ico" }],
    apple: [{ url: "/apple-touch-icon.png" }],
  },
  themeColor: "#db2777",
  appleWebApp: {
    capable: true,
    statusBarStyle: "black-translucent",
    title: "AI Maternal Monitor",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${display.variable} min-h-screen overflow-x-hidden bg-slate-50 text-slate-900 antialiased`}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
