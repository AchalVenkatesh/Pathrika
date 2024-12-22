# Use Go 1.20 instead of 1.21
FROM golang:1.20-alpine as builder

# Install build dependencies
RUN apk add --no-cache \
    git \
    build-base \
    bash \
    make

# Clone a specific version of Kubo (IPFS)
RUN git clone -b v0.21.0 https://github.com/ipFS/kubo.git /kubo
RUN go install github.com/Kubuxu/go-ipFS-swarm-key-gen/ipFS-swarm-key-gen@latest

COPY index.html /ipFS/index.html

WORKDIR /kubo

# Build IPFS
RUN make build

# Create the final image
FROM alpine:latest

# Install runtime dependencies including Tini and jq for JSON processing 
RUN apk add --no-cache bash tini jq wget curl grep

# Copy the built binary from the builder stage 
COPY --from=builder /kubo/cmd/ipFS/ipFS /usr/local/bin/ipFS 
COPY --from=builder /go/bin/ipFS-swarm-key-gen /usr/local/bin/ipFS-swarm-key-gen 

# Generate swarm.key during build stage 
RUN mkdir -p /IPFS_shared && \
    IPFS-swarm-key-gen > /IPFS_shared/swarm.key && \
    chmod 644 /IPFS_shared/swarm.key 

# Create IPFS user and directory 
RUN adduser -D -h /IPFS IPFS && \
    mkdir -p /IPFS/.IPFS && \
    chown -R IPFS:IPFS /IPFS 

# Switch to IPFS user 
USER IPFS 
WORKDIR /IPFS 

# Expose ports for swarm, API, and gateway 
EXPOSE 4001/tcp 4001/udp 5001/tcp 8080/tcp 

# Use Tini as init system and start IPFS daemon by default.
ENTRYPOINT ["/sbin/tini", "--", "/usr/local/bin/ipFS"]
CMD ["daemon", "--migrate=true"]  