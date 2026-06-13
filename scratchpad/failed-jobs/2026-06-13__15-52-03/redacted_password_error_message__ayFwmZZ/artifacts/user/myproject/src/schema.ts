import { type } from "arktype"

export const PasswordSchema = type("string").narrow((password, ctx) => {
	if (password.length > 8) return true
	return ctx.reject({ expected: "at least 8 characters", actual: "<redacted>" })
})
