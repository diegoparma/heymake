"use client";

import { motion } from "framer-motion";

interface ProgressBarProps {
  progress: number;
  message: string;
}

export default function ProgressBar({ progress, message }: ProgressBarProps) {
  return (
    <motion.div
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      exit={{ y: -100, opacity: 0 }}
      className="fixed top-16 left-0 right-0 z-40 bg-black/90 backdrop-blur-xl border-b border-white/10"
    >
      <div className="max-w-4xl mx-auto p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-300">{message}</span>
          <span className="text-sm font-bold bg-gradient-to-r from-violet-400 to-fuchsia-400 bg-clip-text text-transparent">
            {Math.round(progress)}%
          </span>
        </div>
        <div className="relative w-full h-2 bg-gray-800 rounded-full overflow-hidden">
          {/* Glow effect */}
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-violet-500 via-fuchsia-500 to-violet-500 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
          {/* Shine animation */}
          <div
            className="absolute top-0 left-0 h-full bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-full animate-pulse"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </motion.div>
  );
}
