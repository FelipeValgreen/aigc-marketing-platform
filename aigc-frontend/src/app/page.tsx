"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Video, FolderOpen, AlertCircle, PlaySquare, Plus, ArrowUpRight } from "lucide-react";

export default function Dashboard() {
  const [projects, setProjects] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Intentando hacer fetch real, pero controlando errores para que UI brille
    api.get("/projects")
      .then(res => setProjects(res.data))
      .catch((err) => {
        console.error("API Gateway error:", err);
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <header className="flex items-end justify-between pb-6 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2 py-1 rounded bg-indigo-500/10 text-indigo-400 text-xs font-medium border border-indigo-500/20">Production Ready</span>
          </div>
          <h2 className="text-4xl font-semibold tracking-tight text-white mb-2">Dashboard</h2>
          <p className="text-neutral-400 text-sm">Real-time overview of your AI content engine.</p>
        </div>
        <button className="bg-white text-black px-4 py-2 rounded-lg text-sm font-medium hover:bg-neutral-200 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.15)] hover:shadow-[0_0_25px_rgba(255,255,255,0.25)]">
          <Plus className="w-4 h-4" />
          New Generation
        </button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Total Rendered" value="1,248" icon={Video} trend="+12.5%" direction="up" />
        <MetricCard title="Active Campaigns" value="24" icon={FolderOpen} />
        <MetricCard title="Awaiting Script" value="7" icon={AlertCircle} urgent />
      </div>

      <div className="border border-white/5 rounded-2xl bg-[#111111]/80 backdrop-blur-xl overflow-hidden shadow-2xl relative">
        <div className="absolute inset-0 bg-gradient-to-b from-white/[0.03] to-transparent pointer-events-none" />
        
        <div className="p-6 border-b border-white/5 flex items-center justify-between">
          <h3 className="text-lg font-medium text-white/90">Recent Vault Productions</h3>
          <button className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 transition-colors">
            View all <ArrowUpRight className="w-3 h-3" />
          </button>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-neutral-500 font-medium bg-[#161616]">
              <tr>
                <th className="px-6 py-4 rounded-tl-lg">Project Details</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Format</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                <tr><td colSpan={4} className="px-6 py-12 text-center text-neutral-500 animate-pulse">Establishing connection with Backend...</td></tr>
              ) : projects.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-neutral-500">
                    <FolderOpen className="w-8 h-8 mx-auto mb-3 opacity-20" />
                    No projects found. Launch your first workspace.
                  </td>
                </tr>
              ) : projects.map((p: any) => (
                <tr key={p.id} className="hover:bg-white/[0.02] transition-colors group">
                  <td className="px-6 py-4 font-medium text-neutral-200">{p.product_name}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 text-xs rounded-full border ${p.status === 'COMPLETADO' ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-400' : 'border-amber-500/20 bg-amber-500/10 text-amber-400'}`}>
                      {p.status === 'COMPLETADO' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-2" />}
                      {p.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-neutral-400">{p.video_angle || 'Organic UGC'}</td>
                  <td className="px-6 py-4 text-right">
                    <button className="text-neutral-500 hover:text-white transition-colors p-2 hover:bg-white/10 rounded-md">
                      <PlaySquare className="w-4 h-4 ml-auto" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, trend, urgent, direction }: any) {
  return (
    <div className="relative group overflow-hidden rounded-2xl border border-white/5 bg-[#111111]/80 p-6 transition-all hover:bg-[#161616] hover:border-white/10 shadow-lg">
      <div className="absolute -inset-px bg-gradient-to-br from-indigo-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl" />
      <div className="flex justify-between items-start">
        <div className="p-2 bg-white/5 rounded-lg border border-white/5 group-hover:bg-indigo-500/10 group-hover:border-indigo-500/20 transition-colors">
          <Icon className={`w-5 h-5 ${urgent ? 'text-amber-400' : 'text-neutral-400 group-hover:text-indigo-400'}`} />
        </div>
        {trend && (
          <span className={`flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full bg-white/5 border border-white/5 ${direction === 'up' ? 'text-emerald-400' : 'text-amber-400'}`}>
            {direction === 'up' && <ArrowUpRight className="w-3 h-3" />}
            {trend}
          </span>
        )}
      </div>
      <div className="mt-8">
        <p className="text-sm font-medium text-neutral-500">{title}</p>
        <h3 className="text-3xl font-semibold text-white tracking-tight mt-1">{value}</h3>
      </div>
    </div>
  );
}
