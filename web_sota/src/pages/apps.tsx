import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LayoutGrid, Loader2, ExternalLink } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface FleetEntry {
  port: number;
  url: string;
  health_url: string;
  reachable: boolean;
  health?: Record<string, unknown> | null;
}

interface FleetMeta {
  total_ports_registered?: number;
  ports_probed?: number;
  truncated?: boolean;
  max_ports_cap?: number;
}

export function Apps() {
  const [fleet, setFleet] = useState<FleetEntry[]>([]);
  const [fleetMeta, setFleetMeta] = useState<FleetMeta | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    const t = window.setTimeout(() => ac.abort(), 60000);
    apiFetch("/api/fleet", { signal: ac.signal })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: { fleet?: FleetEntry[]; fleet_meta?: FleetMeta }) => {
        setFleet(data.fleet ?? []);
        setFleetMeta(data.fleet_meta ?? null);
        setLoading(false);
      })
      .catch((err: unknown) => {
        const msg =
          err instanceof DOMException && err.name === "AbortError"
            ? "Fleet probe timed out (60s). Is the bridge on 10815 running?"
            : "Fleet discovery failed (bridge on 10815? auth?)";
        setError(msg);
        setLoading(false);
      })
      .finally(() => {
        window.clearTimeout(t);
      });
    return () => {
      ac.abort();
      window.clearTimeout(t);
    };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Apps Hub</h2>
        <p className="text-slate-400">Probe fleet registry ports for <code className="text-slate-500">/api/health</code>.</p>
      </div>

      {error && <p className="text-sm text-amber-400">{error}</p>}
      {fleetMeta?.truncated && (
        <p className="text-sm text-slate-500">
          Showing {fleetMeta.ports_probed ?? fleet.length} of {fleetMeta.total_ports_registered} ports
          (cap {fleetMeta.max_ports_cap}; set NOTEPADPP_FLEET_MAX_PORTS to raise).
        </p>
      )}

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <LayoutGrid className="h-5 w-5 text-blue-400" />
            <CardTitle className="text-white">Fleet status</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-slate-500 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Scanning…
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500">
                    <th className="py-2 pr-4">Port</th>
                    <th className="py-2 pr-4">Reachable</th>
                    <th className="py-2 pr-4">Health</th>
                    <th className="py-2">Open</th>
                  </tr>
                </thead>
                <tbody>
                  {fleet.map((row) => (
                    <tr key={row.port} className="border-b border-slate-800/60">
                      <td className="py-2 pr-4 font-mono text-slate-300">{row.port}</td>
                      <td className="py-2 pr-4">
                        <span className={row.reachable ? "text-emerald-400" : "text-slate-600"}>
                          {row.reachable ? "yes" : "no"}
                        </span>
                      </td>
                      <td className="py-2 pr-4 text-slate-500 truncate max-w-xs">
                        {row.health ? JSON.stringify(row.health) : "—"}
                      </td>
                      <td className="py-2">
                        <a
                          href={row.url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300"
                        >
                          <ExternalLink className="h-3 w-3" />
                          UI
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
