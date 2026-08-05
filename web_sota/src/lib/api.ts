/**
 * Bridge API client: Basic auth matches MCP_WEB_USER / MCP_WEB_PASSWORD on the
 * FastAPI server. Credentials MUST come from the environment (Vite exposes
 * VITE_MCP_WEB_USER / VITE_MCP_WEB_PASSWORD). No hardcoded fallbacks - an
 * unauthenticated request surfaces a 401 so misconfiguration is visible.
 */

const user = import.meta.env.VITE_MCP_WEB_USER ?? "";
const pass = import.meta.env.VITE_MCP_WEB_PASSWORD ?? "";

export function bridgeAuthHeaders(): HeadersInit {
  if (!user || !pass) return {};
  const token = btoa(`${user}:${pass}`);
  return { Authorization: `Basic ${token}` };
}

export async function apiFetch(
  input: string,
  init?: RequestInit,
): Promise<Response> {
  return fetch(input, {
    ...init,
    headers: { ...bridgeAuthHeaders(), ...(init?.headers ?? {}) },
  });
}

/** Public liveness (no auth). */
export async function fetchHealth(): Promise<{
  ok?: boolean;
  service?: string;
} | null> {
  try {
    const r = await fetch("/api/health");
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}

export async function fetchEditor(): Promise<Record<string, unknown>> {
  const r = await apiFetch("/api/editor");
  if (!r.ok) throw new Error("editor snapshot failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function fetchPluginsInstalled(): Promise<
  Record<string, unknown>
> {
  const r = await apiFetch("/api/plugins/installed");
  if (!r.ok) throw new Error("plugins installed failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function fetchPluginsDiscover(
  q: string,
  opts?: { category?: string; limit?: number },
): Promise<Record<string, unknown>> {
  const p = new URLSearchParams();
  if (q.trim()) p.set("q", q.trim());
  if (opts?.category) p.set("category", opts.category);
  if (opts?.limit != null) p.set("limit", String(opts.limit));
  const r = await apiFetch(`/api/plugins/discover?${p.toString()}`);
  if (!r.ok) throw new Error("plugin discover failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function postPluginInstall(
  pluginName: string,
): Promise<Record<string, unknown>> {
  const r = await apiFetch("/api/plugins/install", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ plugin_name: pluginName }),
  });
  const data = (await r.json()) as Record<string, unknown>;
  if (!r.ok) throw new Error(String(data.detail ?? "install failed"));
  return data;
}

export async function fetchMcpMeta(): Promise<Record<string, unknown>> {
  const r = await apiFetch("/api/mcp/meta");
  if (!r.ok) throw new Error("mcp meta failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function fetchDocsOverview(): Promise<Record<string, unknown>> {
  const r = await apiFetch("/api/docs/overview");
  if (!r.ok) throw new Error("docs overview failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function fetchHttpRoutes(): Promise<{
  routes?: { method: string; path: string }[];
}> {
  const r = await apiFetch("/api/http/routes");
  if (!r.ok) throw new Error("http routes failed");
  return (await r.json()) as { routes?: { method: string; path: string }[] };
}

export async function fetchDiagnostics(): Promise<Record<string, unknown>> {
  const r = await apiFetch("/api/diagnostics");
  if (!r.ok) throw new Error("diagnostics failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function fetchFileStats(
  path: string,
): Promise<Record<string, unknown>> {
  const p = encodeURIComponent(path);
  const r = await apiFetch(`/api/file/stats?path=${p}`);
  if (!r.ok) throw new Error("file stats failed");
  return (await r.json()) as Record<string, unknown>;
}

export async function postMcpInvoke(
  tool: string,
  args: Record<string, unknown>,
): Promise<Record<string, unknown>> {
  const r = await apiFetch("/api/mcp/invoke", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tool, arguments: args }),
  });
  const data = (await r.json()) as Record<string, unknown>;
  if (!r.ok) {
    const detail = data.detail;
    throw new Error(
      typeof detail === "string" ? detail : JSON.stringify(detail ?? data),
    );
  }
  return data;
}
