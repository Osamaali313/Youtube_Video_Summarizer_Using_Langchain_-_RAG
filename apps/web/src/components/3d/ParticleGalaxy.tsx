'use client';

import { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { createNoise3D } from 'simplex-noise';

function ParticleField() {
  const ref = useRef<THREE.Points>(null!);
  const noise3D = useMemo(() => createNoise3D(), []);

  // Generate particle positions
  const [positions, colors] = useMemo(() => {
    const positions = new Float32Array(5000 * 3);
    const colors = new Float32Array(5000 * 3);

    for (let i = 0; i < 5000; i++) {
      // Create spiral galaxy shape
      const radius = Math.random() * 25;
      const spinAngle = radius * 0.5;
      const branchAngle = ((i % 3) / 3) * Math.PI * 2;

      const randomX = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3;
      const randomY = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3;
      const randomZ = Math.pow(Math.random(), 3) * (Math.random() < 0.5 ? 1 : -1) * 0.3;

      positions[i * 3] = Math.cos(branchAngle + spinAngle) * radius + randomX;
      positions[i * 3 + 1] = randomY;
      positions[i * 3 + 2] = Math.sin(branchAngle + spinAngle) * radius + randomZ;

      // Color gradient from blue to purple to cyan
      const mixedColor = new THREE.Color();
      const innerColor = new THREE.Color('#6366f1'); // Blue
      const middleColor = new THREE.Color('#ec4899'); // Pink
      const outerColor = new THREE.Color('#14b8a6'); // Cyan

      if (radius < 10) {
        mixedColor.lerpColors(innerColor, middleColor, radius / 10);
      } else {
        mixedColor.lerpColors(middleColor, outerColor, (radius - 10) / 15);
      }

      colors[i * 3] = mixedColor.r;
      colors[i * 3 + 1] = mixedColor.g;
      colors[i * 3 + 2] = mixedColor.b;
    }

    return [positions, colors];
  }, []);

  // Animate particles
  useFrame((state) => {
    const time = state.clock.getElapsedTime();

    if (ref.current) {
      ref.current.rotation.y = time * 0.05;

      const positions = ref.current.geometry.attributes.position.array as Float32Array;

      for (let i = 0; i < positions.length; i += 3) {
        const x = positions[i];
        const y = positions[i + 1];
        const z = positions[i + 2];

        // Add wave motion using noise
        const noiseValue = noise3D(x * 0.1, y * 0.1, time * 0.2);
        positions[i + 1] = y + Math.sin(time + x) * 0.01 + noiseValue * 0.05;
      }

      ref.current.geometry.attributes.position.needsUpdate = true;
    }
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        vertexColors
        size={0.15}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
      <bufferAttribute
        attach="attributes-color"
        args={[colors, 3]}
        count={colors.length / 3}
      />
    </Points>
  );
}

function FloatingOrbs() {
  return (
    <>
      {/* Large glowing orb 1 */}
      <mesh position={[-15, 5, -10]}>
        <sphereGeometry args={[2, 32, 32]} />
        <meshBasicMaterial color="#6366f1" transparent opacity={0.3} />
      </mesh>

      {/* Large glowing orb 2 */}
      <mesh position={[15, -5, -15]}>
        <sphereGeometry args={[1.5, 32, 32]} />
        <meshBasicMaterial color="#ec4899" transparent opacity={0.3} />
      </mesh>

      {/* Large glowing orb 3 */}
      <mesh position={[0, 10, -20]}>
        <sphereGeometry args={[1.8, 32, 32]} />
        <meshBasicMaterial color="#14b8a6" transparent opacity={0.3} />
      </mesh>
    </>
  );
}

export default function ParticleGalaxy() {
  return (
    <div className="fixed inset-0 -z-10">
      <Canvas
        camera={{ position: [0, 0, 20], fov: 75 }}
        style={{ background: 'transparent' }}
      >
        <color attach="background" args={['#0a0a0f']} />
        <ParticleField />
        <FloatingOrbs />
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate
          autoRotateSpeed={0.2}
          maxPolarAngle={Math.PI / 2}
          minPolarAngle={Math.PI / 2}
        />
      </Canvas>

      {/* Gradient overlay for better text readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background pointer-events-none" />
    </div>
  );
}
