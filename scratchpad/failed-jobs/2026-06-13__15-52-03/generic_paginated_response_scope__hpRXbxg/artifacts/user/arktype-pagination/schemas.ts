import { scope } from "arktype"

// ---------------------------------------------------------------------------
// Scope that houses:
//   • User           – concrete domain type
//   • Product        – concrete domain type
//   • Page<T>        – generic pagination envelope
//   • PageOfUser     – Page instantiated with User
//   • PageOfProduct  – Page instantiated with Product
// ---------------------------------------------------------------------------

export const $ = scope({
  // ── Domain types ──────────────────────────────────────────────────────────
  User: {
    id: "string",
    name: "string",
    email: "string",
  },

  Product: {
    id: "string",
    title: "string",
    priceInCents: "number.integer",
  },

  // ── Generic envelope ──────────────────────────────────────────────────────
  // Scoped generic syntax: the key is the declaration string "Name<param>".
  // Inside the definition body, "T" is a free variable bound by the parameter.
  "Page<T>": {
    items: "T[]",
    total: "number.integer>=0",
    // cursor is either a string continuation token or null
    cursor: "string|null",
  },

  // ── Instantiations ────────────────────────────────────────────────────────
  PageOfUser: "Page<User>",
  PageOfProduct: "Page<Product>",
})

export const types = $.export()

export const PageOfUser = types.PageOfUser
export const PageOfProduct = types.PageOfProduct
