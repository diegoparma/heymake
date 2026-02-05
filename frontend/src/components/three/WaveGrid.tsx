"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function AnimatedGrid() {
  const meshRef = useRef<THREE.Points>(null);
  
  const { positions, colors } = useMemo(() => {
    const size = 40;
    const segments = 40;
    const positions: number[] = [];
    const colors: number[] = [];
    
    for (let i = 0; i <= segments; i++) {
      for (let j = 0; j <= segments; j++) {
        const x = (i / segments - 0.5) * size;
        const z = (j / segments - 0.5) * size;
        positions.push(x, 0, z);
        
        // Gradient color from purple to cyan
        const t = i / segments;
        colors.push(
          0.55 + t * 0.1,  // R
          0.36 - t * 0.2,  // G
          0.96 - t * 0.3   // B
        );
      }
    }
    
    return { 
      positions: new Float32Array(positions), 
      colors: new Float32Array(colors) 
    };
  }, []);

  useFrame((state) => {
    if (meshRef.current) {
      const positionAttribute = meshRef.current.geometry.getAttribute('position');
      const time = state.clock.elapsedTime;
      
      for (let i = 0; i < positionAttribute.count; i++) {
        const x = positionAttribute.getX(i);
        const z = positionAttribute.getZ(i);
        const y = Math.sin(x * 0.3 + time) * 0.5 + Math.cos(z * 0.3 + time) * 0.5;
        positionAttribute.setY(i, y);
      }
      
      positionAttribute.needsUpdate = true;
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={positions.length / 3}
          array={positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={colors.length / 3}
          array={colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        vertexColors
        transparent
        opacity={0.8}
        sizeAttenuation
      />
    </points>
  );
}

export default function WaveGrid() {
  return (
    <div className="absolute inset-0 z-0 opacity-40">
      <Canvas camera={{ position: [0, 15, 25], fov: 60 }}>
        <ambientLight intensity={0.5} />
        <AnimatedGrid />
      </Canvas>
    </div>
  );
}
