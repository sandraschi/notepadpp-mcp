import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { useState, useEffect } from "react";

function LLMSettings() {
    const [providers, setProviders] = useState<Record<string, {name:string}[]>>({});
    const [selectedProvider, setSelectedProvider] = useState("ollama");
    const [selectedModel, setSelectedModel] = useState("");
    const [status, setStatus] = useState<"loading"|"ready"|"error">("loading");
    useEffect(() => {
        fetch("/api/llm/providers").then(r => r.json()).then(d => {
            setProviders(d);
            const savedP = localStorage.getItem("llm_provider") || "ollama";
            const savedM = localStorage.getItem("llm_model") || "";
            setSelectedProvider(savedP);
            const models = d[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
            setSelectedModel(savedM && models.some((m:{name:string}) => m.name === savedM) ? savedM : (models[0]?.name || ""));
            setStatus(models.length > 0 ? "ready" : "error");
        }).catch(() => {
            setProviders({ ollama: [{name:"llama3.2:3b"}] });
            setSelectedModel(localStorage.getItem("llm_model") || "llama3.2:3b");
            setStatus("ready");
        });
    }, []);
    const save = (p:string, m:string) => { localStorage.setItem("llm_provider", p); localStorage.setItem("llm_model", m); };
    const models = providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
    return (
        <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
                <CardTitle className="text-white">Local LLM</CardTitle>
                <CardDescription className="text-slate-400">Provider and model selection</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid gap-2">
                    <label className="text-sm font-medium text-slate-300">Provider</label>
                    <select className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
                        value={selectedProvider} onChange={(e) => { setSelectedProvider(e.target.value); save(e.target.value, ""); }}>
                        <option value="ollama">Ollama</option>
                        <option value="lm_studio">LM Studio</option>
                    </select>
                </div>
                <div className="grid gap-2">
                    <label className="text-sm font-medium text-slate-300">Model</label>
                    <select className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
                        value={selectedModel} onChange={(e) => { setSelectedModel(e.target.value); save(selectedProvider, e.target.value); }}>
                        {models.map((m) => <option key={m.name} value={m.name}>{m.name}</option>)}
                    </select>
                </div>
            </CardContent>
        </Card>
    );
}

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

      <LLMSettings />
    </div>
  );
}
