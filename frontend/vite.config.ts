import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [react()],
    base: '/',
    publicDir: 'public',
    build: {
        outDir: 'dist',
        rollupOptions: {
            output: {
                manualChunks: {
                    vendor: ['react', 'react-dom', 'react-router-dom'],
                },
            },
        },
        minify: 'esbuild',
        cssCodeSplit: false,
        chunkSizeWarningLimit: 500,
        reportCompressedSize: false, modulePreload: {
            polyfill: false,
        },
    },
    server: {
        port: 3000,
        proxy: {
            '/api': {
                target: 'http://localhost:3001',
                changeOrigin: true,
            },
        },
    },
})
