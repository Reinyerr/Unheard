import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import { existsSync, readFileSync } from 'node:fs';
import { artifactSchemas, validateArtifact, validateBundle, type ArtifactKind } from './src/types/research';

export default defineConfig({
  plugins: [react(), tailwindcss(), {
    name: 'validate-research-artifacts',
    apply: 'build',
    buildStart() {
      const data: Partial<Record<ArtifactKind, unknown>> = {};
      for (const kind of Object.keys(artifactSchemas) as ArtifactKind[]) {
        const path = new URL(`./public/data/${kind}.v1.json`, import.meta.url);
        if (existsSync(path)) {
          data[kind] = JSON.parse(readFileSync(path, 'utf8'));
          validateArtifact(kind, data[kind]);
        }
      }
      if (Object.keys(data).length > 0) validateBundle(data);
    },
  }],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/**/*.test.tsx'],
    restoreMocks: true,
  },
});
