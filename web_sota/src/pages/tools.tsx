import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Wrench, Loader2, ChevronDown, ChevronRight } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface ToolEntry {
  name: string;
  summary?: string;
  description?: string;
}

export function Tools() {
  const [tools, setTools] = useState<ToolEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    apiFetch("/api/tools")
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: { tools?: ToolEntry[] }) => {
        setTools(data.tools ?? []);
        setLoading(false);
      })
      .catch(() => {
        setError("Could not load tools (is the bridge running on 10815?)");
        setLoading(false);
      });
  }, []);

  function toggle(name: string) {
    setExpanded((prev) => ({ ...prev, [name]: !prev[name] }));
  }

  function preview(t: ToolEntry): string {
    const s = (t.summary ?? "").trim();
    if (s) return s;
    const d = (t.description ?? "").trim();
    if (!d) return "No description provided";
    const line = d.split(/\r?\n/).find((x) => x.trim()) ?? "";
    return line.length > 220 ? `${line.slice(0, 219)}…` : line;
  }

  const hasLongDoc = (t: ToolEntry) => (t.description ?? "").length > (t.summary ?? "").length + 20;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Tools Hub</h2>
        <p className="text-slate-400">One-line summary per tool; expand for full MCP docstring.</p>
      </div>

      {error && (
        <p className="text-sm text-amber-400 border border-amber-900/40 rounded-md p-3 bg-amber-950/20">{error}</p>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {tools.map((tool) => {
          const open = !!expanded[tool.name];
          const longDoc = hasLongDoc(tool);
          return (
            <Card key={tool.name} className="border-slate-800 bg-slate-950/50 hover:bg-slate-900/50 transition-colors">
              <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2 gap-2">
                <div className="space-y-1 min-w-0 flex-1">
                  <CardTitle className="text-sm font-medium text-white font-mono">{tool.name}</CardTitle>
                  <p className="text-xs text-slate-400 leading-relaxed">{preview(tool)}</p>
                </div>
                <Wrench className="h-4 w-4 text-blue-500 shrink-0 mt-0.5" />
              </CardHeader>
              {longDoc && (
                <CardContent className="pt-0">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="text-slate-500 hover:text-slate-300 h-8 px-2 -ml-2"
                    onClick={() => toggle(tool.name)}
                  >
                    {open ? (
                      <ChevronDown className="h-3 w-3 mr-1" />
                    ) : (
                      <ChevronRight className="h-3 w-3 mr-1" />
                    )}
                    {open ? "Hide full docstring" : "Full docstring"}
                  </Button>
                  {open && (
                    <pre className="mt-2 max-h-64 overflow-y-auto rounded-md border border-slate-600/80 bg-slate-900 p-3 text-[12px] leading-relaxed text-slate-200 whitespace-pre-wrap font-mono shadow-inner">
                      {tool.description}
                    </pre>
                  )}
                </CardContent>
              )}
            </Card>
          );
        })}
      </div>

      {loading && (
        <div className="flex items-center justify-center p-12 gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading tools…
        </div>
      )}
    </div>
  );
}
