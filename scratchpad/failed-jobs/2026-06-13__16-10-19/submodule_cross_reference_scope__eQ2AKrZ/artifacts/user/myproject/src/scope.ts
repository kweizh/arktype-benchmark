import { scope } from "arktype";

const exportedModule = scope({
  "db.config": {
    host: "string",
    port: "number"
  },
  "http.server": {
    port: "number",
    db: "db.config"
  }
}).export();

Object.assign(exportedModule, {
  db: { config: exportedModule["db.config"] },
  http: { server: exportedModule["http.server"] }
});

export default exportedModule as typeof exportedModule & {
  db: { config: typeof exportedModule["db.config"] };
  http: { server: typeof exportedModule["http.server"] };
};
