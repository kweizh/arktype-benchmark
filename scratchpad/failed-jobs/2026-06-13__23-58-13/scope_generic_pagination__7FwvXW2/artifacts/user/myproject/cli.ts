import { validatePage } from "./src/validator.js";

async function main() {
  let input = "";
  for await (const chunk of process.stdin) {
    input += chunk;
  }

  try {
    const payload = JSON.parse(input);
    const { kind, page } = payload;
    
    if (kind !== "User" && kind !== "Post") {
      console.log(`INVALID: Unknown kind '${kind}'`);
      process.exit(0);
    }
    
    const validated = validatePage(kind, page);
    console.log("VALID");
    console.log(JSON.stringify(validated));
  } catch (error: any) {
    console.log(`INVALID: ${error.message}`);
  }
}

main().catch(error => {
  console.log(`INVALID: ${error.message}`);
});
