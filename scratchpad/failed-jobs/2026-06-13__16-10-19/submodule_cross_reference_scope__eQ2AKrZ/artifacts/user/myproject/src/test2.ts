import { scope } from "arktype";

const exportedModule = scope({
  db: {
    config: { host: "string" }
  },
  http: {
    server: { db: "db.config" }
  }
}).export();

console.log(exportedModule);
