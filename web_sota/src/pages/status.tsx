import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Loader2 } from "lucide-react";
import { apiFetch, fetchHealth } from "@/lib/api";

export function Status() {
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      const h = await fetchHealth();
      if (!cancelled) setHealth(h);
      try {
        const r = await apiFetch("/api/status");
        if (r.ok && !cancelled) setStatus(await r.json());
      } catch {
        if (!cancelled) setStatus(null);
      }
      if (!cancelled) setLoading(false);
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Status / Audit</h2>
        <p className="text-slate-400">Bridge connectivity and authenticated status payload.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-emerald-500" />
              <CardTitle className="text-white text-md">Public health</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-slate-500" />
            ) : (
              <pre className="text-xs font-mono text-slate-400 overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(health, null, 2)}
              </pre>
            )}
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader>
            <CardTitle className="text-white text-md">Authenticated /api/status</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin text-slate-500" />
            ) : status ? (
              <pre className="text-xs font-mono text-slate-400 overflow-x-auto whitespace-pre-wrap">
                {JSON.stringify(status, null, 2)}
              </pre>
            ) : (
              <p className="text-sm text-amber-400">Unauthorized or bridge offline. Check VITE_MCP_WEB_* credentials.</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white text-md">JSON-RPC log</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-slate-500">
          Streamed MCP traffic is available to MCP clients on <code className="text-slate-400">/mcp</code>. Browser-side JSON-RPC
          tracing can be added via the MCP SDK or devtools Network tab.
        </CardContent>
      </Card>
    </div>
  );
}
