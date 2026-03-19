import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AIGC Platform | Premium SaaS",
  description: "Advanced AI Video Generation Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-[#0A0A0A] text-white min-h-screen antialiased selection:bg-indigo-500/30`}>
        <div className="flex">
          <Sidebar />
          <main className="pl-64 flex-1 min-h-screen relative">
            {/* Ambient background glow */}
            <div className="absolute top-0 right-0 w-[600px] h-[400px] bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
            
            <div className="max-w-7xl mx-auto p-10 relative z-10">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
