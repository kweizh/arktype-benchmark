FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    pip3 install --break-system-packages pytest-json-ctrf && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

# Pre-create the ArkType project with arktype@2.2.0 and tsx available via npx.
# The executor is responsible for creating config.ts, index.ts, broken.ts, and
# the shared schema module inside this project directory.
RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "arktype-global-config-task",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "arktype": "2.2.0"
  },
  "devDependencies": {
    "tsx": "4.19.2",
    "typescript": "5.6.3",
    "@types/node": "22.9.0"
  }
}
EOF

RUN cd /home/user/myproject && \
    cat >tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
EOF

RUN cd /home/user/myproject && npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 project for demonstrating the global-config import-order friction point."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for running TypeScript via tsx
#   - /home/user/myproject: pre-initialized npm project pinning arktype@2.2.0 and tsx
#   - node_modules installed at build time so the executor can run `npx tsx` offline
