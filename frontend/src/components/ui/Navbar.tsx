"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Film, Menu, X } from "lucide-react";
import { useState } from "react";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="fixed top-0 left-0 right-0 z-50 bg-black/80 backdrop-blur-xl border-b border-white/10"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-lg blur-sm group-hover:blur-md transition-all" />
              <div className="relative bg-black rounded-lg p-2">
                <Film className="h-6 w-6 text-white" />
              </div>
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              HeyAI
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link
              href="/projects"
              className="text-gray-300 hover:text-white transition-colors text-sm font-medium"
            >
              Proyectos
            </Link>
            <Link
              href="/projects/new"
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-lg blur-sm opacity-75 group-hover:opacity-100 transition-opacity" />
              <span className="relative bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white px-5 py-2 rounded-lg text-sm font-medium inline-block">
                Crear Proyecto
              </span>
            </Link>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-gray-300 hover:text-white"
          >
            {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden py-4 border-t border-white/10"
          >
            <div className="flex flex-col gap-4">
              <Link
                href="/projects"
                className="text-gray-300 hover:text-white transition-colors text-sm font-medium"
                onClick={() => setIsOpen(false)}
              >
                Proyectos
              </Link>
              <Link
                href="/projects/new"
                className="bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white px-5 py-2 rounded-lg text-sm font-medium text-center"
                onClick={() => setIsOpen(false)}
              >
                Crear Proyecto
              </Link>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
}
