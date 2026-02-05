"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Plus, Film, Calendar, ArrowRight, Sparkles } from "lucide-react";
import Navbar from "@/components/ui/Navbar";
import GlowCard from "@/components/ui/GlowCard";

interface Project {
  id: string;
  title: string;
  description: string;
  status: string;
  created_at: string;
}

const statusColors: Record<string, { bg: string; text: string; glow: string }> = {
  draft: { bg: "bg-gray-500/20", text: "text-gray-400", glow: "violet" },
  processing: { bg: "bg-amber-500/20", text: "text-amber-400", glow: "orange" },
  scenes_ready: { bg: "bg-cyan-500/20", text: "text-cyan-400", glow: "cyan" },
  images_ready: { bg: "bg-fuchsia-500/20", text: "text-fuchsia-400", glow: "violet" },
  completed: { bg: "bg-green-500/20", text: "text-green-400", glow: "green" },
};

const statusLabels: Record<string, string> = {
  draft: "Borrador",
  processing: "Procesando",
  scenes_ready: "Escenas listas",
  images_ready: "Imágenes listas",
  completed: "Completado",
};

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/`)
      .then((res) => res.json())
      .then((data) => {
        setProjects(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black">
        <Navbar />
        <div className="flex items-center justify-center min-h-screen">
          <div className="flex flex-col items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 border-4 border-violet-500/30 rounded-full animate-spin border-t-violet-500" />
              <div className="absolute inset-0 flex items-center justify-center">
                <Film className="h-6 w-6 text-violet-400" />
              </div>
            </div>
            <p className="text-gray-400 animate-pulse">Cargando proyectos...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      <Navbar />
      
      {/* Background */}
      <div className="fixed inset-0 bg-grid-pattern opacity-30 pointer-events-none" />
      <div className="fixed inset-0 bg-gradient-to-b from-black via-transparent to-black pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12"
        >
          <div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">Proyectos</h1>
            <p className="text-gray-400">
              {projects.length > 0
                ? `${projects.length} proyecto${projects.length > 1 ? "s" : ""} creado${projects.length > 1 ? "s" : ""}`
                : "Comienza creando tu primer proyecto"}
            </p>
          </div>
          <Link href="/projects/new" className="group">
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="relative"
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl blur opacity-70 group-hover:opacity-100 transition-opacity" />
              <span className="relative flex items-center gap-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white px-6 py-3 rounded-xl font-semibold">
                <Plus className="h-5 w-5" />
                Nuevo Proyecto
              </span>
            </motion.div>
          </Link>
        </motion.div>

        {projects.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-24"
          >
            <div className="relative inline-block mb-8">
              <div className="absolute inset-0 bg-violet-500/20 rounded-full blur-3xl" />
              <div className="relative bg-gray-900/50 border border-white/10 rounded-full p-8">
                <Film className="h-16 w-16 text-violet-400" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">No hay proyectos aún</h2>
            <p className="text-gray-400 mb-8 max-w-md mx-auto">
              Crea tu primer proyecto y comienza a generar trailers cinematográficos con IA
            </p>
            <Link
              href="/projects/new"
              className="inline-flex items-center gap-2 text-violet-400 hover:text-violet-300 transition-colors font-medium"
            >
              <Sparkles className="h-5 w-5" />
              Crear tu primer proyecto
              <ArrowRight className="h-5 w-5" />
            </Link>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project, index) => {
              const status = statusColors[project.status] || statusColors.draft;
              return (
                <motion.div
                  key={project.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <Link href={`/projects/${project.id}`}>
                    <GlowCard glowColor={status.glow}>
                      <div className="p-6">
                        {/* Header */}
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <div className="bg-violet-500/10 p-2 rounded-lg">
                              <Film className="h-5 w-5 text-violet-400" />
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${status.bg} ${status.text}`}>
                              {statusLabels[project.status] || project.status}
                            </span>
                          </div>
                        </div>

                        {/* Title */}
                        <h2 className="text-xl font-bold text-white mb-2 line-clamp-1 group-hover:text-violet-400 transition-colors">
                          {project.title}
                        </h2>

                        {/* Description */}
                        <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                          {project.description}
                        </p>

                        {/* Footer */}
                        <div className="flex items-center justify-between pt-4 border-t border-white/5">
                          <div className="flex items-center gap-2 text-gray-500 text-sm">
                            <Calendar className="h-4 w-4" />
                            {new Date(project.created_at).toLocaleDateString("es-ES", {
                              day: "numeric",
                              month: "short",
                              year: "numeric",
                            })}
                          </div>
                          <ArrowRight className="h-5 w-5 text-gray-500 group-hover:text-violet-400 group-hover:translate-x-1 transition-all" />
                        </div>
                      </div>
                    </GlowCard>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
