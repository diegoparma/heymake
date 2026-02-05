"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";

interface GlowCardProps {
  children: ReactNode;
  className?: string;
  glowColor?: string;
  onClick?: () => void;
}

export default function GlowCard({
  children,
  className = "",
  glowColor = "violet",
  onClick,
}: GlowCardProps) {
  const gradients: Record<string, string> = {
    violet: "from-violet-500/20 via-fuchsia-500/20 to-purple-500/20",
    cyan: "from-cyan-500/20 via-blue-500/20 to-indigo-500/20",
    green: "from-green-500/20 via-emerald-500/20 to-teal-500/20",
    orange: "from-orange-500/20 via-amber-500/20 to-yellow-500/20",
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -4 }}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      onClick={onClick}
      className={`relative group ${onClick ? "cursor-pointer" : ""} ${className}`}
    >
      {/* Glow effect */}
      <div
        className={`absolute -inset-0.5 bg-gradient-to-r ${gradients[glowColor]} rounded-xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500`}
      />
      
      {/* Card content */}
      <div className="relative bg-gray-900/80 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
        {/* Top gradient line */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        
        {children}
      </div>
    </motion.div>
  );
}
