import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import ReactMarkdown from "react-markdown";
import { fetchDocsOverview, fetchHttpRoutes, fetchMcpMeta } from "@/lib/api";
import { BookOpen, ListTree, Server } from "lucide-react";

type Section = { id: string; title: string; body_md: string };
type RestEp = { method: string; path: string; auth: boolean; summary: string };

export function Help() {
  const docs = useQuery({ queryKey: ["docs", "overview"], queryFn: fetchDocsOverview });
  const meta = useQuery({ queryKey: ["mcp", "meta"], queryFn: fetchMcpMeta });
  const routes = useQuery({ queryKey: ["http", "routes"], queryFn: fetchHttpRoutes });

  const manifest = docs.data as Record<string, unknown> | undefined;
  const sections = (manifest?.sections as Section[] | undefined) ?? [];
  const restTable = (manifest?.rest_endpoints as RestEp[] | undefined) ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Help &amp; reference</h2>
        <p className="text-slate-400 text-sm mt-1">
          Pulled from the Python bridge: <code className="text-slate-300">/api/docs/overview</code>,{" "}
          <code className="text-slate-300">/api/mcp/meta</code>, <code className="text-slate-300">/api/http/routes</code>.
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="flex flex-row items-center gap-2">
          <Server className="h-5 w-5 text-blue-400" />
          <CardTitle className="text-white">Live MCP server</CardTitle>
        </CardHeader>
        <CardContent>
          {meta.isLoading && <p className="text-slate-400 text-sm">Loading meta…</p>}
          {meta.isError && <p className="text-red-400 text-sm">{(meta.error as Error).message}</p>}
          {meta.data && (
            <div className="space-y-2 text-sm">
              <p className="text-slate-300">
                <span className="text-slate-500">Name:</span>{" "}
                <span className="text-white font-medium">{String(meta.data.name ?? "—")}</span>
              </p>
              <p className="text-slate-300">
                <span className="text-slate-500">Registered tools:</span>{" "}
                <span className="text-emerald-400">{String(meta.data.tool_count ?? "—")}</span>
              </p>
              {typeof meta.data.instructions_preview === "string" && (
                <div>
                  <p className="text-slate-500 text-xs uppercase mb-1">Instructions preview</p>
                  <pre className="text-xs p-3 rounded-md bg-slate-900/80 border border-slate-800 text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                    {meta.data.instructions_preview}
                  </pre>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Tabs defaultValue="topics" className="w-full">
        <TabsList className="bg-slate-900 border border-slate-800 flex flex-wrap h-auto gap-1 p-1">
          <TabsTrigger value="topics" className="data-[state=active]:bg-slate-800">
            <BookOpen className="h-4 w-4 mr-1 inline" />
            Topics
          </TabsTrigger>
          <TabsTrigger value="rest" className="data-[state=active]:bg-slate-800">
            REST API
          </TabsTrigger>
          <TabsTrigger value="routes" className="data-[state=active]:bg-slate-800">
            <ListTree className="h-4 w-4 mr-1 inline" />
            FastAPI routes
          </TabsTrigger>
        </TabsList>

        <TabsContent value="topics" className="mt-4 space-y-4">
          {docs.isLoading && <p className="text-slate-400 text-sm">Loading documentation…</p>}
          {docs.isError && <p className="text-red-400 text-sm">{(docs.error as Error).message}</p>}
          {sections.map((sec) => (
            <Card key={sec.id} className="border-slate-800 bg-slate-950/50">
              <CardHeader>
                <CardTitle className="text-white text-lg">{sec.title}</CardTitle>
              </CardHeader>
              <CardContent className="markdown-help text-sm text-slate-300 [&_h2]:text-white [&_h2]:text-base [&_h2]:font-semibold [&_h2]:mt-4 [&_h2]:mb-2 [&_p]:leading-relaxed [&_ul]:list-disc [&_ul]:pl-5 [&_li]:my-1 [&_table]:w-full [&_th]:text-left [&_th]:border [&_td]:border [&_th]:border-slate-700 [&_td]:border-slate-700 [&_th]:p-2 [&_td]:p-2 [&_code]:text-emerald-300 [&_code]:bg-slate-900 [&_code]:px-1 [&_code]:rounded">
                <ReactMarkdown>{sec.body_md}</ReactMarkdown>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="rest" className="mt-4">
          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white text-md">Documented REST endpoints</CardTitle>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              <table className="w-full text-sm text-left">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400">
                    <th className="py-2 pr-2">Method</th>
                    <th className="py-2 pr-2">Path</th>
                    <th className="py-2 pr-2">Auth</th>
                    <th className="py-2">Summary</th>
                  </tr>
                </thead>
                <tbody>
                  {restTable.map((row) => (
                    <tr key={`${row.method}-${row.path}`} className="border-b border-slate-800/80">
                      <td className="py-2 pr-2 font-mono text-amber-400/90">{row.method}</td>
                      <td className="py-2 pr-2 font-mono text-slate-300">{row.path}</td>
                      <td className="py-2 pr-2">{row.auth ? "Yes" : "No"}</td>
                      <td className="py-2 text-slate-400">{row.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="routes" className="mt-4">
          <Card className="border-slate-800 bg-slate-950/50">
            <CardHeader>
              <CardTitle className="text-white text-md">Actual FastAPI routes</CardTitle>
            </CardHeader>
            <CardContent>
              {routes.isLoading && <p className="text-slate-400 text-sm">Loading…</p>}
              {routes.isError && <p className="text-red-400 text-sm">{(routes.error as Error).message}</p>}
              {routes.data?.routes && (
                <div className="max-h-[60vh] overflow-y-auto">
                  <table className="w-full text-sm">
                    <tbody>
                      {routes.data.routes.map((r) => (
                        <tr key={`${r.method}-${r.path}`} className="border-b border-slate-800/60">
                          <td className="py-1 pr-3 font-mono text-amber-400/90">{r.method}</td>
                          <td className="py-1 font-mono text-slate-300">{r.path}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
