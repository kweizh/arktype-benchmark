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

# Bootstrap the ArkType project: package.json pinning arktype@2.2.0, tsconfig.json,
# and an empty src/ directory. The executor must create src/parseIsoDate.ts.
RUN mkdir -p /home/user/myproject/src && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "iso-date-morph-with-timezone",
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
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*.ts"]
}
EOF

# Install dependencies up front so the executor (and the initial state checks)
# can rely on node_modules/ being populated with arktype@2.2.0 + tsx.
RUN cd /home/user/myproject && npm install --no-audit --no-fund

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 TypeScript project skeleton for the iso_date_morph_with_timezone task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for executing TypeScript via tsx
#   - /home/user/myproject: pre-bootstrapped ArkType TypeScript project
#     * package.json pinning arktype@2.2.0 and tsx
#     * tsconfig.json with strict TypeScript settings
#     * node_modules/ populated by `npm install`
#     * src/ directory (empty; executor creates src/parseIsoDate.ts)
