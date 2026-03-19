"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { UploadCloud, Film, Music, CheckCircle2, ChevronRight, Wand2 } from "lucide-react";

export default function PortalCliente() {
  const [clientId, setClientId] = useState("");
  const [productName, setProductName] = useState("");
  const [productDesc, setProductDesc] = useState("");
  const [angle, setAngle] = useState("UGC Tradicional");
  const [music, setMusic] = useState("Sin Música");
  const [file, setFile] = useState<File | null>(null);
  
  const [projectData, setProjectData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRendering, setIsRendering] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    const formData = new FormData();
    formData.append("client_id", clientId);
    formData.append("product_name", productName);
    formData.append("product_desc", productDesc);
    formData.append("video_angle", angle);
    formData.append("music_style", music);
    if (file) formData.append("custom_media", file);

    try {
      const res = await api.post("/projects", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setProjectData(res.data);
    } catch (err: any) {
      console.error(err);
      alert(`Error del Backend: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleApprove = async () => {
    setIsRendering(true);
    try {
      const res = await api.post(`/projects/${projectData.project_id}/approve-and-render`);
      setProjectData({ ...projectData, status: "COMPLETADO", video_url: res.data.video_url });
    } catch (err) {
      console.error(err);
      alert("Error al renderizar el video.");
    } finally {
      setIsRendering(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-500 pb-20">
      <header className="mb-10">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
            <Film className="w-5 h-5" />
          </div>
          <h2 className="text-3xl font-semibold tracking-tight text-white">Portal de Producción</h2>
        </div>
        <p className="text-neutral-400">Lleva el ADN de tu marca directamente a la renderización en VTT.</p>
      </header>

      {/* Formulario Principal */}
      {!projectData && (
        <form onSubmit={handleSubmit} className="space-y-6 bg-[#111111]/80 backdrop-blur-xl p-8 rounded-2xl border border-white/5 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-[80px]" />
          
          <div className="grid grid-cols-2 gap-6 relative z-10">
            <div className="col-span-2 md:col-span-1 space-y-2">
              <label className="text-sm font-medium text-neutral-300">ID de Marca (Cliente)</label>
              <input 
                type="number" required 
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-neutral-600"
                placeholder="Ej. 1"
                onChange={e => setClientId(e.target.value)} 
              />
            </div>
            <div className="col-span-2 md:col-span-1 space-y-2">
              <label className="text-sm font-medium text-neutral-300">Nombre del Producto</label>
              <input 
                type="text" required 
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-neutral-600"
                placeholder="Pastelones Antideslizantes"
                onChange={e => setProductName(e.target.value)} 
              />
            </div>
            <div className="col-span-2 space-y-2">
              <label className="text-sm font-medium text-neutral-300">Descripción Estratégica</label>
              <textarea 
                required rows={3}
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-neutral-600 resize-none"
                placeholder="Escribe el contexto del producto..."
                onChange={e => setProductDesc(e.target.value)} 
              />
            </div>

            {/* Selectores de Estrategia */}
            <div className="col-span-2 md:col-span-1 space-y-2">
              <label className="text-sm font-medium text-neutral-300 flex items-center gap-2">
                <Wand2 className="w-4 h-4 text-purple-400" />
                Ángulo del Guion
              </label>
              <select 
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none appearance-none"
                onChange={e => setAngle(e.target.value)}
              >
                <option>UGC Tradicional</option>
                <option>Hard Selling</option>
                <option>Storytelling + Voice Over</option>
                <option>Educativo/Concientización</option>
              </select>
            </div>
            <div className="col-span-2 md:col-span-1 space-y-2">
              <label className="text-sm font-medium text-neutral-300 flex items-center gap-2">
                <Music className="w-4 h-4 text-emerald-400" />
                Música (Background)
              </label>
              <select 
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-2.5 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none appearance-none"
                onChange={e => setMusic(e.target.value)}
              >
                <option>Sin Música</option>
                <option>Upbeat (Dinámico)</option>
                <option>Corporativo (Serio)</option>
                <option>Lo-Fi (Relajado)</option>
              </select>
            </div>

            {/* Drag & Drop File Upload */}
            <div className="col-span-2 mt-2">
              <label className="text-sm font-medium text-neutral-300 mb-2 block">Media (B-Roll Propio)</label>
              <label htmlFor="custom_media" className="border-2 border-dashed border-white/10 rounded-xl p-8 text-center hover:border-indigo-500/50 hover:bg-indigo-500/5 transition-all group relative cursor-pointer block">
                <input 
                  id="custom_media"
                  type="file" 
                  className="hidden"
                  accept="video/mp4,video/quicktime,image/jpeg,image/png"
                  onChange={e => setFile(e.target.files?.[0] || null)}
                />
                <UploadCloud className="w-8 h-8 text-neutral-500 mx-auto mb-3 group-hover:text-indigo-400 transition-colors" />
                <p className="text-sm text-neutral-300 font-medium">
                  {file ? file.name : "Arrastra un video o imagen aquí (Clic para subir)"}
                </p>
                <p className="text-xs text-neutral-500 mt-1">MP4, MOV, JPG o PNG (Opcional)</p>
              </label>
            </div>
          </div>
          
          <button 
            disabled={isLoading}
            className="w-full mt-8 bg-white text-black py-3.5 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-neutral-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_20px_rgba(255,255,255,0.15)]"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin" />
            ) : (
              <>Generar Guiones de IA <ChevronRight className="w-4 h-4" /></>
            )}
          </button>
        </form>
      )}

      {/* Aprobador de Guion y Pasarela de Renderizado */}
      {projectData && projectData.status === "GUION_LISTO" && (
        <div className="animate-in slide-in-from-bottom-8 duration-500">
          <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-8 mb-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-full h-full bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 to-transparent pointer-events-none" />
            <h3 className="text-xl font-semibold text-white flex items-center gap-2 mb-6">
              <CheckCircle2 className="w-6 h-6 text-indigo-400" />
              Guion Generado Exitosamente
            </h3>
            
            <div className="bg-black/50 rounded-xl p-6 border border-white/5 space-y-4 mb-8">
              <div>
                <span className="text-xs font-bold uppercase text-indigo-400 tracking-wider">Hook (Gancho)</span>
                <p className="text-white/90 mt-1">{projectData.script.hook?.script}</p>
                <p className="text-neutral-500 text-sm mt-1 border-l-2 border-white/10 pl-3 italic">{projectData.script.hook?.visuals}</p>
              </div>
              <div className="h-px w-full bg-white/5" />
              <div>
                <span className="text-xs font-bold uppercase text-emerald-400 tracking-wider">Body (Desarrollo)</span>
                <p className="text-white/90 mt-1">{projectData.script.body?.script}</p>
                <p className="text-neutral-500 text-sm mt-1 border-l-2 border-white/10 pl-3 italic">{projectData.script.body?.visuals}</p>
              </div>
              <div className="h-px w-full bg-white/5" />
              <div>
                <span className="text-xs font-bold uppercase text-amber-400 tracking-wider">Call To Action (Cierre)</span>
                <p className="text-white/90 mt-1">{projectData.script.cta?.script}</p>
              </div>
            </div>

            <button 
              onClick={handleApprove}
              disabled={isRendering}
              className="w-full bg-indigo-500 text-white py-4 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-indigo-600 transition-all disabled:opacity-50 disabled:cursor-wait shadow-[0_0_30px_rgba(99,102,241,0.3)] relative z-10"
            >
              {isRendering ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin mr-2" />
                  Conectando FFmpeg y TTS... (Renderizando)
                </>
              ) : (
                "Aprobar y Enviar a Producción (Render)"
              )}
            </button>
          </div>
        </div>
      )}

      {/* Entrega Final del Motor */}
      {projectData && projectData.status === "COMPLETADO" && (
        <div className="animate-in zoom-in-95 duration-500 bg-[#111111]/80 backdrop-blur-xl rounded-2xl border border-emerald-500/20 p-8 text-center relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full p-1 bg-emerald-500/20" />
          <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-emerald-500/20">
            <CheckCircle2 className="w-8 h-8 text-emerald-400" />
          </div>
          <h3 className="text-2xl font-bold text-white mb-2">¡Producción Finalizada!</h3>
          <p className="text-neutral-400 mb-8">El archivo ha sido masterizado exitosamente con tu identidad de marca.</p>
          
          <div className="aspect-[9/16] w-full max-w-xs mx-auto bg-black rounded-xl overflow-hidden border border-white/10 shadow-2xl relative">
            <video src={projectData.video_url} controls className="w-full h-full object-cover" autoPlay />
          </div>
          
          <button 
            onClick={() => setProjectData(null)}
            className="mt-8 text-sm text-neutral-400 hover:text-white transition-colors"
          >
            ← Crear otro proyecto
          </button>
        </div>
      )}
    </div>
  );
}
