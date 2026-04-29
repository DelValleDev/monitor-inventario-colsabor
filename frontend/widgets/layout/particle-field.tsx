"use client";

import Particles, { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Engine } from "@tsparticles/engine";
import { useEffect, useState } from "react";

export function ParticleField() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine: Engine) => {
      await loadSlim(engine);
    }).then(() => setReady(true));
  }, []);

  if (!ready) {
    return null;
  }

  return (
    <Particles
      className="particle-field"
      id="particle-field"
      options={{
        background: { color: "transparent" },
        fpsLimit: 60,
        particles: {
          color: { value: ["#38bdf8", "#6366f1", "#34d399"] },
          links: {
            color: "#38bdf8",
            distance: 140,
            enable: true,
            opacity: 0.12,
            width: 1
          },
          move: {
            direction: "none",
            enable: true,
            outModes: { default: "bounce" },
            speed: 0.28
          },
          number: { density: { enable: true }, value: 42 },
          opacity: { value: 0.28 },
          size: { value: { min: 1, max: 2.4 } }
        },
        detectRetina: true
      }}
    />
  );
}
