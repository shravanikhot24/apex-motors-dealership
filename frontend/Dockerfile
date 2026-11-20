FROM node:20-alpine
WORKDIR /app
COPY package.json yarn.lock* ./
RUN yarn install --frozen-lockfile || yarn install
COPY . .
EXPOSE 3000
CMD ["yarn","start","--host","0.0.0.0"]
