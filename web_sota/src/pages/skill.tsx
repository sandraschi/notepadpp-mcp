import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BookOpen, Loader2 } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface SkillEntry {
  name: string;
  uri: string;
}

export function Skill() {
  const [skills, setSkills] = useState<SkillEntry[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [contentLoading, setContentLoading] = useState(false);

  useEffect(() => {
    apiFetch("/api/skills")
      .then((res) => (res.ok ? res.json() : { skills: [] }))
      .then((data: { skills?: SkillEntry[] }) => {
        setSkills(data.skills ?? []);
        if (data.skills?.length && !selected) setSelected(data.skills[0].name);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selected) return;
    setContentLoading(true);
    apiFetch(`/api/skills/${encodeURIComponent(selected)}`)
      .then((res) => (res.ok ? res.json() : { content: "" }))
      .then((data: { content?: string }) => {
        setContent(data.content ?? "");
        setContentLoading(false);
      })
      .catch(() => setContentLoading(false));
  }, [selected]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Skill</h2>
        <p className="text-slate-400">
          Anthropic-style skill content (FastMCP 3.1 resources) so clients know how to use this server.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-blue-400" />
            <CardTitle className="text-white text-md">Skill content</CardTitle>
          </div>
          <CardDescription className="text-slate-400">
            Select a skill to render SKILL.md. If none are listed, the server does not expose skills yet.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-slate-500 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading skills…
            </p>
          ) : skills.length === 0 ? (
            <p className="text-slate-500">No skills exposed by this server.</p>
          ) : (
            <>
              <div className="flex gap-2 flex-wrap">
                {skills.map((s) => (
                  <button
                    key={s.name}
                    type="button"
                    onClick={() => setSelected(s.name)}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      selected === s.name ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-300 hover:bg-slate-700"
                    }`}
                  >
                    {s.name}
                  </button>
                ))}
              </div>
              <div className="prose prose-invert prose-slate prose-sm max-w-none border border-slate-600/80 rounded-md p-4 bg-slate-900 text-slate-200 prose-p:text-slate-300 prose-headings:text-slate-100 prose-code:text-amber-200 min-h-[200px]">
                {contentLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin text-slate-500" />
                ) : (
                  <ReactMarkdown>{content}</ReactMarkdown>
                )}
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
