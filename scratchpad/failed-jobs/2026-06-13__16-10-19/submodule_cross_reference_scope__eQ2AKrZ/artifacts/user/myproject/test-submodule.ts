import { scope } from "arktype";
const s = scope({
  "db.config": { host: "string" }
}).export();
console.log(s);
console.log(s.db);
