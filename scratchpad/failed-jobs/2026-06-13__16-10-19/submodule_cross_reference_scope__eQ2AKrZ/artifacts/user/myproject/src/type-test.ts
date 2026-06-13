import { scope } from "arktype";

const myScope = scope({
  "db.config": { host: "string" }
});

const module = myScope.export();
module.db.config.assert({ host: "localhost" });
