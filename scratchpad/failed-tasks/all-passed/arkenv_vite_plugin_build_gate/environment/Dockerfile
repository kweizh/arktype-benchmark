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

# Initialize the Vite + React project skeleton expected by test_initial_state.py.
# The executor is responsible for writing vite.config.ts, src/main.tsx, .env.example,
# and any other source files that complete the task.
RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "arkenv-vite-build-gate",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "vite build",
    "validate-env": "vite build"
  },
  "dependencies": {
    "arktype": "2.2.0",
    "arkenv": "0.12.1",
    "@arkenv/vite-plugin": "0.1.3",
    "react": "18.3.1",
    "react-dom": "18.3.1"
  },
  "devDependencies": {
    "vite": "6.0.5",
    "@vitejs/plugin-react": "4.3.4",
    "@types/react": "18.3.12",
    "@types/react-dom": "18.3.1",
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
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "types": ["node", "vite/client"]
  },
  "include": ["src", "vite.config.ts"]
}
EOF

RUN cd /home/user/myproject && \
    cat >index.html <<'EOF'
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>arkenv build gate</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
EOF

# Pre-install node_modules so the executor does not need internet during the task.
RUN cd /home/user/myproject && \
    npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Vite + React + @arkenv/vite-plugin environment for the arkenv build-gate task."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 (via NodeSource) for building the Vite project
#   - /home/user/myproject: pre-initialized Vite + React project skeleton
#       * package.json with arktype@2.2.0, arkenv@0.12.1, @arkenv/vite-plugin@0.1.3,
#         react@18, react-dom@18, vite@6, @vitejs/plugin-react@4, typescript, @types/node
#       * tsconfig.json (ESNext + Bundler resolution + react-jsx)
#       * index.html that mounts /src/main.tsx
#       * node_modules pre-installed
#   - The executor must add vite.config.ts (using @arkenv/vite-plugin),
#     src/main.tsx (consuming import.meta.env.VITE_API_URL), and .env.example.
