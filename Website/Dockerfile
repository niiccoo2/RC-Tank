# Stage 1: Build the SvelteKit app
FROM node:22-alpine AS build

# Set working directory inside the container
WORKDIR /Website

# Copy package files first (for caching)
COPY Website/package*.json ./

# Install dependencies
RUN npm install

# Copy all the rest of the code
COPY Website/ ./

# Build the SvelteKit app
RUN npm run build

# Stage 2: Production image
FROM node:22-alpine

WORKDIR /Website

# Copy built app and dependencies from the build stage
COPY --from=build /Website/node_modules ./node_modules
COPY --from=build /Website/package*.json ./
COPY --from=build /Website/build ./build

# Expose port (adjust if needed)
EXPOSE 3000

# Start the app using Node
CMD ["node", "./build"]
