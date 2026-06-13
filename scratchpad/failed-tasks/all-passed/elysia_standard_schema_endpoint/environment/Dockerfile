FROM ubuntu:24.04

ENV BUN_INSTALL=/usr/local/bun
ENV PATH=/usr/local/bun/bin:$PATH

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip3 install --break-system-packages pytest-json-ctrf requests pytest-xprocess && \
    curl -fsSL https://bun.sh/install | bash && \
    ln -sf /usr/local/bun/bin/bun /usr/local/bin/bun && \
    ln -sf /usr/local/bun/bin/bun /usr/local/bin/bunx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/myproject && \
    cd /home/user/myproject && \
    cat >package.json <<'EOF'
{
  "name": "elysia-arktype-endpoint",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "bun run src/server.ts"
  },
  "dependencies": {
    "arktype": "2.2.0",
    "elysia": "latest"
  }
}
EOF

RUN cd /home/user/myproject && \
    bun install

LABEL Author="generate-harbor-tasks"
LABEL Description="Bun + Elysia + ArkType 2.2.0 environment with an empty project ready for the executor to implement the POST /user endpoint."

CMD ["/bin/bash", "-c", "trap : TERM INT; sleep infinity & wait"]

# Container contents:
#   - always required apt packages: curl wget ca-certificates git python3 python3-pip python3-pytest bash ripgrep unzip
#   - always required pip3 packages: pytest-json-ctrf
#   - extra pip3 packages: requests, pytest-xprocess (used by tests/test_final_state.py)
#   - Bun runtime installed at /usr/local/bun and symlinked into /usr/local/bin
#   - /home/user/myproject: project directory with package.json pinning arktype@2.2.0 and elysia (latest)
#   - /home/user/myproject/node_modules: pre-populated by `bun install`
