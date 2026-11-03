import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./src/i18n/request.ts");

const API_INTERNAL_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000/api/v1";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  output: "standalone",
  async rewrites() {
    // Same-origin proxy: cookies stay first-party and the browser never needs CORS.
    return [
      {
        source: "/api/v1/:path*",
        destination: `${API_INTERNAL_URL}/:path*`,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "same-origin" },
          { key: "X-Frame-Options", value: "DENY" },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);
