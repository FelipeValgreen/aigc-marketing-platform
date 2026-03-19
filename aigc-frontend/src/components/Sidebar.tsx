"use client";
import { Home, FileVideo, LayoutDashboard, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  const pathname = usePathname();
  
  const navItems = [
    { label: "Dashboard", href: "/", icon: LayoutDashboard },
    { label: "Create Project", href: "/portal", icon: Home },
    { label: "Vault (Bóveda)", href: "/vault", icon: FileVideo },
    { label: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-white/5 bg-black/80 backdrop-blur-xl flex flex-col h-screen fixed top-0 left-0 z-50">
      <div className="p-6">
        <h1 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-500 bg-clip-text text-transparent flex items-center gap-2">
          <div className="w-7 h-7 rounded border border-white/10 bg-gradient-to-br from-indigo-500/20 to-purple-600/20 flex items-center justify-center text-white text-[10px] tracking-tighter">AI</div>
          AIGC
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-1.5 mt-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-300",
              isActive 
                ? "bg-white/10 text-white font-medium shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] ring-1 ring-white/10" 
                : "text-neutral-400 hover:text-white hover:bg-white/5"
            )}>
              <Icon className={cn("w-4 h-4", isActive ? "text-indigo-400" : "text-neutral-500")} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-white/5 mx-4 mb-4 rounded-xl bg-white/[0.02]">
        <div className="flex items-center gap-3 cursor-pointer group">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-500 overflow-hidden shadow-lg border border-white/20 shadow-purple-500/20"></div>
          <div className="text-sm">
            <p className="text-gray-200 group-hover:text-white transition-colors">Agency Admin</p>
            <p className="text-neutral-500 text-xs">admin@aigc.inc</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
