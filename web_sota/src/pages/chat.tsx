import {
  Bot,
  Download,
  Eraser,
  Loader2,
  Send,
  Sparkles,
  User,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { apiFetch } from "@/lib/api";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  ts?: string;
};

const HISTORY_KEY = "notepadpp-mcp-chat-history";
const PERSONALITY_KEY = "notepadpp-mcp-chat-personality";
const MAX_MESSAGES = 100;

const PERSONALITIES: Record<
  string,
  { id: string; label: string; prompt: string }
> = {
  assistant: {
    id: "assistant",
    label: "Research Assistant",
    prompt:
      "You are a precise assistant for Notepad++ automation. Be concise and concrete; name exact MCP tool calls when an action is requested.",
  },
  reviewer: {
    id: "reviewer",
    label: "Expert Reviewer",
    prompt:
      "You are an expert code reviewer. Analyze files and edits critically, list issues by severity, and propose concrete fixes.",
  },
  summarizer: {
    id: "summarizer",
    label: "Quick Summarizer",
    prompt:
      "You are a summarizer. Answer with short bullet points; no preamble.",
  },
  custom: {
    id: "custom",
    label: "Custom",
    prompt: "",
  },
};

const EXAMPLE_PROMPTS = [
  "How do I open a file and find a keyword?",
  "Insert a license header at the top of the active file",
  "List my open tabs and switch to the second one",
  "Lint the current Python file and show issues",
  "Save my current workspace as a session",
  "Which plugins are installed, and what does XMLTools do?",
];

function loadHistory(): ChatMessage[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.slice(-MAX_MESSAGES) : [];
  } catch {
    return [];
  }
}

function saveHistory(messages: ChatMessage[]) {
  try {
    localStorage.setItem(
      HISTORY_KEY,
      JSON.stringify(messages.slice(-MAX_MESSAGES)),
    );
  } catch {
    // storage full or unavailable - degrade silently
  }
}

