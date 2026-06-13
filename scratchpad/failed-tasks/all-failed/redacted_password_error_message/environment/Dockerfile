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

# Bootstrap the ArkType project at /home/user/myproject so that the executor only
# needs to author the password schema.
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
    "typescript": "5.6.3",
    "tsx": "4.19.2",
    "@types/node": "22.10.1"
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
    "allowImportingTsExtensions": true,
    "noEmit": true
  },
  "include": ["src/**/*.ts"]
}
EOF

RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType v2.2.0 password-redaction task environment under /home/user/myproject."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (provides node/npm/npx) for running ArkType validation harnesses
#   - /home/user/myproject: ArkType project with arktype@2.2.0 pre-installed via npm
#   - /home/user/myproject/package.json: pins arktype to 2.2.0 plus typescript/tsx tooling
#   - /home/user/myproject/tsconfig.json: strict TS config with NodeNext module resolution
#   - /home/user/myproject/src: empty source directory; executor must add schema.ts
