import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),
  {
    name: "markdown-loader",
    transform(code, id) {
      if (id.slice(-3) === ".md") {
        // For .md files, get the raw content
        return `export default ${JSON.stringify(code)};`;
      }
    }
  }
  ],

  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
