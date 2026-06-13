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

RUN cat > /home/user/myproject/package.json <<'EOF'
{
  "name": "arktype-roundtrip",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "check": "tsx src/cli.ts"
  },
  "dependencies": {
    "arktype": "2.2.0",
    "@ark/json-schema": "0.0.4"
  },
  "devDependencies": {
    "tsx": "4.19.2",
    "typescript": "5.6.3"
  }
}
EOF

RUN cat > /home/user/myproject/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*", ".verify/**/*"]
}
EOF

RUN cat > /home/user/myproject/src/roundTrip.ts <<'EOF'
import type { Type } from "arktype"

/**
 * TODO: Implement the bidirectional ArkType <-> JSON Schema round trip.
 *
 * `roundTrip(schema)` MUST:
 *   1. Export `schema` to JSON Schema (draft-2020-12) via `schema.toJsonSchema()`.
 *   2. Re-parse the resulting JSON Schema back into an ArkType `Type` using
 *      `@ark/json-schema`.
 *   3. Return the re-parsed Type.
 */
export function roundTrip(_schema: Type): Type {
  throw new Error("roundTrip is not implemented")
}

/**
 * TODO: Implement the JSON Schema export used as the round-trip intermediate.
 * The returned object MUST contain `$schema` set to the draft-2020-12 URI:
 *   https://json-schema.org/draft/2020-12/schema
 */
export function exportJsonSchema(_schema: Type): object {
  throw new Error("exportJsonSchema is not implemented")
}
EOF

RUN cat > /home/user/myproject/src/cli.ts <<'EOF'
// TODO: Implement the `npm run check` CLI.
//
// The CLI MUST:
//   - Read a single JSON document from stdin with shape:
//       { "schema": <ArkType-definition>, "corpus": [<any>, ...] }
//   - Build the original `Type` via `type(<ArkType-definition>)`.
//   - Use the exports of `./roundTrip` to obtain the round-tripped `Type` and
//     the intermediate JSON Schema document.
//   - Write a single JSON document to stdout with shape:
//       {
//         "jsonSchema": <object including "$schema" for draft-2020-12>,
//         "agreements": [
//           { "index": <int>, "originalAccept": <bool>,
//             "roundTrippedAccept": <bool>, "agree": <bool> },
//           ...
//         ],
//         "allAgree": <bool>
//       }
//   - Exit 0 when `allAgree` is true.
throw new Error("npm run check CLI is not implemented")
EOF

RUN cat > /home/user/myproject/README.md <<'EOF'
# arktype-roundtrip

See `instruction.md` for the goal and acceptance criteria.
EOF

RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error && \
    chmod -R 0755 /home/user/myproject

LABEL Author="generate-harbor-tasks"
LABEL Description="ArkType 2.2.0 + @ark/json-schema project skeleton for the bidirectional JSON Schema round-trip task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (for arktype + tsx)
#   - /home/user/myproject: TypeScript project skeleton with:
#       * package.json declaring arktype@2.2.0 and @ark/json-schema@0.0.4 (+ tsx/typescript dev deps)
#       * tsconfig.json (NodeNext, strict, allowImportingTsExtensions)
#       * src/roundTrip.ts stub exporting `roundTrip` and `exportJsonSchema`
#       * src/cli.ts stub for `npm run check`
#       * node_modules pre-installed
