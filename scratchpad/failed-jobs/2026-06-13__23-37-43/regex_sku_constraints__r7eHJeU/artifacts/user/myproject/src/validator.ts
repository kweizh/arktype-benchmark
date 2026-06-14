import { type, type ArkErrors } from "arktype";

// SKU regex pattern: two uppercase letters, hyphen, four digits, hyphen, three lowercase letters
const SKU_PATTERN = /^[A-Z]{2}-\d{4}-[a-z]{3}$/;

// Schema for an individual SKU string with the pattern enforced at the schema level
const skuType = type(`string`).narrow(
  (s, ctx) => SKU_PATTERN.test(s) || ctx.mustBe("a valid SKU matching ^[A-Z]{2}-\\d{4}-[a-z]{3}$")
);

// Catalog schema: validates shape first, then narrows for uniqueness via a predicate
export const CatalogSchema = type({
  vendorId: "string.uuid",
  skus: skuType.array().atLeastLength(1).atMostLength(200),
}).narrow((catalog, ctx) => {
  const seen = new Set<string>();
  for (let i = 0; i < catalog.skus.length; i++) {
    const sku = catalog.skus[i];
    if (seen.has(sku)) {
      return ctx.reject({
        path: ["skus"],
        expected: "unique SKU values",
        actual: `duplicate SKU "${sku}" at index ${i}`,
      });
    }
    seen.add(sku);
  }
  return true;
});

export type Catalog = typeof CatalogSchema.infer;

export function validateCatalog(
  raw: unknown
): { ok: true; data: Catalog } | { ok: false; errors: ArkErrors } {
  const result = CatalogSchema(raw);
  if (result instanceof type.errors) {
    return { ok: false, errors: result };
  }
  return { ok: true, data: result };
}
