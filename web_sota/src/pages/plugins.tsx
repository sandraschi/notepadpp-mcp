import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  fetchPluginsDiscover,
  fetchPluginsInstalled,
  postPluginInstall,
} from "@/lib/api";
import { Puzzle, Search, HardDrive, Download } from "lucide-react";

export function Plugins() {
  const qc = useQueryClient();
  const [q, setQ] = useState("");
  const [discoverQ, setDiscoverQ] = useState("");

  const installed = useQuery({
    queryKey: ["plugins", "installed"],
    queryFn: fetchPluginsInstalled,
    refetchInterval: 15000,
  });

  const discover = useQuery({
    queryKey: ["plugins", "discover", discoverQ],
    queryFn: () => fetchPluginsDiscover(discoverQ, { limit: 40 }),
    enabled: discoverQ.trim().length >= 2,
  });

  const installMut = useMutation({
    mutationFn: postPluginInstall,
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ["plugins", "installed"] });
    },
  });

  type InstalledRow = {
    name: string;
    path: string;
    directory?: string;
    catalog_match?: boolean;
    catalog_display_name?: string;
    description_one_line?: string;
  };

  const rows =
    installed.data?.plugins && Array.isArray(installed.data.plugins as unknown[])
      ? (installed.data.plugins as InstalledRow[])
      : [];

  const catalog =
    discover.data &&
    typeof discover.data === "object" &&
    discover.data !== null &&
    "result" in discover.data
      ? (discover.data as {
          result?: {
            plugins?: {
              name?: string;
              description?: string;
              category?: string;
              version?: string;
            }[];
          };
        }).result?.plugins ?? []
      : [];

  const scrollH = "h-[min(32rem,calc(100vh-13rem))]";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight text-white">Plugins</h2>
        <p className="text-slate-400 text-sm mt-1">
          Pick a tab: Installed lists DLLs on disk with catalog descriptions when matched; Catalog searches{" "}
          <code className="text-slate-300">pl.x64.json</code>. Install uses{" "}
          <code className="text-slate-300">plugin_ops</code> (Plugin Admin — manual finish).
        </p>
      </div>

      <Card className="border-slate-800 bg-slate-950/50">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-lg">Notepad++ plugins</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="installed" className="w-full">
            <TabsList className="bg-slate-900 border border-slate-800 flex w-full max-w-md h-auto gap-1 p-1">
              <TabsTrigger
                value="installed"
                className="flex-1 data-[state=active]:bg-slate-800 gap-1.5"
              >
                <HardDrive className="h-4 w-4 shrink-0 text-emerald-500" />
                Installed
              </TabsTrigger>
              <TabsTrigger value="catalog" className="flex-1 data-[state=active]:bg-slate-800 gap-1.5">
                <Puzzle className="h-4 w-4 shrink-0 text-purple-400" />
                Catalog
              </TabsTrigger>
            </TabsList>

            <TabsContent value="installed" className="mt-4 space-y-3 outline-none">
              {installed.isLoading && <p className="text-slate-400 text-sm">Loading…</p>}
              {installed.isError && (
                <p className="text-red-400 text-sm">{(installed.error as Error).message}</p>
              )}
              {typeof installed.data?.catalog_error === "string" && installed.data.catalog_error.length > 0 && (
                <p className="text-amber-400/90 text-xs">
                  Catalog fetch failed (descriptions may be empty): {installed.data.catalog_error}
                </p>
              )}
              <ScrollArea className={`${scrollH} rounded-md border border-slate-800`}>
                <table className="w-full text-sm min-w-[32rem]">
                  <thead className="sticky top-0 bg-slate-900/95 text-slate-300 z-10">
                    <tr>
                      <th className="text-left p-2 w-[8rem]">DLL / folder</th>
                      <th className="text-left p-2 w-[14rem]">Display name</th>
                      <th className="text-left p-2">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((p, i) => (
                      <tr key={`${p.name}-${i}`} className="border-t border-slate-800/80">
                        <td className="p-2 text-slate-200 align-top font-mono text-xs">{p.name}</td>
                        <td className="p-2 text-slate-300 align-top text-xs">
                          {p.catalog_display_name?.trim() ? p.catalog_display_name : "—"}
                        </td>
                        <td className="p-2 text-slate-400 align-top text-xs">
                          {p.description_one_line?.trim()
                            ? p.description_one_line
                            : p.catalog_match === false
                              ? "—"
                              : ""}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {rows.length === 0 && !installed.isLoading && (
                  <p className="p-4 text-slate-500 text-sm">No DLLs found or bridge unavailable.</p>
                )}
              </ScrollArea>
              <p className="text-xs text-slate-500">
                DLLs:{" "}
                {installed.data != null && "count" in installed.data && installed.data.count != null
                  ? String(installed.data.count)
                  : "—"}
                {" · "}
                catalog matched:{" "}
                {installed.data != null &&
                "catalog_matched_count" in installed.data &&
                installed.data.catalog_matched_count != null
                  ? String(installed.data.catalog_matched_count)
                  : "—"}
              </p>
            </TabsContent>

            <TabsContent value="catalog" className="mt-4 space-y-3 outline-none">
              <div className="flex flex-wrap gap-2 items-center">
                <Input
                  placeholder="Search (min 2 chars)…"
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  className="bg-slate-900 border-slate-700 text-slate-100 max-w-xl flex-1 min-w-[12rem]"
                />
                <Button
                  type="button"
                  variant="secondary"
                  className="shrink-0"
                  onClick={() => setDiscoverQ(q)}
                >
                  <Search className="h-4 w-4 mr-1" />
                  Search
                </Button>
              </div>
              {discoverQ.length < 2 && (
                <p className="text-slate-500 text-sm">Type at least two characters and click Search.</p>
              )}
              {discover.isFetching && <p className="text-slate-400 text-sm">Searching…</p>}
              {discover.isError && (
                <p className="text-red-400 text-sm">{(discover.error as Error).message}</p>
              )}
              <ScrollArea className={`${scrollH} rounded-md border border-slate-800`}>
                <ul className="divide-y divide-slate-800 min-w-0">
                  {catalog.map((pl, i) => (
                    <li key={`${pl.name}-${i}`} className="p-4 flex flex-col gap-1">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <span className="font-medium text-slate-100">{pl.name ?? "(unnamed)"}</span>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-slate-600 shrink-0"
                          disabled={installMut.isPending || !pl.name}
                          onClick={() => {
                            if (!pl.name) return;
                            if (
                              !window.confirm(
                                `Open Plugin Admin automation for "${pl.name}"? Notepad++ will be focused.`
                              )
                            )
                              return;
                            installMut.mutate(pl.name);
                          }}
                        >
                          <Download className="h-3 w-3 mr-1" />
                          Install attempt
                        </Button>
                      </div>
                      <p className="text-xs text-slate-500">{pl.category ?? ""}</p>
                      <p className="text-sm text-slate-400">{pl.description ?? ""}</p>
                    </li>
                  ))}
                </ul>
                {catalog.length === 0 && discoverQ.length >= 2 && !discover.isFetching && (
                  <p className="p-4 text-slate-500 text-sm">No matches.</p>
                )}
              </ScrollArea>
              {installMut.data && (
                <pre className="text-xs p-3 rounded-md bg-slate-900/80 text-slate-300 overflow-x-auto whitespace-pre-wrap border border-slate-800 max-h-48 overflow-y-auto">
                  {JSON.stringify(installMut.data, null, 2)}
                </pre>
              )}
              {installMut.isError && (
                <p className="text-red-400 text-sm">{(installMut.error as Error).message}</p>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
