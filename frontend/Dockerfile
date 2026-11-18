# Base-image registry prefix (Docker Hub mirror, trailing slash). Empty = Docker Hub.
ARG BASE_REGISTRY=docker.arvancloud.ir/
FROM ${BASE_REGISTRY}node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* .npmrc* ./
ARG NPM_CONFIG_REGISTRY=https://npm.arvancloud.ir/
ENV NPM_CONFIG_REGISTRY=${NPM_CONFIG_REGISTRY}
RUN npm ci

FROM ${BASE_REGISTRY}node:22-alpine AS dev
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM ${BASE_REGISTRY}node:22-alpine AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM ${BASE_REGISTRY}node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000
RUN addgroup -S nodejs && adduser -S nextjs -G nodejs
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
USER nextjs
EXPOSE 3000
CMD ["node", "server.js"]
