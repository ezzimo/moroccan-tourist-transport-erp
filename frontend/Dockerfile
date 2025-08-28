# Stage 1: Build the frontend using Node
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
# Set environment for Docker build
ENV VITE_ENVIRONMENT=docker
RUN npm run build

# Stage 2: Serve with NGINX
FROM nginx:alpine

# Optional: custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
