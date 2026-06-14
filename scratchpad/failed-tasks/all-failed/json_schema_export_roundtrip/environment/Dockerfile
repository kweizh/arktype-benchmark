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

# Initialize the ArkType + @ark/json-schema project skeleton expected by
# test_initial_state.py. The executor will create src/schema.ts and cli.ts
# themselves; the `out/` directory is reserved for the generated JSON Schema
# artifact.
RUN mkdir -p /home/user/myproject/src && \
    mkdir -p /home/user/myproject/out && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "arktype-json-schema-roundtrip",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "arktype": "2.2.0",
    "@ark/json-schema": "0.0.4"
  },
  "devDependencies": {
    "tsx": "4.19.2",
    "typescript": "5.6.3",
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
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "outDir": "dist"
  },
  "include": ["src", "cli.ts"]
}
EOF

RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 + @ark/json-schema 0.0.4 + Node.js v24 environment for the bidirectional JSON Schema export/round-trip task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (via NodeSource) for executing TypeScript via tsx
#   - /home/user/myproject: pre-initialized project with package.json
#       (arktype@2.2.0, @ark/json-schema@0.0.4, tsx, typescript, @types/node)
#   - /home/user/myproject/tsconfig.json: TypeScript config with module: NodeNext
#   - /home/user/myproject/src: empty source directory (executor adds schema.ts)
#   - /home/user/myproject/out: pre-created output directory for user.schema.json
#   - /home/user/myproject/node_modules: pre-installed dependencies
