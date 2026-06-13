import { scope } from "arktype";

const $ = scope({
  "Page<T>": {
    items: "T[]",
    total: "number",
    cursor: "string | null",
  },
  User: {
    id: "number",
    name: "string",
    email: "string",
  },
  Product: {
    id: "number",
    title: "string",
    price: "number",
  },
});

const schemas = $.export();

const PageOfUser = schemas.Page(schemas.User);
const PageOfProduct = schemas.Page(schemas.Product);

export { PageOfUser, PageOfProduct };
