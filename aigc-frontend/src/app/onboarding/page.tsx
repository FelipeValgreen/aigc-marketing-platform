"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { Box, Send, Briefcase, PaintBucket, Target } from "lucide-react";
import { useRouter } from "next/navigation";

export default function Onboarding() {
  const router = useRouter();
  const [companyName, setCompanyName] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg("");
    
    try {
      const res = await api.post("/onboarding", {
        company_name: companyName,
        website_url: websiteUrl
      });
      setResult(res.data);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || "Error extrayendo ADN. Intenta de nuevo.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto animate-in fade-in duration-500 pb-20">
      <header className="mb-10 text-center">
        <h2 className="text-4xl font-semibold tracking-tight text-white mb-3">Extracción de Identidad</h2>
        <p className="text-neutral-400 max-w-lg mx-auto">Ingresa la URL de la marca. Nuestra IA navegará la web web, extraerá el tono de voz y el color corporativo automáticamente.</p>
      </header>

      {!result ? (
        <form onSubmit={handleSubmit} className="max-w-lg mx-auto bg-[#111111]/80 backdrop-blur-xl p-8 rounded-2xl border border-white/5 shadow-2xl relative overflow-hidden">
          <div className="space-y-4 relative z-10">
             <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-300">Nombre de la Empresa</label>
              <input 
                type="text" required 
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-neutral-600"
                placeholder="Ej. Hormiglass"
                onChange={e => setCompanyName(e.target.value)} 
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-neutral-300">URL del Sitio Web</label>
              <input 
                type="url" required 
                className="w-full bg-black/50 border border-white/10 rounded-lg px-4 py-3 text-white focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all placeholder:text-neutral-600"
                placeholder="https://hormiglass.cl"
                onChange={e => setWebsiteUrl(e.target.value)} 
              />
            </div>
            {errorMsg && <p className="text-red-400 text-sm py-2">{errorMsg}</p>}
            <button 
              disabled={isLoading}
              className="w-full mt-6 bg-indigo-500 text-white py-3.5 rounded-xl font-medium flex items-center justify-center gap-2 hover:bg-indigo-600 transition-all disabled:opacity-50 disabled:cursor-wait shadow-[0_0_20px_rgba(99,102,241,0.2)]"
            >
              {isLoading ? (
                <><div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin mr-1" /> Analizando ADN...</>
              ) : (
                <>Extraer ADN Corporativo <Send className="w-4 h-4" /></>
              )}
            </button>
          </div>
        </form>
      ) : (
        <div className="animate-in zoom-in-95 duration-500 space-y-6">
          <div className="bg-[#111111]/80 backdrop-blur-xl rounded-2xl border border-white/5 p-8 text-center">
             <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-4">
               <Box className="w-8 h-8 text-indigo-400" />
             </div>
             <h3 className="text-2xl font-bold text-white mb-2">Cliente Registrado</h3>
             <p className="text-neutral-400">ID Asignado: <span className="text-white font-mono text-xl">{result.client.id}</span></p>
             <p className="text-xs text-neutral-500 mt-2">(Guarda este ID para crear proyectos en el Portal)</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
             <div className="p-6 rounded-2xl border border-white/5 bg-[#111111]/80">
               <PaintBucket className="w-6 h-6 text-purple-400 mb-3" />
               <h4 className="text-sm font-medium text-neutral-400 mb-2">Color Primario</h4>
               <div className="flex items-center gap-3">
                 <div className="w-8 h-8 rounded border border-white/20 shadow-inner" style={{ backgroundColor: result.guidelines.primary_color_hex }}></div>
                 <code className="text-white bg-black/50 px-2 py-1 rounded text-sm">{result.guidelines.primary_color_hex}</code>
               </div>
             </div>
             <div className="col-span-2 p-6 rounded-2xl border border-white/5 bg-[#111111]/80">
               <Briefcase className="w-6 h-6 text-emerald-400 mb-3" />
               <h4 className="text-sm font-medium text-neutral-400 mb-2">Tono de Voz</h4>
               <p className="text-white/90 text-sm leading-relaxed">{result.guidelines.tone_of_voice}</p>
             </div>
             <div className="col-span-3 p-6 rounded-2xl border border-white/5 bg-[#111111]/80">
               <Target className="w-6 h-6 text-amber-400 mb-3" />
               <h4 className="text-sm font-medium text-neutral-400 mb-2">Publico y Propuesta</h4>
               <p className="text-white/90 text-sm mb-3">Audience: {result.guidelines.target_audience}</p>
               <p className="text-white/90 text-sm">Value Prop: {result.guidelines.value_proposition}</p>
             </div>
          </div>
          <div className="text-center mt-10">
             <button onClick={() => router.push('/portal')} className="bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-neutral-200 transition-colors">
               Ir al Portal de Producción →
             </button>
          </div>
        </div>
      )}
    </div>
  );
}