export function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>(loadHistory);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [personalityId, setPersonalityId] = useState(
    () => localStorage.getItem(PERSONALITY_KEY) ?? "assistant",
  );
  const [skillName, setSkillName] = useState<string | null>(null);
  const [providerOk, setProviderOk] = useState<boolean | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // biome-ignore lint/correctness/useExhaustiveDependencies: deps are observed state, not referenced values
  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  useEffect(() => {
    apiFetch("/api/skills")
      .then((r) => (r.ok ? r.json() : { skills: [] }))
      .then((d: { skills?: { name?: string }[] }) => {
        const first = d.skills?.[0]?.name;
        if (first) setSkillName(first);
      })
      .catch(() => setSkillName(null));
    apiFetch("/api/llm/discover")
      .then((r) => (r.ok ? r.json() : null))
      .then((d: { detected?: Record<string, unknown> } | null) => {
        setProviderOk(!!d && Object.keys(d.detected ?? {}).length > 0);
      })
      .catch(() => setProviderOk(false));
  }, []);

  const append = useCallback((msg: ChatMessage) => {
    setMessages((prev) => {
      const next = [...prev, msg].slice(-MAX_MESSAGES);
      saveHistory(next);
      return next;
    });
  }, []);

  async function send(override?: string) {
    const text = (override ?? input).trim();
    if (!text || loading) return;
    setInput("");
    setError(null);
    append({ role: "user", content: text, ts: new Date().toISOString() });
    setLoading(true);
    try {
      const personality = PERSONALITIES[personalityId];
      const context = [
        skillName
          ? `Server skill available: ${skillName}. Use it to guide Notepad++ workflows.`
          : "",
        personality.prompt,
      ]
        .filter(Boolean)
        .join("\n");
      const r = await apiFetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text, context: context || undefined }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const reply =
        typeof data.response === "string"
          ? data.response
          : JSON.stringify(data);
      append({
        role: "assistant",
        content: reply,
        ts: new Date().toISOString(),
      });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Request failed";
      setError(msg);
      append({
        role: "assistant",
        content: `Error: ${msg}`,
        ts: new Date().toISOString(),
      });
    } finally {
      setLoading(false);
    }
  }

  function exportChat() {
    const lines = messages
      .map(
        (m) =>
          `[${m.ts ?? ""}] ${m.role === "user" ? "User" : "Assistant"}: ${m.content}`,
      )
      .join("\n");
    const blob = new Blob([lines], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `notepadpp-mcp-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function clearChat() {
    setMessages([]);
    setError(null);
    localStorage.removeItem(HISTORY_KEY);
  }

  return (
    <div
      data-testid="chat-page"
      className="flex h-[calc(100vh-8rem)] flex-col space-y-4"
    >
      <div
        data-testid="chat-controls"
        className="flex flex-wrap items-center justify-between gap-3"
      >
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            LLM Chat
          </h2>
          <p className="text-sm text-slate-300">
            {skillName ? `skill:${skillName}` : "Local LLM (Ollama-compatible)"}
            {providerOk === true && (
              <span
                className="ml-2 text-emerald-400"
                data-testid="chat-provider-status"
              >
                ● provider detected
              </span>
            )}
            {providerOk === false && (
              <span
                className="ml-2 text-amber-400"
                data-testid="chat-provider-status"
              >
                ● no local LLM detected
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            data-testid="personality-select"
            className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
            value={personalityId}
            onChange={(e) => {
              setPersonalityId(e.target.value);
              localStorage.setItem(PERSONALITY_KEY, e.target.value);
            }}
          >
            {Object.values(PERSONALITIES).map((p) => (
              <option key={p.id} value={p.id}>
                {p.label}
              </option>
            ))}
          </select>
          <Button
            size="sm"
            variant="outline"
            data-testid="chat-export"
            onClick={exportChat}
            disabled={messages.length === 0}
            title="Export conversation (.txt)"
          >
            <Download className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            data-testid="chat-clear"
            onClick={clearChat}
            disabled={messages.length === 0}
            title="Clear conversation"
          >
            <Eraser className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <Card className="flex-1 border-slate-800 bg-slate-950/50 flex flex-col overflow-hidden">
        <CardContent
          ref={scrollRef}
          data-testid="chat-messages"
          className="flex-1 overflow-y-auto p-4 space-y-4"
        >
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-3">
              <Sparkles className="h-8 w-8 text-blue-400" />
              <p className="text-slate-200">
                Ask anything about Notepad++ automation: open files, edit text,
                manage tabs and sessions, lint code, or control plugins.
              </p>
              <p className="text-sm text-slate-300">
                Press Enter to send. Responses come from your local LLM.
              </p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className="flex gap-3">
              <div
                className={`h-8 w-8 rounded-full flex items-center justify-center border ${
                  m.role === "user"
                    ? "bg-slate-800 border-slate-700"
                    : "bg-blue-900/20 border-blue-800"
                }`}
              >
                {m.role === "user" ? (
                  <User className="h-4 w-4 text-slate-300" />
                ) : (
                  <Bot className="h-4 w-4 text-blue-400" />
                )}
              </div>
              <div className="flex-1 text-sm text-slate-200 bg-slate-900/40 p-3 rounded-md border border-slate-800 whitespace-pre-wrap">
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="h-8 w-8 rounded-full bg-blue-900/20 flex items-center justify-center border border-blue-800">
                <Bot className="h-4 w-4 text-blue-400" />
              </div>
              <div className="flex items-center text-sm text-slate-300">
                <Loader2 className="h-4 w-4 animate-spin mr-2" /> Thinking...
              </div>
            </div>
          )}
          {error && <p className="text-sm text-red-400">{error}</p>}
        </CardContent>
        <div className="p-4 border-t border-slate-800 bg-slate-900/30">
          <div
            data-testid="example-prompts"
            className="mb-3 flex flex-wrap gap-2"
          >
            {EXAMPLE_PROMPTS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => send(p)}
                className="text-xs text-slate-200 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 rounded-full px-3 py-1 transition-colors"
              >
                {p}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              data-testid="chat-input"
              className="flex-1 bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-sm text-white focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
              placeholder="e.g. Open README.md and insert a header..."
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
              data-testid="chat-send"
              className="bg-blue-600 hover:bg-blue-700"
              type="button"
              onClick={() => send()}
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
