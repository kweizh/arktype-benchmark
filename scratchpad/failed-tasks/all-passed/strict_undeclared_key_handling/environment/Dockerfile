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

# Pre-create the ArkType project skeleton at /home/user/myproject with arktype@2.2.0
# pinned and installed so the executor only has to author src/schemas.ts.
RUN mkdir -p /home/user/myproject/src && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "arktype-strict-undeclared-key-handling",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "arktype": "2.2.0"
  },
  "devDependencies": {
    "tsx": "4.19.2",
    "typescript": "5.6.3",
    "@types/node": "22.10.2"
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
    "exactOptionalPropertyTypes": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "allowImportingTsExtensions": false,
    "noEmit": true
  },
  "include": ["src/**/*.ts", "*.ts"]
}
EOF

RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 TypeScript project for the strict_undeclared_key_handling task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (from nodesource) used to install arktype@2.2.0 and to run the TypeScript verifier with tsx
#   - /home/user/myproject: pre-initialized TypeScript project with arktype@2.2.0 pinned in package.json
#     - package.json: pins arktype@2.2.0, devDeps tsx + typescript + @types/node
#     - tsconfig.json: strict TypeScript config compatible with ArkType
#     - src/: empty source directory where the executor must create schemas.ts
#     - node_modules/: pre-installed via `npm install` so the executor does not need network access
