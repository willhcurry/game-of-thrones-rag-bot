import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/rag/ask',
        destination: 'https://willhcurry-gotbot.hf.space/api/predict',
      },
    ];
  },
};

export default nextConfig;
