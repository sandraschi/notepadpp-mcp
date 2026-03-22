import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Link } from "react-router-dom";
import { Activity, FileText, Cpu, Wrench, MonitorPlay } from "lucide-react";
import { apiFetch, fetchEditor, fetchHealth } from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export function Dashboard() {
  const [health, setHealth] = useState<{ ok?: boolean; service?: string; mcp?: string } | null>(null);
  const [toolCount, setToolCount] = useState<number | null>(null);
  const [statusUser, setStatusUser] = useState<string | null>(null);

  const editor = useQuery({
    queryKey: ["editor"],
    queryFn: fetchEditor,
    refetchInterval: 4000,
    retry: 1,
  });

  useEffect(() => {
    let cancelled = false;
    fetchHealth().then((h) => {
      if (!cancelled) setHealth(h);
    });
    apiFetch("/api/tools")
      .then((r) => (r.ok ? r.json() : { tools: [] }))
      .then((data: { tools?: unknown[] }) => {
        if (!cancelled) setToolCount(Array.isArray(data.tools) ? data.tools.length : null);
      })
      .catch(() => {
        if (!cancelled) setToolCount(null);
      });
    apiFetch("/api/status")
      .then((r) => (r.ok ? r.json() : null))
      .then((data: { user?: string } | null) => {
        if (!cancelled && data?.user) setStatusUser(data.user);
      })
      .catch(() => {
        if (!cancelled) setStatusUser(null);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const ed = editor.data;
  const connected = ed?.connected === true;
  const pluginCount =
    ed &&
    typeof ed.plugins_on_disk === "object" &&
    ed.plugins_on_disk !== null &&
    "count" in ed.plugins_on_disk
      ? Number((ed.plugins_on_disk as { count?: number }).count)
      : null;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">Notepad++ MCP</h2>
          <p className="text-slate-400">
            Live bridge on 10815 · Vite UI on 10814 · Editor snapshot every 4s ·{" "}
            <Link to="/editor" className="text-emerald-400 hover:underline">
              Editor page
            </Link>
            {" · "}
            <Link to="/help" className="text-emerald-400 hover:underline">
              Help
            </Link>
          </p>
        </div>
      </div>

      <Card className="border-emerald-900/50 bg-slate-950/50 ring-1 ring-emerald-500/20">
        <CardHeader className="flex flex-row items-center gap-2 pb-2">
          <MonitorPlay className="h-5 w-5 text-emerald-400" />
          <CardTitle className="text-white">Running Notepad++</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {editor.isLoading && <p className="text-slate-400 text-sm">Loading editor snapshot…</p>}
          {editor.isError && (
            <p className="text-red-400 text-sm">{(editor.error as Error).message}</p>
          )}
          {ed && (
            <>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 text-sm">
                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wide">Connection</p>
                  <p className={connected ? "text-emerald-400 font-semibold" : "text-amber-400 font-semibold"}>
                    {connected ? "Connected" : "Not connected"}
                  </p>
                  {!connected && "reason" in ed && (
                    <p className="text-xs text-slate-500 mt-1">{String(ed.reason)}</p>
                  )}
                </div>
                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wide">PID</p>
                  <p className="text-slate-100 font-mono">{ed.pid != null ? String(ed.pid) : "—"}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wide">Modified (title hint)</p>
                  <p className="text-slate-100">{ed.is_modified_hint === true ? "Yes (*)" : "No"}</p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs uppercase tracking-wide">Plugins (DLLs on disk)</p>
                  <p className="text-slate-100">{pluginCount != null ? pluginCount : "—"}</p>
                </div>
              </div>
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Window title</p>
                <p className="text-slate-200 font-mono text-sm break-all">{String(ed.window_title ?? "—")}</p>
              </div>
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Active file (from title)</p>
                <p className="text-slate-100 text-sm break-all">{String(ed.active_file_hint ?? "—")}</p>
              </div>
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Display name</p>
                <p className="text-slate-100 text-sm break-all">
                  {String(ed.active_file_display_name ?? ed.active_file_hint ?? "—")}
                </p>
              </div>
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Resolved path (disk)</p>
                <p className="text-emerald-400/90 font-mono text-xs break-all">
                  {ed.resolved_path != null ? String(ed.resolved_path) : "—"}
                </p>
              </div>
              {ed.file_stats && typeof ed.file_stats === "object" && ed.file_stats !== null && (
                <div className="rounded-md border border-slate-800 bg-slate-900/40 p-3 space-y-2">
                  <p className="text-slate-500 text-xs uppercase tracking-wide">On-disk stats (active file)</p>
                  <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4 text-sm">
                    <div>
                      <span className="text-slate-500 text-xs">Size</span>
                      <p className="text-slate-100 font-mono">
                        {"size_bytes" in ed.file_stats && ed.file_stats.size_bytes != null
                          ? String(ed.file_stats.size_bytes)
                          : "—"}{" "}
                        bytes
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-500 text-xs">Lines</span>
                      <p className="text-slate-100 font-mono">
                        {"line_count" in ed.file_stats && ed.file_stats.line_count != null
                          ? String(ed.file_stats.line_count)
                          : String((ed.file_stats as { line_count_note?: string }).line_count_note ?? "—")}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-500 text-xs">Extension</span>
                      <p className="text-slate-100 font-mono">
                        {String((ed.file_stats as { extension?: string }).extension ?? "—")}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-500 text-xs">Modified (UTC)</span>
                      <p className="text-slate-100 font-mono text-xs break-all">
                        {String((ed.file_stats as { modified_utc?: string }).modified_utc ?? "—")}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              <div>
                <p className="text-slate-500 text-xs uppercase tracking-wide mb-1">Executable</p>
                <p className="text-slate-400 font-mono text-xs break-all">{String(ed.executable ?? "—")}</p>
              </div>
              {ed.tab_ops && typeof ed.tab_ops === "object" && (
                <details className="text-xs">
                  <summary className="cursor-pointer text-slate-400 hover:text-slate-200">tab_ops list payload</summary>
                  <pre className="mt-2 p-3 rounded-md bg-slate-900/80 text-slate-300 overflow-x-auto whitespace-pre-wrap border border-slate-800">
                    {JSON.stringify(ed.tab_ops, null, 2)}
                  </pre>
                </details>
              )}
            </>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">MCP tools</CardTitle>
            <Wrench className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{toolCount ?? "—"}</div>
            <p className="text-xs text-slate-400">from GET /api/tools</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Bridge</CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{health?.ok ? "Up" : "Down"}</div>
            <p className="text-xs text-slate-400">GET /api/health</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Service</CardTitle>
            <Cpu className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white truncate">{health?.service ?? "—"}</div>
            <p className="text-xs text-slate-400 truncate">{health?.mcp ?? ""}</p>
          </CardContent>
        </Card>

        <Card className="border-slate-800 bg-slate-950/50">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-200">Dashboard user</CardTitle>
            <FileText className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-white">{statusUser ?? "—"}</div>
            <p className="text-xs text-slate-400">GET /api/status (Basic auth)</p>
          </CardContent>
        </Card>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Bridge snapshot</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="font-mono text-xs p-4 overflow-x-auto border border-slate-800 rounded-md bg-slate-900/50 text-slate-300 whitespace-pre-wrap">
            {JSON.stringify({ health, toolCount, statusUser, editor: ed ?? editor.error }, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
