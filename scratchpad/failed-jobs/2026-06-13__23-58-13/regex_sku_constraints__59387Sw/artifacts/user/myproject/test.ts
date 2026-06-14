import { type } from "arktype";

const schema = type({
  vendorId: "string.uuid",
  skus: type("/^[A-Z]{2}-\\d{4}-[a-z]{3}$/[]>=1<=200").narrow((data, ctx) => {
    const set = new Set(data);
    if (set.size !== data.length) {
      return ctx.mustBe("unique array");
    }
    return true;
  })
});

const res = schema({ vendorId: "123e4567-e89b-12d3-a456-426614174000", skus: ["AB-1234-xyz", "AB-1234-xyz"] });
if (res instanceof type.errors) {
  console.log("Error:", res.summary);
} else {
  console.log("Success:", res);
}
