"use client";
import { useState } from "react";
import ProjectForm from "@/components/ProjectForm";
import { Film, CheckCircle2, Wand2 } from "lucide-react";
import { api } from "@/lib/api";

export default function PortalCliente() {
  const [projectData, setProjectData] = useState<any>(null);
  const [isRendering, setIsRendering] = useState(false);

  const handleApprove = async () => {
    setIsRendering(true);
    try {
      const res = await api.post(`/clients/projects/${projectData.project_id}/approve-and-render`);
      setProjectData({ ...projectData, status: "COMPLETADO", video_url: res.data.video_url });
    } catch (err: any) {
      alert(`Error Backend: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-500 pb-20">
      <header className="mb-12 border-b border-[#27272a] pb-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2.5 rounded-xl bg-[#18181b] border border-[#27272a] shadow-inner text-white">
            <Film className="w-5 h-5" />
          </div>
          <h2 className="text-3xl font-semibold tracking-tight text-white">Production Studio</h2>
        </div>
        <p className="text-neutral-400 text-sm">Engineered for World-Class output. Inject brand DNA to output standard.</p>
      </header>

      {!projectData && (
         <ProjectForm onSuccess={(data) => setProjectData(data)} />
      )}

      {projectData && projectData.status === "GUION_LISTO" && (
        <div className="animate-in zoom-in-95 duration-500">
          <div className="bg-[#18181b] border border-[#27272a] rounded-3xl p-10 mb-6 relative overflow-hidden shadow-2xl">
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-[100px] pointer-events-none" />
            <h3 className="text-2xl font-bold text-white flex items-center gap-3 mb-8 tracking-tight">
              <CheckCircle2 className="w-7 h-7 text-indigo-400" />
              Machine Generated Script
            </h3>
            
            <div className="bg-[#09090b] rounded-2xl p-8 border border-[#27272a] space-y-6 mb-8 shadow-inner">
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase text-indigo-400 tracking-widest block mb-2">Pilar 1: Hook (Gancho)</span>
                <p className="text-white/90 text-lg font-medium">{projectData.script.hook?.script}</p>
                <p className="text-neutral-500 text-sm italic py-2">🎥 Dir: {projectData.script.hook?.visuals}</p>
              </div>
              <div className="h-px w-full bg-[#27272a]" />
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase text-emerald-400 tracking-widest block mb-2">Pilar 2: Body (Desarrollo)</span>
                <p className="text-white/90 text-lg font-medium">{projectData.script.body?.script}</p>
                <p className="text-neutral-500 text-sm italic py-2">🎥 Dir: {projectData.script.body?.visuals}</p>
              </div>
              <div className="h-px w-full bg-[#27272a]" />
              <div className="space-y-1">
                <span className="text-[10px] font-bold uppercase text-amber-400 tracking-widest block mb-2">Pilar 3: Call To Action</span>
                <p className="text-white/90 text-lg font-medium">{projectData.script.cta?.script}</p>
              </div>
            </div>

            <button 
              onClick={handleApprove}
              disabled={isRendering}
              className="w-full bg-white text-black font-bold text-[15px] py-4 rounded-xl flex items-center justify-center gap-3 hover:bg-neutral-200 transition-all disabled:opacity-50 disabled:cursor-wait shadow-[0_0_30px_rgba(255,255,255,0.2)] group"
            >
              {isRendering ? (
                <>
                  <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                  Conectando FFmpeg y TTS... (Renderizando Toma)
                </>
              ) : (
                <><Wand2 className="w-4 h-4 group-hover:rotate-12 transition-transform" /> Deploy to Production (Render Final)</>
              )}
            </button>
          </div>
        </div>
      )}

      {projectData && projectData.status === "COMPLETADO" && (
        <div className="animate-in slide-in-from-bottom-8 duration-700 bg-[#18181b] backdrop-blur-3xl rounded-3xl border border-emerald-500/20 p-12 text-center relative overflow-hidden shadow-2xl">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-emerald-600" />
          <div className="w-20 h-20 bg-[#09090b] rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-500/30 shadow-[0_0_30px_rgba(52,211,153,0.15)]">
            <CheckCircle2 className="w-10 h-10 text-emerald-400" />
          </div>
          <h3 className="text-3xl font-bold text-white tracking-tight mb-2">Pipeline Finalizado</h3>
          <p className="text-neutral-400 mb-10">B-Roll, TTS Neural, Audio Ducking y Filtros ASS inyectados.</p>
          
          <div className="aspect-[9/16] w-full max-w-[280px] mx-auto bg-[#09090b] rounded-2xl overflow-hidden border border-[#27272a] shadow-inner relative ring-4 ring-black">
            <video src={projectData.video_url} controls className="w-full h-full object-cover" autoPlay />
          </div>
          
          <button 
            onClick={() => setProjectData(null)}
            className="mt-10 px-6 py-2 bg-white/5 border border-white/10 rounded-full text-sm text-neutral-300 font-medium hover:text-white hover:bg-white/10 transition-all"
          >
            ← Volver al Workshop
          </button>
        </div>
      )}
    </div>
  );
}
