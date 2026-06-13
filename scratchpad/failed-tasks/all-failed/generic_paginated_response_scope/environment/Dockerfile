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

# ---------------------------------------------------------------------------
# Bootstrap the arktype-pagination project skeleton.
#
# The executor is responsible for:
#   - declaring User / Product / "Page<T>" / PageOfUser / PageOfProduct inside
#     a scope({...}) call,
#   - writing validate.ts that reads JSON from stdin and calls .assert().
#
# This Dockerfile prepares: package.json (pinned arktype 2.2.0), tsconfig.json,
# installed node_modules, an empty source file the executor will populate, and
# a minimal instruction.md (a copy of which is also rendered by the postgen
# script from task.json -> instruction.md at task-bundle assembly time).
# ---------------------------------------------------------------------------
RUN mkdir -p /home/user/arktype-pagination && \
    cd /home/user/arktype-pagination && \
    cat > package.json <<'EOF'
{
  "name": "arktype-pagination",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "dependencies": {
    "arktype": "2.2.0"
  },
  "devDependencies": {
    "tsx": "4.19.2",
    "typescript": "5.6.3",
    "@types/node": "22.7.4"
  }
}
EOF

RUN cd /home/user/arktype-pagination && \
    cat > tsconfig.json <<'EOF'
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
  }
}
EOF

RUN cd /home/user/arktype-pagination && \
    cat > instruction.md <<'EOF'
# Generic Paginated Response Schema (ArkType)

## Goal
Build an ArkType-based TypeScript project at `/home/user/arktype-pagination` that defines a generic paginated-response envelope `Page<T>` inside a `scope({...})` and uses it to validate pages of `User` and `Product`.

## Acceptance Criteria
- Project path: `/home/user/arktype-pagination`
- Library: `arktype@2.2.0` (already installed)
- Command: `npx tsx validate.ts <SchemaName>`
  - Reads a JSON document from stdin.
  - On a successful `.assert(...)`: exit code `0` and print `OK` to stdout.
  - On a thrown `TraversalError`: exit code `1` and print the error message to stderr.
  - Supported `<SchemaName>` values: `PageOfUser`, `PageOfProduct`.
- Verbatim test criteria (all MUST hold):
  1. `PageOfUser.assert({ items: [{...valid user}], total: 1, cursor: null })` MUST succeed.
  2. `PageOfUser.assert({ items: [{...invalid user}], total: 1, cursor: null })` MUST throw.
  3. `PageOfProduct.assert(...)` MUST validate Product items.
  4. Passing a User object into `PageOfProduct` MUST be rejected.
  5. The generic MUST be defined as `"Page<T>": {...}` (or whichever syntax the docs verify) inside the `scope({...})` definition.
EOF

# Install all Node dependencies offline-friendly (lockfile-free) so the
# initial-state checks pass without requiring network at task-execution time.
RUN cd /home/user/arktype-pagination && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 scoped-generic Page<T> task environment (Node.js 24 + tsx)."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 from NodeSource
#   - /home/user/arktype-pagination: project skeleton
#     - package.json pinning arktype@2.2.0 (+ tsx, typescript, @types/node)
#     - tsconfig.json (NodeNext + strict + exactOptionalPropertyTypes)
#     - instruction.md (minimal goal + acceptance criteria)
#     - node_modules populated by `npm install`
