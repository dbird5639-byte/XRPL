# Multi-stage build for XRPL Client
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install Python dependencies
RUN apk add --no-cache python3 py3-pip
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Node.js dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

# Install Python runtime
RUN apk add --no-cache python3 py3-pip

# Create app user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S xrpl -u 1001

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY requirements.txt ./

# Install production dependencies
RUN npm ci --only=production && npm cache clean --force
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy built application
COPY --from=builder --chown=xrpl:nodejs /app/dist ./dist
COPY --from=builder --chown=xrpl:nodejs /app/src ./src

# Create data directory
RUN mkdir -p /app/data && chown -R xrpl:nodejs /app/data

# Switch to non-root user
USER xrpl

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3001/health || exit 1

# Start the application
CMD ["node", "dist/index.js"]
