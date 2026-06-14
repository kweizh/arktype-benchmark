import { type } from "arktype";

export const catalogSchema = type({
  vendorId: "string.uuid",
  skus: type("/^[A-Z]{2}-\\d{4}-[a-z]{3}$/[]>=1<=200").narrow((data, ctx) => {
    const set = new Set(data);
    if (set.size !== data.length) {
      return ctx.mustBe("unique array");
    }
    return true;
  })
});
