"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Film, Sparkles, Clock, Palette } from "lucide-react";
import Navbar from "@/components/ui/Navbar";

export default function NewProjectPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    original_script: "",
    style: "",
    reference_prompt: "",
    duration_target: 60,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      if (response.ok) {
        const project = await response.json();
        router.push(`/projects/${project.id}`);
      } else {
        alert("Error al crear el proyecto");
      }
    } catch (error) {
      console.error(error);
      alert("Error al crear el proyecto");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <Navbar />

      {/* Background */}
      <div className="fixed inset-0 bg-grid-pattern opacity-30 pointer-events-none" />
      <div className="fixed inset-0 bg-radial-gradient pointer-events-none" />

      <div className="relative z-10 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12">
        {/* Back button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => router.push("/projects")}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-8"
        >
          <ArrowLeft className="h-5 w-5" />
          Volver a proyectos
        </motion.button>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10"
        >
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-violet-500/30 rounded-xl blur-lg" />
              <div className="relative bg-gradient-to-r from-violet-600 to-fuchsia-600 p-3 rounded-xl">
                <Film className="h-8 w-8 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-4xl font-bold text-white">Nuevo Proyecto</h1>
              <p className="text-gray-400">Crea un nuevo trailer con IA</p>
            </div>
          </div>
        </motion.div>

        {/* Form */}
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          onSubmit={handleSubmit}
          className="space-y-8"
        >
          {/* Card container */}
          <div className="bg-gray-900/80 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
            <div className="space-y-6">
              {/* Title */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-3">
                  <Sparkles className="h-4 w-4 text-violet-400" />
                  Título del proyecto *
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) =>
                    setFormData({ ...formData, title: e.target.value })
                  }
                  className="input-dark"
                  placeholder="Ej: Trailer película de ciencia ficción"
                />
              </div>

              {/* Description */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-3">
                  Descripción *
                </label>
                <textarea
                  required
                  value={formData.description}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                  className="input-dark resize-none"
                  rows={3}
                  placeholder="Describe brevemente de qué trata el proyecto"
                />
              </div>

              {/* Script */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-3">
                  Guión / Idea
                </label>
                <textarea
                  value={formData.original_script}
                  onChange={(e) =>
                    setFormData({ ...formData, original_script: e.target.value })
                  }
                  className="input-dark resize-none font-mono text-sm"
                  rows={10}
                  placeholder="Escribe aquí tu idea o guión completo. La IA lo analizará y dividirá en escenas visuales..."
                />
                <p className="mt-2 text-xs text-gray-500">
                  💡 Mientras más detallado sea el guión, mejores serán las escenas generadas
                </p>
              </div>

              {/* Style & Duration row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Style */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-3">
                    <Palette className="h-4 w-4 text-fuchsia-400" />
                    Estilo visual
                  </label>
                  <input
                    type="text"
                    value={formData.style}
                    onChange={(e) =>
                      setFormData({ ...formData, style: e.target.value })
                    }
                    className="input-dark"
                    placeholder="Cinematográfico, anime, realista..."
                  />
                </div>

                {/* Duration */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-3">
                    <Clock className="h-4 w-4 text-cyan-400" />
                    Duración objetivo (segundos)
                  </label>
                  <input
                    type="number"
                    value={formData.duration_target}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        duration_target: parseInt(e.target.value),
                      })
                    }
                    className="input-dark"
                    min={10}
                    max={300}
                  />
                </div>
              </div>

              {/* Reference Prompt - Full width */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-gray-300 mb-3">
                  <Sparkles className="h-4 w-4 text-amber-400" />
                  Prompt de referencia
                </label>
                <textarea
                  value={formData.reference_prompt}
                  onChange={(e) =>
                    setFormData({ ...formData, reference_prompt: e.target.value })
                  }
                  className="input-dark resize-none text-sm"
                  rows={4}
                  placeholder="Describe elementos visuales, ambientación, o estética que debe aplicarse a todas las imágenes generadas. Ej: 'Iluminación cálida, tonos dorados, ambiente nostálgico de los años 80'"
                />
                <p className="mt-2 text-xs text-gray-500">
                  ✨ Este prompt se aplicará a todas las imágenes y videos generados
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              type="button"
              onClick={() => router.push("/projects")}
              className="flex-1 sm:flex-none px-8 py-4 bg-white/5 border border-white/10 text-white font-medium rounded-xl hover:bg-white/10 transition-colors"
            >
              Cancelar
            </button>
            <motion.button
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: loading ? 1 : 0.98 }}
              type="submit"
              disabled={loading}
              className="flex-1 relative group"
            >
              <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl blur opacity-70 group-hover:opacity-100 transition-opacity" />
              <span className="relative flex items-center justify-center gap-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white px-8 py-4 rounded-xl font-semibold">
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Creando proyecto...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Crear Proyecto
                  </>
                )}
              </span>
            </motion.button>
          </div>
        </motion.form>
      </div>
    </div>
  );
}
