import { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

function LLMSettings() {
  const [providers, setProviders] = useState<
    Record<string, { name: string }[]>
  >({});
  const [selectedProvider, setSelectedProvider] = useState("ollama");
  const [selectedModel, setSelectedModel] = useState("");
  const [status, setStatus] = useState<"probing" | "detected" | "not_found">(
    "probing",
  );
  useEffect(() => {
    apiFetch("/api/llm/providers")
      .then((r) => (r.ok ? r.json() : null))
      .then(
        (
          d: {
            providers?: Record<string, { models: { name: string }[] }>;
          } | null,
        ) => {
          if (!d?.providers) {
            setStatus("not_found");
            setProviders({});
            return;
          }
          const byName: Record<string, { name: string }[]> = {};
          for (const [key, value] of Object.entries(d.providers)) {
            byName[key === "ollama" ? "ollama" : "lm_studio"] = (
              value.models ?? []
            ).map((m) => ({
              name: m.name,
            }));
          }
          setProviders(byName);
          const hasAny = Object.values(byName).some((list) => list.length > 0);
          setStatus(hasAny ? "detected" : "not_found");
          const savedP = localStorage.getItem("llm_provider") || "ollama";
          const savedM = localStorage.getItem("llm_model") || "";
          setSelectedProvider(savedP);
          const models =
            byName[savedP === "ollama" ? "ollama" : "lm_studio"] || [];
          setSelectedModel(
            savedM && models.some((m) => m.name === savedM)
              ? savedM
              : models[0]?.name || "",
          );
        },
      )
      .catch(() => {
        setStatus("not_found");
        setProviders({});
        setSelectedModel("");
      });
  }, []);
  const save = (p: string, m: string) => {
    localStorage.setItem("llm_provider", p);
    localStorage.setItem("llm_model", m);
  };
  const models =
    providers[selectedProvider === "ollama" ? "ollama" : "lm_studio"] || [];
  return (
    <Card className="border-slate-800 bg-slate-950/50">
      <CardHeader>
        <CardTitle className="text-white">Local LLM</CardTitle>
        <CardDescription className="text-slate-400">
          Provider and model selection
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-300" data-testid="llm-provider-status">
          {status === "probing" && "Probing local LLM providers..."}
          {status === "detected" &&
            "Provider detected (Ollama / LM Studio / vLLM)"}
          {status === "not_found" &&
            "No local LLM detected - start Ollama or LM Studio to enable AI features"}
        </p>
        <div className="grid gap-2">
          <label className="text-sm font-medium text-slate-300">Provider</label>
          <select
            data-testid="llm-provider-select"
            className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
            value={selectedProvider}
            onChange={(e) => {
              setSelectedProvider(e.target.value);
              save(e.target.value, "");
            }}
          >
            <option value="ollama">Ollama</option>
            <option value="lm_studio">LM Studio</option>
          </select>
        </div>
        <div className="grid gap-2">
          <label className="text-sm font-medium text-slate-300">Model</label>
          <select
            data-testid="llm-model-select"
            className="h-9 w-full rounded-md border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
            value={selectedModel}
            onChange={(e) => {
              setSelectedModel(e.target.value);
              save(selectedProvider, e.target.value);
            }}
          >
            {models.length === 0 && (
              <option value="">No models detected</option>
            )}
            {models.map((m) => (
              <option key={m.name} value={m.name}>
                {m.name}
              </option>
            ))}
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
        <h2 className="text-2xl font-bold tracking-tight text-white">
          Settings
        </h2>
        <p className="text-slate-400">
          Bridge authentication and environment (not stored in the browser)
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <CardTitle className="text-white">Web dashboard auth</CardTitle>
          <CardDescription className="text-slate-400">
            The FastAPI bridge uses HTTP Basic auth. Defaults match other fleet
            servers unless you override env vars.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-slate-400">
          <p>
            <span className="text-slate-300">Server:</span>{" "}
            <code className="text-slate-500">MCP_WEB_USER</code>,{" "}
            <code className="text-slate-500">MCP_WEB_PASSWORD</code>
          </p>
          <p>
            <span className="text-slate-300">Vite (this UI):</span>{" "}
            <code className="text-slate-500">VITE_MCP_WEB_USER</code>,{" "}
            <code className="text-slate-500">VITE_MCP_WEB_PASSWORD</code> in{" "}
            <code className="text-slate-500">web_sota/.env.local</code>
          </p>
          <p>
            <span className="text-slate-300">Fleet registry (optional):</span>{" "}
            <code className="text-slate-500">NOTEPADPP_FLEET_REGISTRY</code> →
            path to <code className="text-slate-500">webapp-registry.json</code>
          </p>
        </CardContent>
      </Card>

      <LLMSettings />
    </div>
  );
}
