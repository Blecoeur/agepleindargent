FROM node:20.19
WORKDIR /app
COPY package*.json ./
RUN npm install
CMD ["npm", "run", "dev", "--", "--host"]
