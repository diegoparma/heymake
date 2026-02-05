"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import { Film, Sparkles, Zap, Play, ArrowRight, Wand2, Video, ImageIcon } from "lucide-react";
import Navbar from "@/components/ui/Navbar";
import GlowCard from "@/components/ui/GlowCard";

// Cargar Three.js dinámicamente para evitar errores de SSR
const ParticleField = dynamic(() => import("@/components/three/ParticleField"), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-black" />,
});

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 },
};

const stagger = {
  visible: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export default function Home() {
  return (
    <main className="min-h-screen bg-black overflow-hidden">
      <Navbar />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center">
        {/* Three.js Background */}
        <ParticleField />

        {/* Gradient overlays */}
        <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black z-10" />
        <div className="absolute inset-0 bg-radial-gradient z-10" />

        {/* Content */}
        <div className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="text-center"
          >
            {/* Badge */}
            <motion.div variants={fadeInUp} className="mb-8">
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400 text-sm font-medium">
                <Sparkles className="h-4 w-4" />
                Powered by AI
              </span>
            </motion.div>

            {/* Main heading */}
            <motion.h1
              variants={fadeInUp}
              className="text-5xl md:text-7xl lg:text-8xl font-bold mb-6 leading-tight"
            >
              <span className="text-white">Crea Trailers con</span>
              <br />
              <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent animate-gradient bg-[length:200%_auto]">
                Inteligencia Artificial
              </span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              variants={fadeInUp}
              className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto leading-relaxed"
            >
              Transforma tus ideas y guiones en{" "}
              <span className="text-white font-medium">trailers cinematográficos</span>{" "}
              profesionales usando el poder de la IA generativa
            </motion.p>

            {/* CTAs */}
            <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/projects/new" className="group relative">
                <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl blur opacity-70 group-hover:opacity-100 transition-opacity" />
                <span className="relative flex items-center justify-center gap-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white px-8 py-4 rounded-xl font-semibold text-lg">
                  <Play className="h-5 w-5" />
                  Crear Proyecto
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </span>
              </Link>
              <Link
                href="/projects"
                className="flex items-center justify-center gap-2 bg-white/5 border border-white/10 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:bg-white/10 transition-colors"
              >
                Ver Proyectos
              </Link>
            </motion.div>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2 z-20"
        >
          <div className="flex flex-col items-center gap-2 text-gray-500">
            <span className="text-sm">Scroll</span>
            <div className="w-6 h-10 border-2 border-gray-600 rounded-full flex justify-center pt-2">
              <motion.div
                animate={{ y: [0, 12, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-1.5 h-1.5 bg-violet-500 rounded-full"
              />
            </div>
          </div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="relative py-32 bg-black">
        <div className="absolute inset-0 bg-grid-pattern opacity-30" />
        <div className="absolute inset-0 bg-gradient-to-b from-black via-transparent to-black" />

        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              ¿Cómo funciona?
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Un flujo simple de 3 pasos para crear contenido cinematográfico
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: <Wand2 className="h-8 w-8" />,
                title: "Análisis con IA",
                description:
                  "Nuestros LLMs analizan tu guión y lo dividen en escenas visuales detalladas con prompts optimizados",
                color: "violet",
                step: "01",
              },
              {
                icon: <ImageIcon className="h-8 w-8" />,
                title: "Generación de Imágenes",
                description:
                  "Modelos como DALL-E, Gemini y Flux generan imágenes cinematográficas para cada escena",
                color: "fuchsia",
                step: "02",
              },
              {
                icon: <Video className="h-8 w-8" />,
                title: "Animación & Video",
                description:
                  "Kling AI anima las imágenes con movimiento natural y efectos cinematográficos",
                color: "purple",
                step: "03",
              },
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <GlowCard glowColor={feature.color}>
                  <div className="p-8">
                    {/* Step number */}
                    <div className="absolute top-4 right-4 text-6xl font-bold text-white/5">
                      {feature.step}
                    </div>

                    {/* Icon */}
                    <div className={`inline-flex p-4 rounded-2xl bg-${feature.color}-500/10 text-${feature.color}-400 mb-6`}>
                      <div className="relative">
                        <div className={`absolute inset-0 bg-${feature.color}-500/30 rounded-full blur-lg`} />
                        <div className="relative text-violet-400">
                          {feature.icon}
                        </div>
                      </div>
                    </div>

                    {/* Content */}
                    <h3 className="text-xl font-bold text-white mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-gray-400 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </GlowCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-32 overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 animate-gradient bg-[length:200%_auto]" />
          <div className="absolute inset-0 bg-black/80" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              ¿Listo para crear?
            </h2>
            <p className="text-xl text-gray-400 mb-10">
              Empieza a crear trailers profesionales con solo una idea
            </p>
            <Link href="/projects/new" className="group inline-flex">
              <span className="relative flex items-center gap-2 bg-white text-black px-10 py-5 rounded-xl font-bold text-lg hover:bg-gray-100 transition-colors">
                <Film className="h-6 w-6" />
                Comenzar Ahora
                <Zap className="h-5 w-5 text-violet-600" />
              </span>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-12 bg-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 p-2 rounded-lg">
                <Film className="h-5 w-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white">HeyAI</span>
            </div>
            <p className="text-gray-500 text-sm">
              © 2026 HeyAI. Creado con IA generativa.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}
