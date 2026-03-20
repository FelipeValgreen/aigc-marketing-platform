"use client";
import React, { useState, useRef } from "react";
import { UploadCloud, CheckCircle2, ChevronRight, Wand2, Music, Film, ChevronLeft, UserCircle2 } from "lucide-react";
import { api } from "@/lib/api";

export default function ProjectForm({ onSuccess }: { onSuccess: (data: any) => void }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  
  const [data, setData] = useState({
    clientId: "",
    productName: "",
    productDesc: "",
    angle: "Hard Selling",
    music: "Corporativo (Serio)",
    avatarId: "sofia",
  });
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    const formData = new FormData();
    formData.append("client_id", data.clientId);
    formData.append("product_name", data.productName);
    formData.append("product_desc", data.productDesc);
    formData.append("video_angle", data.angle);
    formData.append("music_style", data.music);
    formData.append("avatar_id", data.avatarId);
    if (file) formData.append("custom_media", file);

    try {
      const res = await api.post("/clients/projects", formData);
      onSuccess(res.data);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "System Error. Verify Backend API Connection.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-[#18181b]/50 backdrop-blur-3xl border border-[#27272a] rounded-3xl p-8 lg:p-10 relative overflow-hidden shadow-2xl">
      <div className="absolute -top-32 -right-32 w-64 h-64 bg-purple-500/10 blur-[100px] rounded-full pointer-events-none" />

      <div className="w-full flex gap-2 mb-10 relative z-10">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className={`h-1.5 flex-1 rounded-full transition-all duration-700 ${step >= i ? 'bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]' : 'bg-[#27272a]'}`} />
        ))}
      </div>

      {errorMsg && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm font-medium animate-in fade-in">
          {errorMsg}
        </div>
      )}

      {step === 1 && (
        <div className="animate-in slide-in-from-right-8 fade-in flex flex-col h-full duration-500 relative z-10">
          <h3 className="text-2xl font-bold text-white tracking-tight mb-2">Marca & Producto</h3>
          <p className="text-neutral-400 text-sm mb-8">Paso 1: Asociaremos el guion a la identidad de tu empresa mediante IA.</p>
          <div className="space-y-5">
            <div>
              <label className="text-[11px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5 block">Client ID</label>
              <input type="number" required placeholder="Ingresa ID numérico (Ej: 1)" value={data.clientId} onChange={e => setData({...data, clientId: e.target.value})} className="w-full bg-[#09090b] border border-[#27272a] rounded-xl px-5 py-3.5 text-white focus:border-indigo-500 outline-none transition-all placeholder:text-neutral-700" />
            </div>
            <div>
              <label className="text-[11px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5 block">Producto / Servicio</label>
              <input type="text" required placeholder="Ej: Pastelones de Hormiglass" value={data.productName} onChange={e => setData({...data, productName: e.target.value})} className="w-full bg-[#09090b] border border-[#27272a] rounded-xl px-5 py-3.5 text-white focus:border-indigo-500 outline-none transition-all placeholder:text-neutral-700" />
            </div>
            <button type="button" onClick={nextStep} disabled={!data.clientId || !data.productName} className="w-full mt-4 bg-white text-black font-semibold py-4 rounded-xl flex items-center justify-center gap-2 hover:bg-neutral-200 transition-all disabled:opacity-50">Siguiente <ChevronRight className="w-4 h-4" /></button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="animate-in slide-in-from-right-8 fade-in duration-500 relative z-10">
          <h3 className="text-2xl font-bold text-white tracking-tight mb-2">Dirección Creativa</h3>
          <p className="text-neutral-400 text-sm mb-8">Paso 2: Describe el contexto y elige el formato directivo.</p>
          <div className="space-y-5">
            <div>
              <label className="text-[11px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5 block">Contexto y Propuesta</label>
              <textarea required rows={4} placeholder="Describe los beneficios clave..." value={data.productDesc} onChange={e => setData({...data, productDesc: e.target.value})} className="w-full bg-[#09090b] border border-[#27272a] rounded-xl px-5 py-3.5 text-white focus:border-indigo-500 outline-none transition-all resize-none placeholder:text-neutral-700" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-[11px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5 flex items-center gap-1.5"><Wand2 className="w-3 h-3 text-purple-500"/> Ángulo</label>
                <select value={data.angle} onChange={e => setData({...data, angle: e.target.value})} className="w-full appearance-none bg-[#09090b] border border-[#27272a] rounded-xl px-4 py-3.5 text-white focus:border-indigo-500 outline-none">
                  <option>Hard Selling</option>
                  <option>UGC Tradicional</option>
                  <option>Storytelling</option>
                </select>
              </div>
              <div>
                <label className="text-[11px] font-bold uppercase tracking-widest text-neutral-500 mb-1.5 flex items-center gap-1.5"><Music className="w-3 h-3 text-emerald-500"/> Música (Ducking)</label>
                <select value={data.music} onChange={e => setData({...data, music: e.target.value})} className="w-full appearance-none bg-[#09090b] border border-[#27272a] rounded-xl px-4 py-3.5 text-white focus:border-indigo-500 outline-none">
                  <option>Corporativo (Serio)</option>
                  <option>Upbeat (Dinámico)</option>
                  <option>Lo-Fi (Relajado)</option>
                  <option>Sin Música</option>
                </select>
              </div>
            </div>
            <div className="flex gap-3 pt-4">
              <button type="button" onClick={prevStep} className="px-5 bg-[#09090b] border border-[#27272a] text-white font-medium py-4 rounded-xl hover:bg-[#18181b] transition-all"><ChevronLeft className="w-5 h-5" /></button>
              <button type="button" onClick={nextStep} disabled={!data.productDesc} className="flex-1 bg-white text-black font-semibold py-4 rounded-xl flex items-center justify-center gap-2 hover:bg-neutral-200 transition-all disabled:opacity-50">Siguiente <ChevronRight className="w-4 h-4" /></button>
            </div>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="animate-in slide-in-from-right-8 fade-in duration-500 relative z-10">
          <h3 className="text-2xl font-bold text-white tracking-tight mb-2">Talent Selector</h3>
          <p className="text-neutral-400 text-sm mb-8">Paso 3: Elige a tu Avatar UGC hiperrealista generado por IA.</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <AvatarOption id="sofia" name="Sofía" desc="Acento Chileno - Casual" active={data.avatarId === 'sofia'} onSelect={() => setData({...data, avatarId: 'sofia'})} />
            <AvatarOption id="mateo" name="Mateo" desc="Acento Neutro - Corporativo" active={data.avatarId === 'mateo'} onSelect={() => setData({...data, avatarId: 'mateo'})} />
            <AvatarOption id="elena" name="Elena" desc="Acento Español - Energética" active={data.avatarId === 'elena'} onSelect={() => setData({...data, avatarId: 'elena'})} />
          </div>
          <div className="flex gap-3 pt-4">
             <button type="button" onClick={prevStep} className="px-5 bg-[#09090b] border border-[#27272a] text-white font-medium py-4 rounded-xl hover:bg-[#18181b] transition-all"><ChevronLeft className="w-5 h-5" /></button>
             <button type="button" onClick={nextStep} className="flex-1 bg-white text-black font-semibold py-4 rounded-xl flex items-center justify-center gap-2 hover:bg-neutral-200 transition-all disabled:opacity-50">Siguiente <ChevronRight className="w-4 h-4" /></button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="animate-in slide-in-from-right-8 fade-in duration-500 relative z-10">
          <h3 className="text-2xl font-bold text-white tracking-tight mb-2">Pipeline de Medios</h3>
          <p className="text-neutral-400 text-sm mb-8">Paso final: Adjunta el B-Roll en crudo que la API integrará con tu Avatar.</p>
          <div className="space-y-6">
            <div 
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 ${file ? 'border-indigo-500/50 bg-indigo-500/5' : 'border-dashed border-[#27272a] hover:border-indigo-500/50 hover:bg-indigo-500/5'} rounded-2xl p-12 text-center transition-all cursor-pointer block group`}
            >
              <input 
                ref={fileInputRef} 
                id="file-upload" 
                type="file" 
                accept="*/*" 
                className="hidden" 
                onChange={e => {
                  if (e.target.files && e.target.files.length > 0) setFile(e.target.files[0]);
                }} 
              />
              {file ? (
                <div className="animate-in zoom-in-95 duration-300">
                  <CheckCircle2 className="w-12 h-12 text-indigo-400 mx-auto mb-3" />
                  <p className="text-indigo-400 font-medium">B-Roll Adjuntado a API</p>
                  <p className="text-indigo-400/60 text-xs mt-1 truncate max-w-[200px] mx-auto">{file.name}</p>
                </div>
              ) : (
                <div>
                  <UploadCloud className="w-10 h-10 text-neutral-600 group-hover:text-indigo-400 mx-auto mb-4 transition-colors" />
                  <p className="text-neutral-300 font-semibold mb-1">Arrastre o haga clic para subir.</p>
                  <p className="text-neutral-500 text-xs">Archivos de referencias visuales o B-Roll</p>
                </div>
              )}
            </div>
            <div className="flex gap-3 pt-2">
              <button type="button" onClick={prevStep} disabled={loading} className="px-5 bg-[#09090b] border border-[#27272a] text-white font-medium py-4 rounded-xl hover:bg-[#18181b] transition-all disabled:opacity-50"><ChevronLeft className="w-5 h-5" /></button>
              <button type="submit" disabled={loading} className="flex-1 bg-indigo-500 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 hover:bg-indigo-400 transition-all disabled:opacity-50 shadow-[0_0_20px_rgba(99,102,241,0.25)] relative overflow-hidden group">
                <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 pointer-events-none" />
                {loading ? <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" /> : <><Wand2 className="w-4 h-4" /> Desplegar Motor de IA</>}
              </button>
            </div>
          </div>
        </div>
      )}
    </form>
  );
}

function AvatarOption({ id, name, desc, active, onSelect }: any) {
  return (
    <div onClick={onSelect} className={`p-5 rounded-2xl border cursor-pointer transition-all ${active ? 'border-indigo-500 bg-indigo-500/10 shadow-[0_0_20px_rgba(99,102,241,0.2)]' : 'border-[#27272a] bg-[#09090b] hover:border-indigo-500/50'}`}>
      <div className={`w-12 h-12 rounded-full mb-3 flex items-center justify-center ${active ? 'bg-indigo-500/20 text-indigo-400' : 'bg-[#27272a] text-neutral-400'}`}>
        <UserCircle2 className="w-6 h-6" />
      </div>
      <h4 className={`font-bold ${active ? 'text-white' : 'text-neutral-300'}`}>{name}</h4>
      <p className="text-xs text-neutral-500 mt-1">{desc}</p>
    </div>
  );
}
