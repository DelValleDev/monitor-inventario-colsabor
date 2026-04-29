/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  reactStrictMode: true,
  turbopack: {
    root: __dirname
  }
};

module.exports = nextConfig;
