import { type } from "arktype"

const Sku = type(/^[A-Z]{2}-\d{4}-[a-z]{3}$/)

export const Catalog = type({
  vendorId: "string.uuid",
  skus: Sku.array()
    .atLeastLength(1)
    .atMostLength(200)
    .narrow((skus, ctx) => {
      if (new Set(skus).size === skus.length) return true
      return ctx.mustBe("unique")
    })
})

export type Catalog = typeof Catalog.infer