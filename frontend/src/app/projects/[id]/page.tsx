"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  Film,
  Trash2,
  Sparkles,
  Image as ImageIcon,
  Play,
  Download,
  X,
  Clock,
  Palette,
  FileText,
  ChevronDown,
  ChevronUp,
  Wand2,
  Loader2,
} from "lucide-react";
import Navbar from "@/components/ui/Navbar";
import GlowCard from "@/components/ui/GlowCard";
import ProgressBar from "@/components/ui/ProgressBar";

interface Project {
  id: string;
  title: string;
  description: string;
  status: string;
  original_script?: string;
  style?: string;
  duration_target?: number;
  created_at: string;
  updated_at?: string;
}

interface Scene {
  id: string;
  order: number;
  title: string;
  description: string;
  dialogue?: string;
  image_prompt: string;
  duration?: number;
  notes?: string;
  status: string;
  video_url?: string;
  video_status?: string;
  video_provider?: string;
}

interface Asset {
  id: string;
  scene_id: string;
  type: string;
  url: string;
  status: string;
  scene_order?: number;
  scene_title?: string;
  created_at: string;
}

const statusColors: Record<string, { bg: string; text: string }> = {
  draft: { bg: "bg-gray-500/20", text: "text-gray-400" },
  processing: { bg: "bg-amber-500/20", text: "text-amber-400" },
  scenes_ready: { bg: "bg-cyan-500/20", text: "text-cyan-400" },
  images_ready: { bg: "bg-fuchsia-500/20", text: "text-fuchsia-400" },
  completed: { bg: "bg-green-500/20", text: "text-green-400" },
  pending: { bg: "bg-gray-500/20", text: "text-gray-400" },
};

