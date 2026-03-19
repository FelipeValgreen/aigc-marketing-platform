import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "UGC Studio | AIGC Platform",
  description: "World-Class AI Video Generation Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body suppressHydrationWarning className={`${inter.className} bg-[#09090b] text-white min-h-screen antialiased selection:bg-purple-500/30`}>
        <div className="flex">
          <Sidebar />
          <main className="pl-64 flex-1 min-h-screen relative overflow-hidden">
            {/* Ambient Background Blur */}
            <div className="fixed top-0 right-0 w-[80vw] h-[80vh] bg-purple-500/5 rounded-full blur-[150px] -z-10 pointer-events-none" />
            <div className="fixed bottom-0 left-64 w-[60vw] h-[60vh] bg-blue-500/5 rounded-full blur-[150px] -z-10 pointer-events-none" />
            
            <div className="max-w-7xl mx-auto p-12 relative z-10">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
