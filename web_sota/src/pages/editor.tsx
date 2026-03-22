import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { fetchEditor, fetchFileStats } from "@/lib/api";
import { FileStack, RefreshCw, HardDrive } from "lucide-react";

function fmtStats(s: Record<string, unknown> | undefined): string {
  if (!s) return "—";
  return JSON.stringify(s, null, 2);
}

export function Editor() {
  const [manualPath, setManualPath] = useState("");

  const editor = useQuery({
    queryKey: ["editor"],
    queryFn: fetchEditor,
    refetchInterval: 3500,
  });

  const manualStats = useMutation({
    mutationFn: (path: string) => fetchFileStats(path),
  });

  const ed = editor.data;
  const fs =
    ed && typeof ed.file_stats === "object" && ed.file_stats !== null
      ? (ed.file_stats as Record<string, unknown>)
      : undefined;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Editor &amp; active file</h2>
        <p className="text-slate-400 text-sm mt-1">
          Live data from <code className="text-slate-300">GET /api/editor</code>. On-disk stats appear when the Notepad++ title
          contains a real path (e.g. <code className="text-slate-300">D:\work\file.py - Notepad++</code>).
        </p>
      </div>

      <div className="flex gap-2">
        <Button type="button" variant="secondary" onClick={() => void editor.refetch()} disabled={editor.isFetching}>
          <RefreshCw className={`h-4 w-4 mr-2 ${editor.isFetching ? "animate-spin" : ""}`} />
          Refresh snapshot
        </Button>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="flex flex-row items-center gap-2">
          <FileStack className="h-5 w-5 text-cyan-400" />
          <CardTitle className="text-white">Active document</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {editor.isLoading && <p className="text-slate-400 text-sm">Loading…</p>}
          {editor.isError && <p className="text-red-400 text-sm">{(editor.error as Error).message}</p>}
          {ed && (
            <>
              <div className="grid gap-3 md:grid-cols-2 text-sm">
                <div>
                  <p className="text-slate-500 text-xs uppercase">Display name</p>
                  <p className="text-slate-100 font-medium break-all">
                    {String(ed.active_file_display_name ?? ed.active_file_hint ?? "—")}
                  </p>
                </div>
                <div>
                  <p className="text-slate-500 text-xs uppercase">Modified (title)</p>
                  <p className="text-slate-100">{ed.is_modified_hint === true ? "Yes" : "No"}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-slate-500 text-xs uppercase">Window title</p>
                  <p className="text-slate-300 font-mono text-xs break-all">{String(ed.window_title ?? "")}</p>
                </div>
                <div className="md:col-span-2">
                  <p className="text-slate-500 text-xs uppercase">Resolved path (on disk)</p>
                  <p className="text-emerald-400/90 font-mono text-sm break-all">
                    {ed.resolved_path != null ? String(ed.resolved_path) : "— (save to a path or open a file with full path in title)"}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-slate-500 text-xs uppercase mb-2">Per-file stats (when path resolves)</p>
                <pre className="text-xs p-4 rounded-md border border-slate-800 bg-slate-900/70 text-slate-300 overflow-x-auto whitespace-pre-wrap">
                  {fs ? fmtStats(fs) : "No resolvable path — stats unavailable."}
                </pre>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="flex flex-row items-center gap-2">
          <HardDrive className="h-5 w-5 text-amber-500" />
          <CardTitle className="text-white">Probe path manually</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-slate-400 text-sm">
            Calls <code className="text-slate-300">GET /api/file/stats?path=…</code> — useful for any file on disk, not only the
            active tab.
          </p>
          <div className="flex flex-col sm:flex-row gap-2">
            <Input
              value={manualPath}
              onChange={(e) => setManualPath(e.target.value)}
              placeholder="C:\path\to\file.txt"
              className="bg-slate-900 border-slate-700 text-slate-100 font-mono text-sm"
            />
            <Button
              type="button"
              onClick={() => manualPath.trim() && manualStats.mutate(manualPath.trim())}
              disabled={!manualPath.trim() || manualStats.isPending}
            >
              Stat file
            </Button>
          </div>
          {manualStats.data && (
            <pre className="text-xs p-4 rounded-md border border-slate-800 bg-slate-900/70 text-slate-300 overflow-x-auto whitespace-pre-wrap">
              {fmtStats(manualStats.data as Record<string, unknown>)}
            </pre>
          )}
          {manualStats.isError && (
            <p className="text-red-400 text-sm">{(manualStats.error as Error).message}</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
