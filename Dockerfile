FROM node:20-alpine
WORKDIR /app
COPY . .
CMD ["echo", "Container KahtaCards siap!"]