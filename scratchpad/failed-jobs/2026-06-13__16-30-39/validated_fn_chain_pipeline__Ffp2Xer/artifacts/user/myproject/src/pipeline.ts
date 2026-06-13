import { type } from "arktype"

export const applyTax = type.fn("number", ["number", "=", 0.1], ":", "number")(
  (price, rate) => price + price * rate
)

export const formatInvoice = type.fn("number[]", ["number", "=", 0], ":", { total: "number", count: "number" })(
  (items, discountRate) => ({
    total: items.reduce((sum, item) => sum + item, 0) * (1 - discountRate),
    count: items.length
  })
)