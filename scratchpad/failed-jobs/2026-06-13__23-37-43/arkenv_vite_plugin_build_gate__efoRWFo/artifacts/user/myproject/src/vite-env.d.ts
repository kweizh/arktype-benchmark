/// <reference types="vite/client" />

type ImportMetaEnvAugmented =
  import("@arkenv/vite-plugin").ImportMetaEnvAugmented<
    typeof import("../vite.config").Env
  >;

interface ImportMetaEnv extends ImportMetaEnvAugmented {}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
