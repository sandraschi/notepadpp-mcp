/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_MCP_WEB_USER?: string;
  readonly VITE_MCP_WEB_PASSWORD?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
