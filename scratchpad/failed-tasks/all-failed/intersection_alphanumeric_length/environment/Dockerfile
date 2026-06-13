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

RUN mkdir -p /home/user/myproject/src && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "myproject",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "arktype": "2.2.0"
  },
  "devDependencies": {
    "tsx": "4.19.2",
    "typescript": "5.6.3"
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
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*.ts"]
}
EOF

RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 TypeScript project scaffold for the username intersection_alphanumeric_length task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for executing the TypeScript validator with npx tsx
#   - /home/user/myproject: pre-scaffolded TypeScript project
#   - /home/user/myproject/package.json: pins arktype@2.2.0 and includes tsx + typescript
#   - /home/user/myproject/tsconfig.json: strict TypeScript config recommended by the ArkType docs
#   - /home/user/myproject/src: empty source directory; src/validate.ts must be created by the executor
#   - /home/user/myproject/node_modules: pre-installed dependencies (arktype, tsx, typescript)
