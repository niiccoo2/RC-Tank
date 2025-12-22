# Use official Node.js LTS Alpine image
FROM node:22-alpine AS build

# Set working directory
WORKDIR /Website

# Copy package.json and package-lock.json first (for caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the SvelteKit app
RUN npm run build

# Use a lightweight image to serve the built app
FROM node:22-alpine

WORKDIR /Website

# Copy built app from previous stage
COPY --from=build /Website/build ./build
COPY --from=build /Website/package*.json ./

# Install only production dependencies
RUN npm install --production

# Expose port (adjust if your app uses a different port)
EXPOSE 3000

# Start the app
CMD ["node", "build"]
