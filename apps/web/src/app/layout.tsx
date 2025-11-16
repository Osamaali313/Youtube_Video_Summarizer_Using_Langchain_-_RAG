import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI YouTube Summarizer | Transform Videos into Intelligence",
  description: "AI-powered video summarization with multi-agent workflows powered by LangGraph. Extract insights, ask questions, and export knowledge from YouTube videos.",
  keywords: ["YouTube", "AI", "Summarizer", "LangGraph", "LangChain", "Video Summary", "RAG"],
  authors: [{ name: "AI Summarizer Team" }],
  openGraph: {
    title: "AI YouTube Summarizer",
    description: "Transform YouTube videos into intelligent summaries with AI agents",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "AI YouTube Summarizer",
    description: "Transform YouTube videos into intelligent summaries with AI agents",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: 'rgba(17, 24, 39, 0.8)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#f8f9fa',
            },
            className: 'glass',
          }}
          richColors
        />
      </body>
    </html>
  );
}
