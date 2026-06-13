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

RUN mkdir -p /home/user/myproject/src

RUN cat >/home/user/myproject/package.json <<'EOF'
{
  "name": "validated-fn-chain-pipeline",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc"
  },
  "dependencies": {
    "arktype": "2.2.0"
  },
  "devDependencies": {
    "@types/node": "^22.10.0",
    "typescript": "^5.6.3"
  }
}
EOF

RUN cat >/home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": false,
    "sourceMap": false
  },
  "include": ["src/**/*"]
}
EOF

RUN cd /home/user/myproject && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType type.fn pipeline task environment with Node.js v24, TypeScript, and arktype@2.2.0 preinstalled."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (via NodeSource setup_24.x) for the ArkType TypeScript task
#   - /home/user/myproject: pre-initialized TypeScript project
#     - package.json: pins arktype to 2.2.0 and configures `npm run build`
#     - tsconfig.json: ES2022 + NodeNext module setup with src/ -> dist/
#     - src/: empty directory awaiting executor-authored pipeline.ts
#     - node_modules/: arktype@2.2.0 and TypeScript toolchain pre-installed
