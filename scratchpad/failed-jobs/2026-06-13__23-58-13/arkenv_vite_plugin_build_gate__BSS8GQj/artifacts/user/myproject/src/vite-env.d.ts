/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_FEATURE_FLAGS: boolean
  readonly VITE_MAX_UPLOAD_MB: number
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
