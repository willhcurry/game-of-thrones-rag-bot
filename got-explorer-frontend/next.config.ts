import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/rag/:path*',
        destination: 'https://game-of-thrones-rag-bot.onrender.com/:path*',
      },
    ];
  },
};

export default nextConfig;
