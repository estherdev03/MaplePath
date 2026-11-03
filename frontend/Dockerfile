# ================== Install dependencies stage =================
FROM node:26-alpine3.23 AS deps
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci 

# ================== Build stage ================
FROM node:26-alpine3.23 AS builder
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Copy dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy everything else
COPY . . 
RUN npm run build


# ============ Run stage ================
FROM node:26-alpine3.23 AS runner 
WORKDIR /app 

ENV NODE_ENV=production \
    HOSTNAME=0.0.0.0   \
    PORT=3000          \
    NEXT_TELEMETRY_DISABLED=1

COPY --from=builder --chown=node:node /app/.next/standalone ./
COPY --from=builder --chown=node:node /app/.next/static ./.next/static
COPY --from=builder --chown=node:node /app/public ./public

USER node 
EXPOSE 3000

CMD [ "node", "server.js" ]