import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/rag/:path*',
        destination: 'https://willhcurry-gotbot.hf.space/:path*',
      },
    ];
  },
};

export default nextConfig;
