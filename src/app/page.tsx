"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Video, FolderOpen, PlaySquare, ArrowUpRight, Wand2, Activity } from "lucide-react";
import { useRouter } from "next/navigation";

export default function Dashboard() {
  const router = useRouter();
  const [projects, setProjects] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [errorSync, setErrorSync] = useState(false);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await api.get("/clients/projects");
        setProjects(res.data);
      } catch (err) {
        setErrorSync(true);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProjects();
  }, []);

  return (
    <div className="space-y-10 animate-in fade-in duration-700">
      <header className="flex items-end justify-between pb-6 border-b border-[#27272a]">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-emerald-500 text-[10px] font-bold uppercase tracking-widest">System Operational</span>
          </div>
          <h2 className="text-3xl font-semibold tracking-tight text-white mb-2">Overview</h2>
          <p className="text-neutral-400 text-sm">Track your AI-generated video campaigns in real time.</p>
        </div>
        <button onClick={() => router.push('/onboarding')} className="bg-white text-black px-5 py-2.5 rounded-lg text-sm font-semibold hover:bg-neutral-200 transition-all flex items-center gap-2 shadow-[0_0_20px_rgba(255,255,255,0.1)]">
          <Wand2 className="w-4 h-4" />
          Create Video
        </button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Total Rendered" value="1,248" icon={Video} trend="+12.5%" direction="up" />
        <MetricCard title="Active Campaigns" value="24" icon={FolderOpen} />
        <MetricCard title="System Load" value="1.2s" icon={Activity} />
      </div>

      <div className="border border-[#27272a] rounded-2xl bg-[#18181b]/50 backdrop-blur-3xl overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-[#27272a] flex items-center justify-between">
          <h3 className="text-base font-medium text-white/90">Recent Vault Productions</h3>
          <button className="text-xs font-semibold text-neutral-500 hover:text-white flex items-center gap-1 transition-colors uppercase tracking-wider">
            View all <ArrowUpRight className="w-3 h-3" />
          </button>
        </div>
        
        <div className="overflow-x-auto">
          {isLoading && (
            <div className="px-6 py-20 flex flex-col items-center justify-center space-y-5">
              <div className="w-full max-w-[200px] h-1 bg-[#27272a] rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 w-1/3 animate-[pulse_1s_ease-in-out_infinite] transition-all rounded-full" />
              </div>
              <p className="text-[12px] font-medium text-neutral-500 uppercase tracking-widest animate-pulse">Syncing with AI Engine...</p>
            </div>
          )}

          {!isLoading && errorSync && (
             <div className="px-6 py-12 text-center text-red-400 text-sm bg-red-500/5">
                Error Connecting to API. Ensure Hugging Face Space is Awake.
             </div>
          )}
          
          {!isLoading && !errorSync && projects.length === 0 && (
             <div className="px-6 py-16 text-center text-neutral-500 flex flex-col items-center">
                <FolderOpen className="w-8 h-8 mb-3 opacity-20" />
                <p>No projects found. Launch your first workspace.</p>
             </div>
          )}

          {!isLoading && projects.length > 0 && (
            <table className="w-full text-sm text-left">
              <thead className="text-[11px] text-neutral-500 font-medium uppercase tracking-wider bg-[#09090b]/50 border-b border-[#27272a]">
                <tr>
                  <th className="px-8 py-4">Project Details</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Format</th>
                  <th className="px-8 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#27272a]">
                {projects.map((p: any) => (
                  <tr key={p.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="px-8 py-4 font-medium text-neutral-200">{p.product_name}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2 py-1 text-[10px] uppercase font-bold tracking-widest rounded border ${p.status === 'COMPLETADO' ? 'border-emerald-500/20 text-emerald-400 bg-emerald-500/10' : 'border-amber-500/20 text-amber-400 bg-amber-500/10'}`}>
                        {p.status === 'COMPLETADO' && <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5" />}
                        {p.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-neutral-400">{p.video_angle || 'Organic UGC'}</td>
                    <td className="px-8 py-4 text-right">
                      <button className="text-neutral-500 hover:text-white transition-colors hover:bg-white/5 p-1.5 rounded">
                        <PlaySquare className="w-4 h-4 ml-auto" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon: Icon, trend, direction }: any) {
  return (
    <div className="relative group overflow-hidden rounded-2xl border border-[#27272a] bg-[#18181b] p-6 transition-all hover:border-[#3f3f46] shadow-sm cursor-default">
      <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 blur-[30px] rounded-full pointer-events-none group-hover:bg-indigo-500/20 transition-all opacity-0 group-hover:opacity-100" />
      <div className="flex justify-between items-start">
        <div className="p-2.5 rounded-xl border border-[#27272a] bg-[#09090b] text-neutral-400 group-hover:text-indigo-400 transition-colors shadow-inner relative z-10">
          <Icon className="w-5 h-5" />
        </div>
        {trend && (
          <span className={`flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-full bg-[#09090b] border border-[#27272a] tracking-wide relative z-10 ${direction === 'up' ? 'text-emerald-400' : 'text-amber-400'}`}>
            {direction === 'up' && <ArrowUpRight className="w-3 h-3" />}
            {trend}
          </span>
        )}
      </div>
      <div className="mt-8 relative z-10">
        <p className="text-[13px] font-medium text-neutral-500">{title}</p>
        <h3 className="text-4xl font-semibold text-white tracking-tight mt-1">{value}</h3>
      </div>
    </div>
  );
}
