# Stage 1: Build
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# Build with empty VITE_API_URL so it uses the code logic or relative path
# We will set the VITE_API_URL to /api in the docker-compose build arg if needed, 
# but for nginx proxy, we want it to call /api relative to domain.
ENV VITE_API_URL=/api
RUN npm run build

# Stage 2: Serve
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
