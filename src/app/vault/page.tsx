"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { PlaySquare, FolderOpen } from "lucide-react";

export default function Vault() {
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api.get("/projects")
      .then(res => setProjects(res.data.filter((p: any) => p.status === 'COMPLETADO')))
      .catch((err) => console.error(err))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="animate-in fade-in duration-500">
      <header className="mb-10">
        <h2 className="text-3xl font-semibold tracking-tight text-white mb-2">Bóveda de Contenidos</h2>
        <p className="text-neutral-400">Todos los recursos masterizados y aprobados listos para plataformas Pauta.</p>
      </header>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-8 h-8 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
        </div>
      ) : projects.length === 0 ? (
        <div className="border border-white/5 rounded-2xl bg-[#111111]/80 p-20 text-center">
          <FolderOpen className="w-12 h-12 mx-auto text-neutral-600 mb-4" />
          <h3 className="text-xl font-medium text-white mb-2">La Bóveda está vacía</h3>
          <p className="text-neutral-500">Renderiza tu primer video desde el Portal de Producción.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((p: any) => (
            <div key={p.id} className="border border-white/5 rounded-2xl bg-[#111111]/80 backdrop-blur-xl overflow-hidden group hover:border-indigo-500/30 transition-all">
              <div className="aspect-[9/16] w-full bg-black relative">
                {p.video_url ? (
                  <video src={p.video_url} controls className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity" />
                ) : (
                  <div className="flex items-center justify-center h-full"><PlaySquare className="w-8 h-8 text-neutral-700" /></div>
                )}
                <div className="absolute top-4 left-4">
                  <span className="px-2 py-1 bg-black/60 backdrop-blur-md rounded text-xs border border-white/10 text-white font-medium">#{p.id}</span>
                </div>
              </div>
              <div className="p-5">
                <h4 className="text-white font-medium mb-1 truncate">{p.product_name}</h4>
                <p className="text-sm text-neutral-500 flex justify-between">
                  <span>{p.video_angle}</span>
                  <a href={p.video_url} target="_blank" rel="noreferrer" className="text-indigo-400 hover:text-indigo-300">Descargar</a>
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
