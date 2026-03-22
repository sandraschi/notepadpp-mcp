import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { fetchDiagnostics } from "@/lib/api";
import { Stethoscope, RefreshCw } from "lucide-react";

export function Diagnostics() {
  const q = useQuery({
    queryKey: ["diagnostics"],
    queryFn: fetchDiagnostics,
    refetchInterval: 20000,
  });

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Diagnostics</h2>
        <p className="text-slate-400 text-sm mt-1">
          Bundled <code className="text-slate-300">status_ops</code> calls: <code className="text-slate-300">health_check</code> and{" "}
          <code className="text-slate-300">system_status</code> via <code className="text-slate-300">GET /api/diagnostics</code>.
        </p>
      </div>

      <Button type="button" variant="secondary" onClick={() => void q.refetch()} disabled={q.isFetching}>
        <RefreshCw className={`h-4 w-4 mr-2 ${q.isFetching ? "animate-spin" : ""}`} />
        Refresh
      </Button>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="flex flex-row items-center gap-2">
          <Stethoscope className="h-5 w-5 text-rose-400" />
          <CardTitle className="text-white">status_ops bundle</CardTitle>
        </CardHeader>
        <CardContent>
          {q.isLoading && <p className="text-slate-400 text-sm">Loading…</p>}
          {q.isError && <p className="text-red-400 text-sm">{(q.error as Error).message}</p>}
          {q.data && (
            <pre className="text-xs p-4 rounded-md border border-slate-800 bg-slate-900/70 text-slate-300 overflow-x-auto whitespace-pre-wrap max-h-[70vh]">
              {JSON.stringify(q.data, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
