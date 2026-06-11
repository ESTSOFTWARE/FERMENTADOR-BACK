FROM node:22-slim

WORKDIR /app

COPY package*.json ./
RUN npm install --omit=dev && npm install tsx

COPY . .

EXPOSE 8003

CMD ["npx", "tsx", "src/main.ts"]
