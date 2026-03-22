import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { postMcpInvoke } from "@/lib/api";
import { Terminal, Play } from "lucide-react";

const TOOL_OPTIONS = [
  "file_ops",
  "text_ops",
  "tab_ops",
  "session_ops",
  "linting_ops",
  "display_ops",
  "plugin_ops",
  "status_ops",
] as const;

const ARG_PRESETS: Record<string, string> = {
  file_ops: `{\n  "operation": "info"\n}`,
  text_ops: `{\n  "operation": "find",\n  "text": "TODO"\n}`,
  tab_ops: `{\n  "operation": "list"\n}`,
  session_ops: `{\n  "operation": "list"\n}`,
  linting_ops: `{\n  "operation": "tools"\n}`,
  display_ops: `{\n  "operation": "theme_status"\n}`,
  plugin_ops: `{\n  "operation": "discover",\n  "search_term": "xml",\n  "limit": 10\n}`,
  status_ops: `{\n  "operation": "health_check"\n}`,
};

export function Operations() {
  const [tool, setTool] = useState<string>("file_ops");
  const [argsJson, setArgsJson] = useState(ARG_PRESETS.file_ops);

  const run = useMutation({
    mutationFn: async () => {
      let args: Record<string, unknown>;
      try {
        args = JSON.parse(argsJson) as Record<string, unknown>;
      } catch (e) {
        throw new Error(`Invalid JSON: ${(e as Error).message}`);
      }
      return postMcpInvoke(tool, args);
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Tool operations</h2>
        <p className="text-slate-400 text-sm mt-1">
          HTTP bridge to <code className="text-slate-300">POST /api/mcp/invoke</code> — same payloads as MCP{" "}
          <code className="text-slate-300">call_tool</code>. Only whitelisted portmanteau tools are accepted.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="flex flex-row items-center gap-2">
          <Terminal className="h-5 w-5 text-green-400" />
          <CardTitle className="text-white">Invoke</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-3 items-end">
            <div>
              <label className="text-xs text-slate-500 block mb-1">Tool</label>
              <select
                value={tool}
                onChange={(e) => {
                  const t = e.target.value;
                  setTool(t);
                  setArgsJson(ARG_PRESETS[t] ?? `{}`);
                }}
                className="bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-100"
              >
                {TOOL_OPTIONS.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <Button
              type="button"
              onClick={() => run.mutate()}
              disabled={run.isPending}
            >
              <Play className="h-4 w-4 mr-2" />
              Run
            </Button>
          </div>
          <div>
            <label className="text-xs text-slate-500 block mb-1">Arguments (JSON)</label>
            <textarea
              value={argsJson}
              onChange={(e) => setArgsJson(e.target.value)}
              rows={12}
              className="w-full font-mono text-xs bg-slate-900 border border-slate-800 rounded-md p-3 text-slate-200"
            />
          </div>
          {run.isError && (
            <p className="text-red-400 text-sm whitespace-pre-wrap">{(run.error as Error).message}</p>
          )}
          {run.data && (
            <pre className="text-xs p-4 rounded-md border border-slate-800 bg-slate-900/70 text-slate-300 overflow-x-auto whitespace-pre-wrap max-h-[480px]">
              {JSON.stringify(run.data, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
