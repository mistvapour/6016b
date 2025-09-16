import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function fetchData<T>(path: string): Promise<T> {
  const response = await fetch(`${API}${path}`);
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export default function App() {
  const [top, setTop] = useState<any[]>([]);
  const [cmp, setCmp] = useState("Altitude");
  const [bySpec, setBySpec] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [search, setSearch] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData<any[]>("/api/review/top")
      .then(setTop)
      .catch(console.error);
  }, []);

  async function doCompare() {
    setLoading(true);
    try {
      const data = await fetchData<any>(`/api/compare?q=${encodeURIComponent(cmp)}`);
      setBySpec(data.by_spec || []);
    } catch (error) {
      console.error("比较失败:", error);
    } finally {
      setLoading(false);
    }
  }

  async function doSearch() {
    setLoading(true);
    try {
      const data = await fetchData<any>(`/api/search?q=${encodeURIComponent(q)}`);
      setSearch(data.results || []);
    } catch (error) {
      console.error("搜索失败:", error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">MIL-STD-6016 Explorer</h1>
          <p className="text-muted-foreground">
            探索和分析MIL-STD-6016标准数据
          </p>
        </div>

        <Tabs defaultValue="search" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="search">搜索</TabsTrigger>
            <TabsTrigger value="compare">比较</TabsTrigger>
            <TabsTrigger value="top">热门概念</TabsTrigger>
          </TabsList>

          <TabsContent value="search" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>搜索</CardTitle>
                <CardDescription>
                  搜索概念、别名、字段或数据项
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    value={q}
                    onChange={(e) => setQ(e.target.value)}
                    placeholder="输入搜索关键词..."
                    className="flex-1"
                  />
                  <Button onClick={doSearch} disabled={loading}>
                    {loading ? "搜索中..." : "搜索"}
                  </Button>
                </div>
                
                {search.length > 0 && (
                  <div className="border rounded-lg">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>来源</TableHead>
                          <TableHead>命中名称</TableHead>
                          <TableHead>规范名称</TableHead>
                          <TableHead>规范</TableHead>
                          <TableHead>J系列</TableHead>
                          <TableHead>字</TableHead>
                          <TableHead>字段</TableHead>
                          <TableHead>位</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {search.map((r: any, i: number) => (
                          <TableRow key={i}>
                            <TableCell>
                              <Badge variant="outline">{r.source}</Badge>
                            </TableCell>
                            <TableCell className="font-medium">{r.hit_name}</TableCell>
                            <TableCell>{r.canonical_name || ""}</TableCell>
                            <TableCell>
                              {[r.code, r.edition, r.part_label].filter(Boolean).join(" ")}
                            </TableCell>
                            <TableCell>{r.j_series || ""}</TableCell>
                            <TableCell>{r.word_label || ""}</TableCell>
                            <TableCell>{r.field_name || ""}</TableCell>
                            <TableCell>
                              {r.start_bit != null ? `${r.start_bit}–${r.end_bit}` : ""}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="compare" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>比较</CardTitle>
                <CardDescription>
                  比较不同规范中的概念定义
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    value={cmp}
                    onChange={(e) => setCmp(e.target.value)}
                    placeholder="输入要比较的概念..."
                    className="flex-1"
                  />
                  <Button onClick={doCompare} disabled={loading}>
                    {loading ? "比较中..." : "比较"}
                  </Button>
                </div>
                
                {bySpec.length > 0 && (
                  <div className="border rounded-lg">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>规范</TableHead>
                          <TableHead>字段绑定</TableHead>
                          <TableHead>数据项绑定</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {bySpec.map((r: any, i: number) => (
                          <TableRow key={i}>
                            <TableCell className="font-medium">
                              {[r.code, r.edition, r.part_label].filter(Boolean).join(" ")}
                            </TableCell>
                            <TableCell>{r.field_bindings}</TableCell>
                            <TableCell>{r.data_item_bindings}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="top" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>热门概念</CardTitle>
                <CardDescription>
                  最常使用的概念和字段
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>概念</TableHead>
                        <TableHead>字段数</TableHead>
                        <TableHead>数据项数</TableHead>
                        <TableHead>消息数</TableHead>
                        <TableHead>规范数</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {top.map((r: any, i: number) => (
                        <TableRow key={i}>
                          <TableCell className="font-medium">{r.canonical_name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{r.fields}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{r.data_items}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{r.messages}</Badge>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{r.specs}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}