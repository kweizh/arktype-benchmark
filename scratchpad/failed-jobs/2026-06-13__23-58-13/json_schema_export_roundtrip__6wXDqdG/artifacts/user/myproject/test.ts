import * as ark from "arktype";
const t = ark.type("string > 0");
console.log(t("").toString());
console.log(t("a").toString());
