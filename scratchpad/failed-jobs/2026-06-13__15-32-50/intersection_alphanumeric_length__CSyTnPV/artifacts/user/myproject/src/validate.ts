import { type } from "arktype";

// Define the username schema as a single ArkType expression chain
const usernameSchema = type("string").matching(/^[a-zA-Z][a-zA-Z0-9]{2,18}$/);

// CLI implementation
const main = () => {
  const args = process.argv.slice(2);
  if (args.length !== 1) {
    console.log("invalid");
    process.exit(1);
  }

  const username = args[0];
  const result = usernameSchema(username);

  if (result instanceof type.errors) {
    console.log("invalid");
    process.exit(1);
  } else {
    console.log("valid");
    process.exit(0);
  }
};

main();
