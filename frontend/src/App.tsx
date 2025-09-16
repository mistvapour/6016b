import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Search, GitCompare, TrendingUp, Database, FileText, Zap, Globe, Shield } from "lucide-react";

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
    <div className="min-h-screen w-full bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-40 left-1/2 w-80 h-80 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-500"></div>
      </div>
      
      {/* 主容器 - 确保全屏并居中 */}
      <div className="relative w-full min-h-screen flex flex-col items-center justify-start">
        {/* 头部区域 */}
        <div className="w-full max-w-7xl px-6 py-8">
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-4 mb-4">
              <div className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                MIL-STD-6016 Explorer
              </h1>
            </div>
            <p className="text-xl text-slate-600 max-w-4xl mx-auto leading-relaxed">
              探索和分析MIL-STD-6016标准数据，发现军事通信协议的深层洞察
            </p>
            <div className="flex items-center justify-center space-x-8 text-sm text-slate-500">
              <div className="flex items-center space-x-2">
                <Database className="h-4 w-4" />
                <span>实时数据</span>
              </div>
              <div className="flex items-center space-x-2">
                <Zap className="h-4 w-4" />
                <span>快速搜索</span>
              </div>
              <div className="flex items-center space-x-2">
                <Globe className="h-4 w-4" />
                <span>标准兼容</span>
              </div>
            </div>
          </div>
        </div>

        {/* 标签页容器 */}
        <div className="w-full max-w-7xl px-6 pb-8 flex-1">
          <Tabs defaultValue="search" className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-white/80 backdrop-blur-sm border border-slate-200 shadow-lg mb-6">
              <TabsTrigger value="search" className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white">
                <Search className="h-4 w-4" />
                <span>搜索</span>
              </TabsTrigger>
              <TabsTrigger value="compare" className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white">
                <GitCompare className="h-4 w-4" />
                <span>比较</span>
              </TabsTrigger>
              <TabsTrigger value="top" className="flex items-center space-x-2 data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-500 data-[state=active]:to-indigo-500 data-[state=active]:text-white">
                <TrendingUp className="h-4 w-4" />
                <span>热门概念</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="search" className="space-y-6">
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
                  <CardTitle className="flex items-center space-x-2 text-2xl">
                    <Search className="h-6 w-6 text-blue-600" />
                    <span>智能搜索</span>
                  </CardTitle>
                  <CardDescription className="text-slate-600">
                    搜索概念、别名、字段或数据项，快速找到您需要的信息
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6 p-6">
                  <div className="flex gap-4">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input
                        value={q}
                        onChange={(e) => setQ(e.target.value)}
                        placeholder="输入搜索关键词..."
                        className="pl-10 h-12 text-lg border-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                      />
                    </div>
                    <Button 
                      onClick={doSearch} 
                      disabled={loading}
                      className="h-12 px-8 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
                    >
                      {loading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>搜索中...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <Search className="h-4 w-4" />
                          <span>搜索</span>
                        </div>
                      )}
                    </Button>
                  </div>
                  
                  {search.length > 0 && (
                    <div className="bg-white rounded-xl border border-slate-200 shadow-lg overflow-hidden">
                      <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 border-b">
                        <h3 className="text-lg font-semibold text-slate-800 flex items-center space-x-2">
                          <FileText className="h-5 w-5 text-blue-600" />
                          <span>搜索结果 ({search.length} 条)</span>
                        </h3>
                      </div>
                      <div className="overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow className="bg-slate-50/50">
                              <TableHead className="font-semibold text-slate-700">来源</TableHead>
                              <TableHead className="font-semibold text-slate-700">命中名称</TableHead>
                              <TableHead className="font-semibold text-slate-700">规范名称</TableHead>
                              <TableHead className="font-semibold text-slate-700">规范</TableHead>
                              <TableHead className="font-semibold text-slate-700">J系列</TableHead>
                              <TableHead className="font-semibold text-slate-700">字</TableHead>
                              <TableHead className="font-semibold text-slate-700">字段</TableHead>
                              <TableHead className="font-semibold text-slate-700">位</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {search.map((r: any, i: number) => (
                              <TableRow key={i} className="hover:bg-blue-50/50 transition-colors">
                                <TableCell>
                                  <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                    {r.source}
                                  </Badge>
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
                                  {r.start_bit != null ? (
                                    <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                      {r.start_bit}–{r.end_bit}
                                    </Badge>
                                  ) : ""}
                                </TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="compare" className="space-y-6">
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-t-lg">
                  <CardTitle className="flex items-center space-x-2 text-2xl">
                    <GitCompare className="h-6 w-6 text-indigo-600" />
                    <span>规范比较</span>
                  </CardTitle>
                  <CardDescription className="text-slate-600">
                    比较不同规范中的概念定义，发现差异和相似性
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6 p-6">
                  <div className="flex gap-4">
                    <div className="relative flex-1">
                      <GitCompare className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input
                        value={cmp}
                        onChange={(e) => setCmp(e.target.value)}
                        placeholder="输入要比较的概念..."
                        className="pl-10 h-12 text-lg border-2 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
                      />
                    </div>
                    <Button 
                      onClick={doCompare} 
                      disabled={loading}
                      className="h-12 px-8 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
                    >
                      {loading ? (
                        <div className="flex items-center space-x-2">
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                          <span>比较中...</span>
                        </div>
                      ) : (
                        <div className="flex items-center space-x-2">
                          <GitCompare className="h-4 w-4" />
                          <span>比较</span>
                        </div>
                      )}
                    </Button>
                  </div>
                  
                  {bySpec.length > 0 && (
                    <div className="bg-white rounded-xl border border-slate-200 shadow-lg overflow-hidden">
                      <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 border-b">
                        <h3 className="text-lg font-semibold text-slate-800 flex items-center space-x-2">
                          <GitCompare className="h-5 w-5 text-indigo-600" />
                          <span>比较结果 ({bySpec.length} 个规范)</span>
                        </h3>
                      </div>
                      <div className="overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow className="bg-slate-50/50">
                              <TableHead className="font-semibold text-slate-700">规范</TableHead>
                              <TableHead className="font-semibold text-slate-700">字段绑定</TableHead>
                              <TableHead className="font-semibold text-slate-700">数据项绑定</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {bySpec.map((r: any, i: number) => (
                              <TableRow key={i} className="hover:bg-indigo-50/50 transition-colors">
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
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="top" className="space-y-6">
              <Card className="bg-white/80 backdrop-blur-sm border-0 shadow-xl">
                <CardHeader className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-t-lg">
                  <CardTitle className="flex items-center space-x-2 text-2xl">
                    <TrendingUp className="h-6 w-6 text-purple-600" />
                    <span>热门概念</span>
                  </CardTitle>
                  <CardDescription className="text-slate-600">
                    最常使用的概念和字段，了解MIL-STD-6016标准的核心内容
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="bg-white rounded-xl border border-slate-200 shadow-lg overflow-hidden">
                    <div className="bg-gradient-to-r from-slate-50 to-slate-100 px-6 py-4 border-b">
                      <h3 className="text-lg font-semibold text-slate-800 flex items-center space-x-2">
                        <TrendingUp className="h-5 w-5 text-purple-600" />
                        <span>热门概念排行榜 ({top.length} 个)</span>
                      </h3>
                    </div>
                    <div className="overflow-x-auto">
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50/50">
                            <TableHead className="font-semibold text-slate-700">概念</TableHead>
                            <TableHead className="font-semibold text-slate-700">字段数</TableHead>
                            <TableHead className="font-semibold text-slate-700">数据项数</TableHead>
                            <TableHead className="font-semibold text-slate-700">消息数</TableHead>
                            <TableHead className="font-semibold text-slate-700">规范数</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {top.map((r: any, i: number) => (
                            <TableRow key={i} className="hover:bg-purple-50/50 transition-colors">
                              <TableCell className="font-medium text-slate-800">{r.canonical_name}</TableCell>
                              <TableCell>
                                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                                  {r.fields}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                                  {r.data_items}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline" className="bg-orange-50 text-orange-700 border-orange-200">
                                  {r.messages}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                                  {r.specs}
                                </Badge>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}