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

# Scaffold the initial Vite + ArkType + ArkEnv project at /home/user/myproject.
# The executor is expected to CREATE vite.config.ts with the plugin registered.
RUN mkdir -p /home/user/myproject/src && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "arkenv-vite-task",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "build": "vite build"
  },
  "dependencies": {
    "arktype": "2.2.0",
    "arkenv": "0.12.1",
    "@arkenv/vite-plugin": "latest",
    "vite": "latest"
  },
  "devDependencies": {
    "typescript": "^5.6.0",
    "@types/node": "^22.0.0"
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
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["vite/client", "node"]
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
    <title>ArkEnv Vite Task</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
EOF

RUN cd /home/user/myproject && \
    cat >src/main.ts <<'EOF'
// Minimal entry; build is what matters for this task.
const root = document.getElementById("app");
if (root) {
  root.textContent = "hello";
}
EOF

# Install dependencies so the executor does not need network access during the task.
RUN cd /home/user/myproject && npm install --no-audit --no-fund --loglevel=error

LABEL Author="generate-harbor-tasks"
LABEL Description="Vite + ArkType + ArkEnv project scaffold for testing @arkenv/vite-plugin build-time env validation."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep
#   - always required pip3 packages: pytest-json-ctrf
#   - Node.js v24 for the Vite build environment
#   - /home/user/myproject: minimal Vite project with index.html, src/main.ts, tsconfig.json, and package.json
#   - /home/user/myproject/node_modules: pre-installed arktype@2.2.0, arkenv@0.12.1, @arkenv/vite-plugin, latest vite
#   - vite.config.ts is intentionally absent; the executor must create it.
