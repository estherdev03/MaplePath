import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  // Self-contained server build for the Docker image
  output: "standalone",
};

export default nextConfig;
