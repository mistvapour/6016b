import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Search, GitCompare, TrendingUp, Database, FileText, Zap, Globe, Shield, Filter } from "lucide-react";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

const API = import.meta.env.VITE_API_BASE_URL || ""; // 开发期推荐走 Vite 代理，避免 CORS

async function fetchData<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export default function App() {
  const [top, setTop] = useState<any[]>([]);
  const [cmp, setCmp] = useState("Altitude");
  const [bySpec, setBySpec] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [search, setSearch] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // 视图模式：concept（原有列）| word（word_label 专用列）
  const [viewMode, setViewMode] = useState<"concept" | "word">("concept");

  // J 系列与模糊开关
  const [jSeries, setJSeries] = useState<string>("all"); // "all"=全部
  const [fuzzy, setFuzzy] = useState<boolean>(true);

  useEffect(() => {
    fetchData<any[]>("/api/review/top")
      .then(setTop)
      .catch((err) => {
        console.warn("无法加载热门概念，可能是后端未启动或跨域：", err);
        // 提供占位数据，保证页面不空
        setTop([
          { canonical_name: "Altitude", fields: 15, data_items: 8, messages: 3, specs: 2 },
          { canonical_name: "Heading", fields: 12, data_items: 6, messages: 2, specs: 2 },
          { canonical_name: "Speed", fields: 10, data_items: 5, messages: 2, specs: 1 },
        ]);
      });
  }, []);

  async function doCompare() {
    if (!cmp.trim()) {
      setError("请输入要比较的概念");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await fetchData<any>(`/api/compare?q=${encodeURIComponent(cmp)}`);
      setBySpec(data.by_spec || []);
    } catch (e) {
      setError("比较失败，请检查网络连接或稍后重试");
      console.error("比较失败:", e);
    } finally {
      setLoading(false);
    }
  }

  async function doSearch() {
    if (!q.trim() && jSeries === "all") {
      setError("请输入搜索关键词或选择 J 系列");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.set("q", q.trim());
      if (jSeries && jSeries !== "all") params.set("j", jSeries);
      params.set("fuzzy", fuzzy ? "1" : "0");
      const data = await fetchData<any>(`/api/search?${params.toString()}`);
      setSearch(data.results || []);
      setViewMode("concept"); // 切回概念/字段视图
    } catch (e) {
      setError("搜索失败，后端可能未启动或网络连接问题");
      console.error("搜索失败:", e);
      // 提供一些模拟数据用于演示
      setSearch([
        {
          source: "示例来源",
          hit_name: q || "示例命中",
          canonical_name: "示例规范名称",
          code: "MIL-STD-6016",
          edition: "A", 
          part_label: "Part 1",
          j_series: jSeries !== "all" ? jSeries : "J3",
          word_label: "示例字",
          field_name: "示例字段",
          start_bit: 0,
          end_bit: 15
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function doSearchWord() {
    if (!q.trim() && jSeries === "all") {
      setError("请输入 word_label 或选择 J 系列");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (q.trim()) params.set("q", q.trim());
      if (jSeries && jSeries !== "all") params.set("j", jSeries);
      params.set("fuzzy", fuzzy ? "1" : "0");
      const data = await fetchData<any>(`/api/word/search?${params.toString()}`);
      setSearch(data.results || []);
      setViewMode("word"); // 切换到按字视图
    } catch (e) {
      setError("按字搜索失败，后端可能未启动或数据库字段不匹配");
      console.error("按字搜索失败:", e);
      // 提供一些模拟数据用于演示
      setSearch([
        {
          word_label: q || "示例字段",
          dfi: "DFI001",
          dui: "DUI001", 
          descriptor: "示例字段描述",
          position_bits: "0-15",
          resolution_coding: "示例编码",
          j_series: jSeries !== "all" ? jSeries : "J3",
          code: "MIL-STD-6016",
          edition: "A",
          part_label: "Part 1"
        }
      ]);
      setViewMode("word");
    } finally {
      setLoading(false);
    }
  }

  function onEnter(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") doSearch();
  }

  return (
    <div className="relative min-h-screen w-full overflow-x-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* 背景 */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply blur-xl opacity-10" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply blur-xl opacity-10" />
        <div className="absolute top-40 left-1/2 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply blur-xl opacity-10 hidden md:block" />
      </div>

      <main className="relative mx-auto w-full max-w-[1200px] px-6 py-6">
        {/* 头部 */}
        <div className="text-center space-y-4 pb-4">
          <div className="flex items-center justify-center gap-4 mb-3">
            <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
              MIL-STD-6016 Explorer
            </h1>
          </div>
          <p className="text-lg text-slate-600 leading-relaxed">
            探索和分析MIL-STD-6016标准数据，发现军事通信协议的深层洞察
          </p>
          <div className="flex items-center justify-center gap-8 text-sm text-slate-500">
            <div className="flex items-center gap-2"><Database className="h-4 w-4" /><span>实时数据</span></div>
            <div className="flex items-center gap-2"><Zap className="h-4 w-4" /><span>快速搜索</span></div>
            <div className="flex items-center gap-2"><Globe className="h-4 w-4" /><span>标准兼容</span></div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="search" className="w-full pb-8">
          <TabsList className="grid w-full grid-cols-3 bg-white/80 backdrop-blur-sm border border-slate-200 shadow mb-4">
            <TabsTrigger value="search" className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white">
              <Search className="h-4 w-4" /> 搜索
            </TabsTrigger>
            <TabsTrigger value="compare" className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white">
              <GitCompare className="h-4 w-4" /> 比较
            </TabsTrigger>
            <TabsTrigger value="top" className="flex items-center gap-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white">
              <TrendingUp className="h-4 w-4" /> 热门概念
            </TabsTrigger>
          </TabsList>

          {/* 搜索 */}
          <TabsContent value="search" className="space-y-4">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow">
              <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
                <CardTitle className="flex items-center gap-2 text-xl">
                  <Search className="h-5 w-5 text-blue-600" /> 智能搜索
                </CardTitle>
                <CardDescription className="text-slate-600 text-sm">
                  关键词 + J 系列筛选；可选择模糊匹配。支持“以字搜索（word_label）”。
                </CardDescription>
              </CardHeader>

              <CardContent className="flex flex-col gap-4 p-6">
                {/* 查询条件 */}
                <div className="flex flex-wrap items-center gap-3">
                  <div className="relative flex-1 min-w-[280px]">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      value={q}
                      onChange={(e) => setQ(e.target.value)}
                      onKeyDown={onEnter}
                      placeholder="输入关键词或 word_label，如 Altitude、Heading…"
                      className="pl-10 h-12 text-lg border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                    />
                  </div>

                  {/* J 系列选择 */}
                  <div className="flex items-center gap-2">
                    <Filter className="h-4 w-4 text-slate-500" />
                    <Select value={jSeries} onValueChange={setJSeries}>
                      <SelectTrigger className="w-[140px] h-12">
                        <SelectValue placeholder="J 系列(全部)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部</SelectItem>
                        <SelectItem value="J0">J0</SelectItem>
                        <SelectItem value="J1">J1</SelectItem>
                        <SelectItem value="J2">J2</SelectItem>
                        <SelectItem value="J3">J3</SelectItem>
                        <SelectItem value="J5">J5</SelectItem>
                        <SelectItem value="J6">J6</SelectItem>
                        <SelectItem value="J7">J7</SelectItem>
                        <SelectItem value="J9">J9</SelectItem>
                        <SelectItem value="J10">J10</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* 模糊匹配 */}
                  <div className="flex items-center gap-2 pl-1">
                    <Switch id="fuzzy" checked={fuzzy} onCheckedChange={setFuzzy} />
                    <Label htmlFor="fuzzy" className="text-slate-700 select-none">模糊匹配</Label>
                  </div>

                  {/* 搜索按钮 */}
                  <Button
                    onClick={doSearch}
                    disabled={loading}
                    className="h-12 px-8 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow"
                  >
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>搜索中...</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <Search className="h-4 w-4" /> 搜索
                      </div>
                    )}
                  </Button>

                  {/* 以字搜索 */}
                  <Button
                    variant="secondary"
                    onClick={doSearchWord}
                    disabled={loading}
                    className="h-12 px-6"
                  >
                    以字搜索（word_label）
                  </Button>
                </div>

                {/* 错误提示 */}
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                )}

                {/* 条件提示 */}
                {(jSeries !== "all" || q || fuzzy !== true) && (
                  <div className="flex flex-wrap items-center gap-2">
                    {q && <Badge variant="outline" className="bg-slate-50">关键词：{q}</Badge>}
                    {jSeries && jSeries !== "all" && (
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">J系列：{jSeries}</Badge>
                    )}
                    <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                      匹配：{fuzzy ? "模糊" : "精确"}
                    </Badge>
                    <Badge variant="outline" className="bg-amber-50 text-amber-700 border-amber-200">
                      视图：{viewMode === "word" ? "按字" : "概念/字段"}
                    </Badge>
                  </div>
                )}

                {/* 结果 */}
                {search.length > 0 ? (
                  <div className="bg-white rounded-xl border border-slate-200 shadow overflow-hidden">
                    <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b">
                      <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                        <FileText className="h-4 w-4 text-blue-600" /> 搜索结果 ({search.length} 条)
                      </h3>
                    </div>
                    <div className="max-h-[56vh] overflow-auto">
                      <Table>
                        <TableHeader>
                          {viewMode === "word" ? (
                            <TableRow className="bg-slate-50/50">
                              <TableHead>word_label</TableHead>
                              <TableHead>DFI</TableHead>
                              <TableHead>DUI</TableHead>
                              <TableHead>DATA FIELD DESCRIPTOR</TableHead>
                              <TableHead>POSITION BITS</TableHead>
                              <TableHead>RESOLUTION / CODING</TableHead>
                              <TableHead>J系列</TableHead>
                              <TableHead>规范</TableHead>
                            </TableRow>
                          ) : (
                            <TableRow className="bg-slate-50/50">
                              <TableHead>来源</TableHead>
                              <TableHead>命中名称</TableHead>
                              <TableHead>规范名称</TableHead>
                              <TableHead>规范</TableHead>
                              <TableHead>J系列</TableHead>
                              <TableHead>字</TableHead>
                              <TableHead>字段</TableHead>
                              <TableHead>位</TableHead>
                            </TableRow>
                          )}
                        </TableHeader>
                        <TableBody>
                          {viewMode === "word"
                            ? search.map((r: any, i: number) => (
                                <TableRow key={i} className="hover:bg-blue-50/50">
                                  <TableCell className="font-medium text-slate-800">{r.word_label}</TableCell>
                                  <TableCell className="text-slate-600">{r.dfi ?? ""}</TableCell>
                                  <TableCell className="text-slate-600">{r.dui ?? ""}</TableCell>
                                  <TableCell className="text-slate-600">{r.descriptor ?? ""}</TableCell>
                                  <TableCell>
                                    {r.position_bits ? (
                                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                        {r.position_bits}
                                      </Badge>
                                    ) : null}
                                  </TableCell>
                                  <TableCell className="max-w-[360px] truncate" title={r.resolution_coding ?? ""}>
                                    {r.resolution_coding ?? ""}
                                  </TableCell>
                                  <TableCell className="text-slate-600">{r.j_series ?? ""}</TableCell>
                                  <TableCell>
                                    <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                                      {[r.code, r.edition, r.part_label].filter(Boolean).join(" ")}
                                    </Badge>
                                  </TableCell>
                                </TableRow>
                              ))
                            : search.map((r: any, i: number) => (
                                <TableRow key={i} className="hover:bg-blue-50/50">
                                  <TableCell>
                                    <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">{r.source}</Badge>
                                  </TableCell>
                                  <TableCell className="font-medium text-slate-800">{r.hit_name}</TableCell>
                                  <TableCell className="text-slate-600">{r.canonical_name || ""}</TableCell>
                                  <TableCell>
                                    <Badge variant="secondary" className="bg-slate-100 text-slate-700">
                                      {[r.code, r.edition, r.part_label].filter(Boolean).join(" ")}
                                    </Badge>
                                  </TableCell>
                                  <TableCell className="text-slate-600">{r.j_series || ""}</TableCell>
                                  <TableCell className="text-slate-600">{r.word_label || ""}</TableCell>
                                  <TableCell className="text-slate-600">{r.field_name || ""}</TableCell>
                                  <TableCell>
                                    {r.start_bit != null && (
                                      <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                        {r.start_bit}–{r.end_bit}
                                      </Badge>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ) : !loading && (q || jSeries !== "all") ? (
                  <div className="bg-white rounded-xl border border-slate-200 shadow p-8 text-center">
                    <Search className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-600 mb-2">未找到匹配结果</h3>
                    <p className="text-slate-500">请尝试其他关键词或调整搜索条件</p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 比较 */}
          <TabsContent value="compare" className="space-y-4">
            <Card className="bg-white/80 backdrop-blur-sm border-0 shadow">
              <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-t-lg">
                <CardTitle className="flex items-center gap-2 text-xl">
                  <GitCompare className="h-5 w-5 text-indigo-600" /> 规范比较
                </CardTitle>
                <CardDescription className="text-slate-600 text-sm">
                  比较不同规范中的概念定义，发现差异和相似性
                </CardDescription>
              </CardHeader>

              <CardContent className="flex flex-col gap-4 p-6">
                <div className="flex gap-4 w-full">
                  <div className="relative flex-1">
                    <GitCompare className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                    <Input
                      value={cmp}
                      onChange={(e) => setCmp(e.target.value)}
                      onKeyDown={(e) => e.key === "Enter" && doCompare()}
                      placeholder="输入要比较的概念，如 Altitude、Heading…"
                      className="pl-10 h-12 text-lg border-2 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                    />
                  </div>
                  <Button onClick={doCompare} disabled={loading}
                    className="h-12 px-8 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow">
                    {loading ? (
                      <div className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        <span>比较中...</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <GitCompare className="h-4 w-4" /> 比较
                      </div>
                    )}
                  </Button>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-red-700 text-sm">{error}</p>
                  </div>
                )}

                {bySpec.length > 0 ? (
                  <div className="bg-white rounded-xl border border-slate-200 shadow overflow-hidden">
                    <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b">
                       <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                        <GitCompare className="h-4 w-4 text-indigo-600" /> 比较结果 ({bySpec.length} 个规范)
                      </h3>
                    </div>
                    <div className="max-h-[56vh] overflow-auto">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50/50">
                            <TableHead>规范</TableHead>
                            <TableHead>字段绑定</TableHead>
                            <TableHead>数据项绑定</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {bySpec.map((r: any, i: number) => (
                            <TableRow key={i} className="hover:bg-indigo-50/50">
                              <TableCell className="font-medium text-slate-800">
                                <Badge variant="outline" className="bg-indigo-50 text-indigo-700 border-indigo-200">
                                  {[r.code, r.edition, r.part_label].filter(Boolean).join(" ")}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-slate-600">{r.field_bindings}</TableCell>
                              <TableCell className="text-slate-600">{r.data_item_bindings}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ) : !loading && cmp ? (
                  <div className="bg-white rounded-xl border border-slate-200 shadow p-8 text-center">
                    <GitCompare className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-600 mb-2">未找到比较结果</h3>
                    <p className="text-slate-500">请尝试其他概念名称</p>
                  </div>
                ) : null}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 热门概念 */}
          <TabsContent value="top" className="space-y-4">
             <Card className="bg-white/80 backdrop-blur-sm border-0 shadow">
              <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-lg">
                <CardTitle className="flex items-center gap-2 text-xl">
                  <TrendingUp className="h-5 w-5 text-purple-600" /> 热门概念
                </CardTitle>
                <CardDescription className="text-slate-600 text-sm">
                  最常使用的概念和字段，了解MIL-STD-6016标准的核心内容
                </CardDescription>
              </CardHeader>

              <CardContent className="p-6">
                {top.length > 0 ? (
                  <div className="bg-white rounded-xl border border-slate-200 shadow overflow-hidden">
                    <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-4 py-3 border-b">
                      <h3 className="text-base font-semibold text-slate-800 flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-purple-600" /> 热门概念排行榜 ({top.length} 个)
                      </h3>
                    </div>
                    <div className="max-h-[56vh] overflow-auto">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50/50">
                            <TableHead>概念</TableHead>
                            <TableHead>字段数</TableHead>
                            <TableHead>数据项数</TableHead>
                            <TableHead>消息数</TableHead>
                            <TableHead>规范数</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {top.map((r: any, i: number) => (
                            <TableRow key={i} className="hover:bg-purple-50/50">
                              <TableCell className="font-medium text-slate-800">{r.canonical_name}</TableCell>
                              <TableCell><Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">{r.fields}</Badge></TableCell>
                              <TableCell><Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">{r.data_items}</Badge></TableCell>
                              <TableCell><Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">{r.messages}</Badge></TableCell>
                              <TableCell><Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">{r.specs}</Badge></TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                ) : (
                  <div className="bg-white rounded-xl border border-slate-200 shadow p-8 text-center">
                    <TrendingUp className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-slate-600 mb-2">正在加载热门概念</h3>
                    <p className="text-slate-500">请稍候...</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
