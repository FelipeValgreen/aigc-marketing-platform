"use client";
import { Home, FileVideo, LayoutDashboard, Settings, Zap } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

export default function Sidebar() {
  const pathname = usePathname();
  
  const navItems = [
    { label: "Overview", href: "/", icon: LayoutDashboard },
    { label: "Create Studio", href: "/portal", icon: Home },
    { label: "Vault (Bóveda)", href: "/vault", icon: FileVideo },
    { label: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside className="w-64 border-r border-[#27272a] bg-[#09090b] bg-opacity-80 backdrop-blur-3xl flex flex-col h-screen fixed top-0 left-0 z-50">
      <div className="p-6 pb-8 border-b border-[#27272a]">
        <h1 className="text-xl font-bold flex items-center gap-3 text-neutral-100 tracking-tight">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
            <Zap className="w-4 h-4 text-white fill-white" />
          </div>
          UGC Studio
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-1.5 mt-8">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13px] font-medium transition-all duration-200",
              isActive 
                ? "bg-[#18181b] text-white border border-[#27272a] shadow-sm" 
                : "text-neutral-400 hover:text-white hover:bg-[#18181b]/50"
            )}>
              <Icon className={cn("w-4 h-4", isActive ? "text-purple-400" : "text-neutral-500")} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-[#27272a]">
        <div className="flex items-center gap-3 p-3 cursor-pointer rounded-xl hover:bg-[#18181b] transition-colors border border-transparent hover:border-[#27272a]">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-500 overflow-hidden shadow-inner"></div>
          <div className="text-sm">
            <p className="text-gray-200 font-medium">Agency Admin</p>
            <p className="text-neutral-500 text-xs">Premium Plan</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