export default function ProjectDetailPage({
  params,
}: {
  params: { id: string };
}) {
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [scenes, setScenes] = useState<Scene[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [generatingImages, setGeneratingImages] = useState(false);
  const [animatingScenes, setAnimatingScenes] = useState(false);
  const [imageProvider, setImageProvider] = useState<"dalle" | "aimlapi" | "higgsfield" | "gemini">("gemini");
  const [videoProvider, setVideoProvider] = useState<"veo" | "kling" | "sora">("veo");
  const [selectedImage, setSelectedImage] = useState<Asset | null>(null);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [expandedScenes, setExpandedScenes] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadProject();
    loadScenes();
    loadAssets();
  }, [params.id]);

  const loadProject = () => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/${params.id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Proyecto no encontrado");
        return res.json();
      })
      .then((data) => {
        setProject(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  };

  const loadScenes = () => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/scenes/project/${params.id}`)
      .then((res) => res.json())
      .then((data) => setScenes(data))
      .catch((err) => console.error(err));
  };

  const loadAssets = () => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/scenes/project/${params.id}/assets`)
      .then((res) => res.json())
      .then((data) => setAssets(data))
      .catch((err) => console.error(err));
  };

  const handleAnalyzeScript = async () => {
    if (!project?.original_script) {
      alert("No hay guión para analizar");
      return;
    }

    setAnalyzing(true);
    setGenerationProgress(0);
    setProgressMessage("Analizando guión con IA...");

    try {
      const progressInterval = setInterval(() => {
        setGenerationProgress((prev) => Math.min(prev + 10, 90));
      }, 500);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/generation/analyze-script`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            project_id: params.id,
            script: project.original_script,
          }),
        }
      );

      clearInterval(progressInterval);
      setGenerationProgress(100);

      if (response.ok) {
        const result = await response.json();
        setProgressMessage(`✅ ${result.total_scenes} escenas creadas`);
        setTimeout(() => {
          loadProject();
          loadScenes();
          setGenerationProgress(0);
          setProgressMessage("");
        }, 1500);
      } else {
        const errorText = await response.text();
        let errorMsg = "No se pudo analizar el guión";
        try {
          const errorData = JSON.parse(errorText);
          errorMsg = errorData.detail || errorMsg;
        } catch {
          errorMsg = errorText || errorMsg;
        }
        alert(`Error: ${errorMsg}`);
        setGenerationProgress(0);
        setProgressMessage("");
      }
    } catch (error) {
      console.error("Analyze script error:", error);
      alert(`Error al analizar el guión: ${error instanceof Error ? error.message : "Error de conexión"}`);
      setGenerationProgress(0);
      setProgressMessage("");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleGenerateImages = async () => {
    if (scenes.length === 0) {
      alert("No hay escenas para generar imágenes");
      return;
    }

    setGeneratingImages(true);
    setGenerationProgress(0);
    setProgressMessage("Conectando con el servidor...");
    setGenerationError(null);

    try {
      // Usar SSE para progreso en tiempo real
      const eventSource = new EventSource(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/generation/generate-images-stream/${params.id}?provider=${imageProvider}`
      );

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
          case "start":
            setProgressMessage(data.message);
            setGenerationProgress(5);
            break;
            
          case "progress":
            // Calcular progreso real basado en la imagen actual
            const progressPercent = (data.current / data.total) * 85 + 5; // 5% a 90%
            setGenerationProgress(progressPercent);
            setProgressMessage(data.message);
            break;
            
          case "scene_complete":
            const completePercent = (data.scene / data.total) * 85 + 10;
            setGenerationProgress(completePercent);
            setProgressMessage(data.message);
            break;
            
          case "scene_error":
            setProgressMessage(`⚠️ ${data.message}`);
            // Si es un error de quota/créditos, mostrar error persistente
            if (data.error_code === "quota_exhausted" || data.error_code === "no_credits") {
              setGenerationError(data.message);
            }
            break;

          case "fatal_error":
            // Error fatal: quota agotada, sin créditos, etc.
            setGenerationError(data.message);
            setProgressMessage(data.message);
            eventSource.close();
            setTimeout(() => {
              loadProject();
              loadScenes();
              loadAssets();
              setGenerationProgress(0);
              setProgressMessage("");
              setGeneratingImages(false);
            }, 2000);
            break;
            
          case "complete":
            setGenerationProgress(100);
            setProgressMessage(data.message);
            if (data.generated === 0) {
              setGenerationError(`No se pudo generar ninguna imagen. Probá con otro proveedor.`);
            }
            eventSource.close();
            
            setTimeout(() => {
              loadProject();
              loadScenes();
              loadAssets();
              setGenerationProgress(0);
              setProgressMessage("");
              setGeneratingImages(false);
            }, 1500);
            break;
            
          case "error":
            setGenerationError(data.message);
            eventSource.close();
            setGenerationProgress(0);
            setProgressMessage("");
            setGeneratingImages(false);
            break;
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        // Si hubo progreso, probablemente terminó ok
        if (generationProgress > 50) {
          setGenerationProgress(100);
          setProgressMessage("✅ Generación completada");
          setTimeout(() => {
            loadProject();
            loadScenes();
            loadAssets();
            setGenerationProgress(0);
            setProgressMessage("");
            setGeneratingImages(false);
          }, 1500);
        } else {
          setGenerationError("Error de conexión con el servidor. Verificá que el backend esté corriendo.");
          setGenerationProgress(0);
          setProgressMessage("");
          setGeneratingImages(false);
        }
      };

    } catch (error) {
      console.error(error);
      alert("Error al generar las imágenes");
      setGenerationProgress(0);
      setProgressMessage("");
      setGeneratingImages(false);
    }
  };

  const handleAnimateScenes = async () => {
    if (imageAssets.length === 0) {
      alert("Primero debes generar las imágenes");
      return;
    }

    setAnimatingScenes(true);
    setGenerationProgress(0);
    const providerName = videoProvider === "veo" ? "Veo 3.1" : videoProvider === "kling" ? "Kling" : "Sora";
    setProgressMessage(`Iniciando animación con ${providerName}...`);

    try {
      // Llamar al endpoint de animación en batch
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/generation/animate-scenes/${params.id}?provider=${videoProvider}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (response.ok) {
        const result = await response.json();
        setProgressMessage(`✅ ${result.tasks?.length || 0} animaciones iniciadas`);
        
        // Polling para verificar progreso
        const pollInterval = setInterval(async () => {
          const statusResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/${params.id}`
          );
          
          if (statusResponse.ok) {
            const projectData = await statusResponse.json();
            
            // Verificar si todas las escenas tienen video
            const scenesWithVideo = scenes.filter(s => s.status === "video_ready").length;
            const progress = (scenesWithVideo / scenes.length) * 100;
            
            setGenerationProgress(progress);
            setProgressMessage(`Animando escenas: ${scenesWithVideo}/${scenes.length}`);
            
            if (scenesWithVideo === scenes.length || progress >= 100) {
              clearInterval(pollInterval);
              setGenerationProgress(100);
              setProgressMessage("✅ Todas las animaciones completadas");
              
              setTimeout(() => {
                loadProject();
                loadScenes();
                loadAssets();
                setGenerationProgress(0);
                setProgressMessage("");
                setAnimatingScenes(false);
              }, 2000);
            }
          }
        }, 10000); // Polling cada 10 segundos
        
        // Timeout de 10 minutos
        setTimeout(() => {
          clearInterval(pollInterval);
          setAnimatingScenes(false);
          setProgressMessage("⚠️ Tiempo de espera agotado. Revisa el estado manualmente.");
        }, 600000);
        
      } else {
        const error = await response.json();
        alert(`Error: ${error.detail || "No se pudieron animar las escenas"}`);
        setGenerationProgress(0);
        setProgressMessage("");
        setAnimatingScenes(false);
      }
    } catch (error) {
      console.error(error);
      alert("Error al animar las escenas");
      setGenerationProgress(0);
      setProgressMessage("");
      setAnimatingScenes(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("¿Estás seguro de eliminar este proyecto?")) return;

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/projects/${params.id}`,
        { method: "DELETE" }
      );
      if (response.ok) {
        router.push("/projects");
      } else {
        alert("Error al eliminar el proyecto");
      }
    } catch (error) {
      console.error(error);
      alert("Error al eliminar el proyecto");
    }
  };

  const handleDownloadImage = async (asset: Asset) => {
    try {
      const response = await fetch(asset.url);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `escena_${asset.scene_order}_${asset.scene_title || "imagen"}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading:", error);
      window.open(asset.url, "_blank");
    }
  };

  const toggleScene = (sceneId: string) => {
    setExpandedScenes((prev) => {
      const next = new Set(prev);
      if (next.has(sceneId)) {
        next.delete(sceneId);
      } else {
        next.add(sceneId);
      }
      return next;
    });
  };

  // Loading state
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
            <p className="text-gray-400 animate-pulse">Cargando proyecto...</p>
          </div>
        </div>
      </div>
    );
  }

  // Not found state
  if (!project) {
    return (
      <div className="min-h-screen bg-black">
        <Navbar />
        <div className="flex flex-col items-center justify-center min-h-screen gap-6">
          <Film className="h-16 w-16 text-gray-600" />
          <h1 className="text-2xl font-bold text-white">Proyecto no encontrado</h1>
          <button
            onClick={() => router.push("/projects")}
            className="text-violet-400 hover:text-violet-300"
          >
            ← Volver a proyectos
          </button>
        </div>
      </div>
    );
  }

  const status = statusColors[project.status] || statusColors.draft;
  const imageAssets = assets.filter((a) => a.type === "image");

  return (
    <div className="min-h-screen bg-black">
      <Navbar />

      {/* Progress Bar */}
      <AnimatePresence>
        {(analyzing || generatingImages) && generationProgress > 0 && (
          <ProgressBar progress={generationProgress} message={progressMessage} />
        )}
      </AnimatePresence>

      {/* Error Banner */}
      <AnimatePresence>
        {generationError && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-20 left-1/2 -translate-x-1/2 z-50 max-w-2xl w-full px-4"
          >
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 backdrop-blur-xl shadow-2xl">
              <div className="flex items-start gap-3">
                <div className="text-red-400 text-xl flex-shrink-0">⚠️</div>
                <div className="flex-1">
                  <p className="text-red-300 text-sm font-medium">Error de generación</p>
                  <p className="text-red-200/80 text-sm mt-1">{generationError}</p>
                </div>
                <button
                  onClick={() => setGenerationError(null)}
                  className="text-red-400 hover:text-red-300 flex-shrink-0"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Image Modal */}
      <AnimatePresence>
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/90 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="relative max-w-5xl"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                onClick={() => setSelectedImage(null)}
                className="absolute -top-12 right-0 text-gray-400 hover:text-white flex items-center gap-2"
              >
                <X className="h-5 w-5" /> Cerrar
              </button>
              <img
                src={selectedImage.url}
                alt={`Escena ${selectedImage.scene_order}`}
                className="max-w-full max-h-[85vh] object-contain rounded-xl"
              />
              <div className="absolute bottom-4 left-4 right-4 bg-black/80 backdrop-blur p-4 rounded-xl">
                <p className="font-semibold text-white mb-2">
                  Escena {selectedImage.scene_order}: {selectedImage.scene_title}
                </p>
                <button
                  onClick={() => handleDownloadImage(selectedImage)}
                  className="flex items-center gap-2 px-4 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg text-white"
                >
                  <Download className="h-4 w-4" /> Descargar
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Background */}
      <div className="fixed inset-0 bg-grid-pattern opacity-30 pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 pt-24 pb-12">
        {/* Back button */}
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => router.push("/projects")}
          className="flex items-center gap-2 text-gray-400 hover:text-white mb-8"
        >
          <ArrowLeft className="h-5 w-5" /> Volver a proyectos
        </motion.button>

        {/* Project Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <GlowCard>
            <div className="p-8">
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                <div className="flex items-start gap-4">
                  <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 p-4 rounded-xl">
                    <Film className="h-8 w-8 text-white" />
                  </div>
                  <div>
                    <h1 className="text-3xl font-bold text-white mb-2">{project.title}</h1>
                    <div className="flex flex-wrap items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-sm ${status.bg} ${status.text}`}>
                        {project.status}
                      </span>
                      {project.style && (
                        <span className="flex items-center gap-1 text-gray-400 text-sm">
                          <Palette className="h-4 w-4" /> {project.style}
                        </span>
                      )}
                      {project.duration_target && (
                        <span className="flex items-center gap-1 text-gray-400 text-sm">
                          <Clock className="h-4 w-4" /> {project.duration_target}s
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <button
                  onClick={handleDelete}
                  className="flex items-center gap-2 px-4 py-2 text-red-400 hover:bg-red-500/10 border border-red-500/30 rounded-lg"
                >
                  <Trash2 className="h-4 w-4" /> Eliminar
                </button>
              </div>

              <p className="text-gray-400 mt-6">{project.description}</p>

              {project.original_script && (
                <div className="mt-6 pt-6 border-t border-white/10">
                  <div className="flex items-center gap-2 text-gray-300 mb-3">
                    <FileText className="h-4 w-4" />
                    <span className="font-medium">Guión Original</span>
                  </div>
                  <div className="bg-black/50 border border-white/5 rounded-xl p-4 max-h-48 overflow-y-auto">
                    <pre className="text-gray-400 text-sm whitespace-pre-wrap font-mono">
                      {project.original_script}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </GlowCard>
        </motion.div>

        {/* Workflow Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-10"
        >
          <GlowCard glowColor="cyan">
            <div className="p-6">
              <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <Wand2 className="h-5 w-5 text-violet-400" /> Flujo de trabajo
              </h2>
              <div className="space-y-4">
                {/* Step 1 */}
                <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center">
                  <span className="w-8 h-8 flex items-center justify-center bg-violet-500/20 text-violet-400 rounded-full text-sm font-bold">
                    1
                  </span>
                  <button
                    onClick={handleAnalyzeScript}
                    disabled={analyzing || !project.original_script}
                    className="flex-1 relative group disabled:opacity-50"
                  >
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl blur opacity-50 group-hover:opacity-75" />
                    <span className="relative flex items-center justify-center gap-2 bg-gray-900 border border-white/10 text-white px-6 py-4 rounded-xl w-full">
                      {analyzing ? (
                        <><Loader2 className="h-5 w-5 animate-spin" /> Analizando...</>
                      ) : (
                        <>
                          <Sparkles className="h-5 w-5 text-violet-400" /> Analizar guión con IA
                          {scenes.length > 0 && (
                            <span className="ml-2 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                              ✓ {scenes.length} escenas
                            </span>
                          )}
                        </>
                      )}
                    </span>
                  </button>
                </div>

                {/* Step 2 */}
                <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center">
                  <span className="w-8 h-8 flex items-center justify-center bg-fuchsia-500/20 text-fuchsia-400 rounded-full text-sm font-bold">
                    2
                  </span>
                  <div className="flex-1 flex flex-col sm:flex-row gap-3">
                    <button
                      onClick={handleGenerateImages}
                      disabled={generatingImages || scenes.length === 0}
                      className="flex-1 relative group disabled:opacity-50"
                    >
                      <div className="absolute -inset-0.5 bg-gradient-to-r from-fuchsia-600 to-violet-600 rounded-xl blur opacity-50 group-hover:opacity-75" />
                      <span className="relative flex items-center justify-center gap-2 bg-gray-900 border border-white/10 text-white px-6 py-4 rounded-xl w-full">
                        {generatingImages ? (
                          <><Loader2 className="h-5 w-5 animate-spin" /> Generando...</>
                        ) : (
                          <>
                            <ImageIcon className="h-5 w-5 text-fuchsia-400" />
                            Generar imágenes {scenes.length > 0 && `(${scenes.length})`}
                            {imageAssets.length > 0 && (
                              <span className="ml-2 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                                ✓ {imageAssets.length}
                              </span>
                            )}
                          </>
                        )}
                      </span>
                    </button>
                    <select
                      value={imageProvider}
                      onChange={(e) => setImageProvider(e.target.value as typeof imageProvider)}
                      disabled={generatingImages}
                      className="px-4 py-4 bg-gray-900 border border-white/10 rounded-xl text-gray-300 focus:ring-2 focus:ring-violet-500/50"
                    >
                      <option value="gemini">Gemini</option>
                      <option value="dalle">DALL-E 2</option>
                      <option value="aimlapi">AIMLAPI</option>
                      <option value="higgsfield">Higgsfield</option>
                    </select>
                  </div>
                </div>

                {/* Step 3 - Animate scenes */}
                <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center">
                  <span className="w-8 h-8 flex items-center justify-center bg-cyan-500/20 text-cyan-400 rounded-full text-sm font-bold">
                    3
                  </span>
                  <div className="flex-1 flex flex-col sm:flex-row gap-3">
                    <button
                      onClick={handleAnimateScenes}
                      disabled={animatingScenes || imageAssets.length === 0}
                      className="flex-1 relative group disabled:opacity-50"
                    >
                      <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-xl blur opacity-50 group-hover:opacity-75" />
                      <span className="relative flex items-center justify-center gap-2 bg-gray-900 border border-white/10 text-white px-6 py-4 rounded-xl w-full">
                        {animatingScenes ? (
                          <><Loader2 className="h-5 w-5 animate-spin" /> Animando...</>
                        ) : (
                          <>
                            <Play className="h-5 w-5 text-cyan-400" />
                            Animar escenas con {videoProvider === "veo" ? "Veo 3.1" : videoProvider === "kling" ? "Kling" : "Sora"}
                          </>
                        )}
                      </span>
                    </button>
                    <select
                      value={videoProvider}
                      onChange={(e) => setVideoProvider(e.target.value as typeof videoProvider)}
                      disabled={animatingScenes}
                      className="px-4 py-4 bg-gray-900 border border-white/10 rounded-xl text-gray-300 focus:ring-2 focus:ring-cyan-500/50"
                    >
                      <option value="veo">Veo 3.1</option>
                      <option value="kling">Kling AI</option>
                      <option value="sora">Sora (OpenAI)</option>
                    </select>
                  </div>
                </div>

                {/* Step 4 - Coming soon */}
                <div className="flex flex-col md:flex-row gap-4 items-stretch md:items-center opacity-50">
                  <span className="w-8 h-8 flex items-center justify-center bg-green-500/20 text-green-400 rounded-full text-sm font-bold">
                    4
                  </span>
                  <button disabled className="flex-1 flex items-center justify-center gap-2 bg-gray-900/50 border border-white/5 text-gray-500 px-6 py-4 rounded-xl">
                    <Download className="h-5 w-5" /> Exportar video (próximamente)
                  </button>
                </div>
              </div>
            </div>
          </GlowCard>
        </motion.div>

        {/* Generated Images */}
        {imageAssets.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mb-10"
          >
            <GlowCard glowColor="violet">
              <div className="p-6">
                <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                  <ImageIcon className="h-5 w-5 text-fuchsia-400" />
                  Imágenes Generadas ({imageAssets.length})
                </h2>
                <p className="text-gray-400 text-sm mb-6">Click en una imagen para ver en grande</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {imageAssets.map((asset, index) => (
                    <motion.div
                      key={asset.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.05 }}
                      onClick={() => setSelectedImage(asset)}
                      className="relative group cursor-pointer overflow-hidden rounded-xl bg-gray-900 border border-white/10 hover:border-violet-500/50"
                    >
                      <div className="aspect-square">
                        <img
                          src={asset.url}
                          alt={`Escena ${asset.scene_order}`}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          onError={(e) => {
                            (e.target as HTMLImageElement).src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Crect fill='%23111' width='200' height='200'/%3E%3Ctext x='50%25' y='50%25' text-anchor='middle' fill='%23666'%3EError%3C/text%3E%3C/svg%3E";
                          }}
                        />
                      </div>
                      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                        <div className="absolute bottom-0 left-0 right-0 p-3">
                          <p className="text-white text-sm font-medium truncate">Escena {asset.scene_order}</p>
                          <p className="text-gray-400 text-xs truncate">{asset.scene_title}</p>
                        </div>
                      </div>
                      <div className="absolute top-2 left-2 px-2 py-1 bg-black/60 rounded text-xs text-white">
                        #{asset.scene_order}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </GlowCard>
          </motion.div>
        )}

        {/* Scenes List */}
        {scenes.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <GlowCard>
              <div className="p-6">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-cyan-400" />
                  Escenas ({scenes.length})
                </h2>
                <div className="space-y-3">
                  {scenes.map((scene, index) => {
                    const isExpanded = expandedScenes.has(scene.id);
                    const sceneStatus = statusColors[scene.status] || statusColors.pending;

                    return (
                      <motion.div
                        key={scene.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.03 }}
                        className="bg-black/50 border border-white/5 rounded-xl overflow-hidden"
                      >
                        <button
                          onClick={() => toggleScene(scene.id)}
                          className="w-full flex items-center justify-between p-4 hover:bg-white/5"
                        >
                          <div className="flex items-center gap-4">
                            <span className="w-8 h-8 flex items-center justify-center bg-violet-500/20 text-violet-400 rounded-lg text-sm font-bold">
                              {scene.order}
                            </span>
                            <div className="text-left">
                              <h3 className="text-white font-medium">{scene.title}</h3>
                              <p className="text-gray-500 text-sm truncate max-w-md">{scene.description}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {scene.duration && <span className="text-gray-500 text-sm">{scene.duration}s</span>}
                            <span className={`px-2 py-1 rounded-full text-xs ${sceneStatus.bg} ${sceneStatus.text}`}>
                              {scene.status}
                            </span>
                            {isExpanded ? <ChevronUp className="h-5 w-5 text-gray-400" /> : <ChevronDown className="h-5 w-5 text-gray-400" />}
                          </div>
                        </button>

                        <AnimatePresence>
                          {isExpanded && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="border-t border-white/5"
                            >
                              <div className="p-4 space-y-4">
                                {/* Video Player */}
                                {scene.video_url && scene.video_status === 'completed' && (
                                  <div className="bg-black/70 border border-cyan-500/30 rounded-lg p-3">
                                    <p className="text-sm text-cyan-400 mb-2 flex items-center gap-2">
                                      <Play className="h-4 w-4" />
                                      Video generado con {scene.video_provider || 'Veo 3.1'}:
                                    </p>
                                    <video
                                      controls
                                      className="w-full rounded-lg"
                                      src={scene.video_url}
                                    >
                                      Tu navegador no soporta el elemento de video.
                                    </video>
                                  </div>
                                )}

                                <p className="text-gray-400">{scene.description}</p>

                                {scene.dialogue && (
                                  <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3">
                                    <p className="text-sm text-gray-400 mb-1">Diálogo:</p>
                                    <p className="text-white italic">&ldquo;{scene.dialogue}&rdquo;</p>
                                  </div>
                                )}

                                <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-3">
                                  <p className="text-sm text-gray-400 mb-1">Prompt para imagen:</p>
                                  <p className="text-cyan-300 text-sm">{scene.image_prompt}</p>
                                </div>

                                {scene.notes && (
                                  <p className="text-gray-500 text-sm italic">Nota: {scene.notes}</p>
                                )}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </GlowCard>
          </motion.div>
        )}
      </div>
    </div>
  );
}
