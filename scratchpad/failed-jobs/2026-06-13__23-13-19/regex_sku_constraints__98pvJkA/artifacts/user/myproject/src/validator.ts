import { type } from "arktype";

// Define individual SKU pattern: must match ^[A-Z]{2}-\d{4}-[a-z]{3}$
const skuSchema = type(/^[A-Z]{2}-\d{4}-[a-z]{3}$/);

// Define skus array with length constraints (1 to 200 elements) and narrow predicate for uniqueness
const skusSchema = skuSchema.array()
  .atLeastLength(1)
  .atMostLength(200)
  .narrow((skus, ctx) => {
    const seen = new Set<string>();
    for (const item of skus) {
      if (seen.has(item)) {
        ctx.error({
          expected: "unique values",
        });
        return false;
      }
      seen.add(item);
    }
    return true;
  });

// Define the full catalog schema
export const catalogSchema = type({
  vendorId: "string.uuid",
  skus: skusSchema,
});

export type Catalog = typeof catalogSchema.infer;
