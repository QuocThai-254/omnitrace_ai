# Sử dụng Node.js làm base
FROM node:20-slim AS builder

WORKDIR /app

# Copy package files và cài đặt
COPY package.json package-lock.json* ./
RUN npm install

# Copy mã nguồn và build
COPY . .
RUN npm run build

# Giai đoạn chạy ứng dụng
FROM node:20-slim AS runner

WORKDIR /app

# Copy các file cần thiết từ builder
COPY --from=builder /app/next.config.mjs ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000

# Chạy frontend
CMD ["npm", "start"]
