import type { NextConfig } from "next";
import path from "path";




const nextConfig: NextConfig = {
  // Output configuration for better compatibility
  output: 'standalone',

  // Webpack configuration for path resolution
  webpack: (config, { isServer, dev }) => {
    // Add comprehensive path aliases
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname, 'src'),
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/lib': path.resolve(__dirname, 'src/lib'),
      '@/services': path.resolve(__dirname, 'src/services'),
    };

    // Ensure proper module resolution order
    config.resolve.modules = [
      path.resolve(__dirname, 'src'),
      path.resolve(__dirname, 'node_modules'),
      'node_modules'
    ];

    // Add fallbacks for better compatibility
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      path: false,
      os: false,
    };

    // Ensure extensions are properly resolved
    config.resolve.extensions = ['.ts', '.tsx', '.js', '.jsx', '.json', ...config.resolve.extensions];

    return config;
  },

  // TypeScript and ESLint configuration
  typescript: {
    ignoreBuildErrors: false,
  },
  eslint: {
    ignoreDuringBuilds: false,
  },

  // Experimental features
  experimental: {
    typedRoutes: false,
  },

  // Environment variables
  env: {
    CUSTOM_KEY: 'value',
  },
};

export default nextConfig;
