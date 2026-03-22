import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Settings</h2>
        <p className="text-slate-400">Bridge authentication and environment (not stored in the browser)</p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Web dashboard auth</CardTitle>
          <CardDescription className="text-slate-400">
            The FastAPI bridge uses HTTP Basic auth. Defaults match other fleet servers unless you override env vars.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-400">
          <p>
            <span className="text-slate-300">Server:</span> <code className="text-slate-500">MCP_WEB_USER</code>,{" "}
            <code className="text-slate-500">MCP_WEB_PASSWORD</code>
          </p>
          <p>
            <span className="text-slate-300">Vite (this UI):</span> <code className="text-slate-500">VITE_MCP_WEB_USER</code>,{" "}
            <code className="text-slate-500">VITE_MCP_WEB_PASSWORD</code> in <code className="text-slate-500">web_sota/.env.local</code>
          </p>
          <p>
            <span className="text-slate-300">Fleet registry (optional):</span>{" "}
            <code className="text-slate-500">NOTEPADPP_FLEET_REGISTRY</code> → path to <code className="text-slate-500">webapp-registry.json</code>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
