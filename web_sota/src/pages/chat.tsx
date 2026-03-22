import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send, Bot, User, Loader2 } from "lucide-react";
import { apiFetch } from "@/lib/api";

export function Chat() {
  const [input, setInput] = useState("");
  const [reply, setReply] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function send() {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const r = await apiFetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: input }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setReply(typeof data.response === "string" ? data.response : JSON.stringify(data));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
      setReply(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">LLM Chat</h2>
          <p className="text-slate-400">POST /api/chat (router stub; extend with local LLM as needed)</p>
        </div>
      </div>

      <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden">
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          <div className="flex gap-3">
            <div className="h-8 w-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
              <User className="h-4 w-4 text-slate-400" />
            </div>
            <div className="flex-1 space-y-1">
              <p className="text-sm text-slate-300">Ask in natural language; the bridge returns a routing hint.</p>
            </div>
          </div>

          {reply && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-blue-900/20 flex items-center justify-center border border-blue-800">
                <Bot className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex-1 text-sm text-slate-300 bg-blue-950/10 p-3 rounded-md border border-blue-900/30 whitespace-pre-wrap">
                {reply}
              </div>
            </div>
          )}

          {error && <p className="text-sm text-red-400">{error}</p>}
        </CardContent>
        <div className="p-4 border-t border-slate-800 bg-slate-900/30">
          <div className="flex gap-2">
            <input
              className="flex-1 bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
              placeholder="e.g. Open README.md and insert a header…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
            />
            <Button
              size="icon"
              className="bg-blue-600 hover:bg-blue-700"
              type="button"
              onClick={send}
              disabled={loading}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
