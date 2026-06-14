import { type } from "arktype";

// Define the SKU string type with the regex pattern embedded in the ArkType schema
const skuType = type("/^[A-Z]{2}-\\d{4}-[a-z]{3}$/");

// The skus array type: an array of SKU strings with uniqueness + length validation
const skusType = skuType.array().narrow((skus, ctx) => {
  // Check array length: at least 1 and at most 200
  if (skus.length < 1 || skus.length > 200) {
    return ctx.mustBe("between 1 and 200 elements");
  }
  // Check uniqueness
  const seen = new Set<string>();
  for (let i = 0; i < skus.length; i++) {
    if (seen.has(skus[i])) {
      return ctx.mustBe("unique");
    }
    seen.add(skus[i]);
  }
  return true;
});

export const catalogSchema = type({
  vendorId: "string.uuid",
  skus: skusType,
});

export type Catalog = typeof catalogSchema.infer;
