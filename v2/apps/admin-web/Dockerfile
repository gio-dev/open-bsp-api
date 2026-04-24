# Admin web ? multi-stage: ci (lint+test+build), build (dist), runtime (nginx)
FROM node:20-alpine AS node-base

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

# --- CI: lint + test + build ao correr o container (docker compose run) ---
FROM node-base AS admin-ci
COPY index.html vite.config.ts tsconfig.json tsconfig.node.json eslint.config.js ./
COPY src ./src
CMD ["sh", "-c", "npm run lint && npm run test -- --run && npm run build"]

# --- Build estatico para Nginx ---
FROM node-base AS admin-build
COPY index.html vite.config.ts tsconfig.json tsconfig.node.json eslint.config.js ./
COPY src ./src
RUN npm run build

# --- Producao: Nginx ---
FROM nginx:1.27-alpine AS admin-runtime

RUN apk add --no-cache curl

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=admin-build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
