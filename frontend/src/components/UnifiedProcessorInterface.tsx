import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog";
import { useToast } from "./ui/toast";

interface UnifiedMessage {
  message_type: string;
  protocol: string;
  data: Record<string, any>;
  metadata?: Record<string, any>;
  timestamp?: string;
}

interface ConversionRequest {
  source_message: UnifiedMessage;
  target_protocol: string;
  target_message_type: string;
  options?: Record<string, any>;
}

interface ConversionResponse {
  success: boolean;
  target_message?: UnifiedMessage;
  processing_time: number;
  confidence: number;
  errors: string[];
  warnings: string[];
  metadata?: Record<string, any>;
}

interface Concept {
  path: string;
  data_type: string;
  unit?: string;
  description: string;
  source: string;
}

interface Mapping {
  mapping_key: string;
  source_protocol: string;
  target_protocol: string;
  version: string;
  source: string;
}

const UnifiedProcessorInterface: React.FC = () => {
  const [activeTab, setActiveTab] = useState("message-processing");
  const [loading, setLoading] = useState(false);
  const { addToast } = useToast();
  
  // 消息转换状态
  const [conversionRequest, setConversionRequest] = useState<ConversionRequest>({
    source_message: {
      message_type: "J_SERIES",
      protocol: "MIL-STD-6016",
      data: {}
    },
    target_protocol: "MQTT",
    target_message_type: "POSITION"
  });
  const [conversionResult, setConversionResult] = useState<ConversionResponse | null>(null);
  
  // 概念管理状态
  const [concepts, setConcepts] = useState<Concept[]>([]);
  const [conceptSearch, setConceptSearch] = useState("");
  
  // 映射管理状态
  const [mappings, setMappings] = useState<Mapping[]>([]);
  const [mappingFilter, setMappingFilter] = useState({
    source_protocol: "",
    target_protocol: ""
  });
  
  // 系统统计状态
  const [statistics, setStatistics] = useState<any>(null);

  const API_BASE = 'http://localhost:8000/api/v2';

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [conceptsRes, mappingsRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/concepts`),
        fetch(`${API_BASE}/mappings`),
        fetch(`${API_BASE}/statistics`)
      ]);

      const [conceptsData, mappingsData, statsData] = await Promise.all([
        conceptsRes.json(),
        mappingsRes.json(),
        statsRes.json()
      ]);

      setConcepts(conceptsData.concepts || []);
      setMappings(mappingsData.mappings || []);
      setStatistics(statsData.statistics || {});
    } catch (error) {
      console.error('Failed to load initial data:', error);
      addToast({
        type: "error",
        title: "加载失败",
        message: "无法加载初始数据，请检查API连接"
      });
    } finally {
      setLoading(false);
    }
  };

  const convertMessage = async () => {
    if (!conversionRequest.source_message.data || Object.keys(conversionRequest.source_message.data).length === 0) {
      addToast({
        type: "warning",
        title: "输入不完整",
        message: "请输入消息数据"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/convert-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(conversionRequest)
      });

      const data = await response.json();
      if (data.success) {
        setConversionResult(data);
        addToast({
          type: "success",
          title: "转换完成",
          message: `消息已成功从 ${conversionRequest.source_message.protocol} 转换为 ${conversionRequest.target_protocol}`
        });
      } else {
        throw new Error(data.detail || '转换失败');
      }
    } catch (error) {
      console.error('Message conversion failed:', error);
      addToast({
        type: "error",
        title: "转换失败",
        message: error instanceof Error ? error.message : "消息转换失败"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file: File) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('file_type', file.type.split('/')[1]);
      
      const response = await fetch(`${API_BASE}/process-file`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.success) {
        addToast({
          type: "success",
          title: "文件处理完成",
          message: `文件 ${file.name} 处理成功`
        });
      } else {
        throw new Error(data.detail || '文件处理失败');
      }
    } catch (error) {
      console.error('File processing failed:', error);
      addToast({
        type: "error",
        title: "文件处理失败",
        message: error instanceof Error ? error.message : "文件处理失败"
      });
    } finally {
      setLoading(false);
    }
  };

  const filteredConcepts = concepts.filter(concept => {
    if (conceptSearch && !concept.path.toLowerCase().includes(conceptSearch.toLowerCase()) && 
        !concept.description.toLowerCase().includes(conceptSearch.toLowerCase())) {
      return false;
    }
    return true;
  });

  const filteredMappings = mappings.filter(mapping => {
    if (mappingFilter.source_protocol && mappingFilter.source_protocol !== "all" && mapping.source_protocol !== mappingFilter.source_protocol) {
      return false;
    }
    if (mappingFilter.target_protocol && mappingFilter.target_protocol !== "all" && mapping.target_protocol !== mappingFilter.target_protocol) {
      return false;
    }
    return true;
  });

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">统一文档处理与语义互操作平台</h1>
          <p className="text-muted-foreground">集成PDF处理、语义互操作、CDM四层法和多格式导入功能</p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="text-sm">
            {concepts.length} 个概念
          </Badge>
          <Badge variant="outline" className="text-sm">
            {mappings.length} 个映射
          </Badge>
          <Badge variant="outline" className="text-sm">
            统一API v2.0
          </Badge>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="message-processing">消息处理</TabsTrigger>
          <TabsTrigger value="file-processing">文件处理</TabsTrigger>
          <TabsTrigger value="concept-management">概念管理</TabsTrigger>
          <TabsTrigger value="mapping-management">映射管理</TabsTrigger>
          <TabsTrigger value="system-overview">系统概览</TabsTrigger>
        </TabsList>

        <TabsContent value="message-processing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>统一消息转换</CardTitle>
              <CardDescription>
                支持多种协议间的消息转换，包括MIL-STD-6016、MAVLink、MQTT等
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="source-protocol">源协议</Label>
                    <Select 
                      value={conversionRequest.source_message.protocol} 
                      onValueChange={(value) => setConversionRequest(prev => ({
                        ...prev,
                        source_message: { ...prev.source_message, protocol: value }
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择源协议" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MIL-STD-6016">MIL-STD-6016</SelectItem>
                        <SelectItem value="MAVLink">MAVLink</SelectItem>
                        <SelectItem value="MQTT">MQTT</SelectItem>
                        <SelectItem value="XML">XML</SelectItem>
                        <SelectItem value="JSON">JSON</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="target-protocol">目标协议</Label>
                    <Select 
                      value={conversionRequest.target_protocol} 
                      onValueChange={(value) => setConversionRequest(prev => ({
                        ...prev,
                        target_protocol: value
                      }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择目标协议" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MIL-STD-6016">MIL-STD-6016</SelectItem>
                        <SelectItem value="MAVLink">MAVLink</SelectItem>
                        <SelectItem value="MQTT">MQTT</SelectItem>
                        <SelectItem value="XML">XML</SelectItem>
                        <SelectItem value="JSON">JSON</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="message-data">消息数据 (JSON格式)</Label>
                  <textarea
                    id="message-data"
                    className="min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    placeholder='{"message_type": "J2.0", "track_id": "T001", "latitude": 39.9042, "longitude": 116.4074}'
                    value={JSON.stringify(conversionRequest.source_message.data, null, 2)}
                    onChange={(e) => {
                      try {
                        const data = JSON.parse(e.target.value);
                        setConversionRequest(prev => ({
                          ...prev,
                          source_message: { ...prev.source_message, data }
                        }));
                      } catch (error) {
                        // 忽略JSON解析错误，让用户继续输入
                      }
                    }}
                  />
                </div>
              </div>
              
              <Button onClick={convertMessage} disabled={loading} className="w-full">
                {loading ? "转换中..." : "执行消息转换"}
              </Button>

              {conversionResult && (
                <div className="mt-4 space-y-4">
                  <div>
                    <h4 className="font-semibold">转换结果</h4>
                    <div className="mt-2 rounded-md bg-muted p-4">
                      <pre className="text-sm overflow-auto">
                        {JSON.stringify(conversionResult, null, 2)}
                      </pre>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <h5 className="font-medium">转换状态</h5>
                      <Badge variant={conversionResult.success ? "default" : "destructive"}>
                        {conversionResult.success ? "✅ 成功" : "❌ 失败"}
                      </Badge>
                    </div>
                    <div>
                      <h5 className="font-medium">处理时间</h5>
                      <span className="text-sm text-muted-foreground">
                        {conversionResult.processing_time.toFixed(3)}秒
                      </span>
                    </div>
                    <div>
                      <h5 className="font-medium">置信度</h5>
                      <span className="text-sm text-muted-foreground">
                        {(conversionResult.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="file-processing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>统一文件处理</CardTitle>
              <CardDescription>
                支持PDF、XML、JSON、CSV等多种格式的文件处理
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <div className="space-y-4">
                  <div className="text-4xl">📁</div>
                  <div>
                    <h3 className="text-lg font-semibold">拖拽文件到此处或点击选择</h3>
                    <p className="text-sm text-muted-foreground">
                      支持 PDF, XML, JSON, CSV 格式
                    </p>
                  </div>
                  <input
                    type="file"
                    accept=".pdf,.xml,.json,.csv"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        handleFileUpload(file);
                      }
                    }}
                    className="hidden"
                    id="file-upload"
                  />
                  <Button asChild>
                    <label htmlFor="file-upload" className="cursor-pointer">
                      选择文件
                    </label>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="concept-management" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>统一概念管理</CardTitle>
              <CardDescription>
                管理CDM概念和语义字段定义
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Input
                    placeholder="搜索概念..."
                    value={conceptSearch}
                    onChange={(e) => setConceptSearch(e.target.value)}
                    className="w-64"
                  />
                </div>
                <div className="text-sm text-muted-foreground">
                  共 {filteredConcepts.length} 个概念
                </div>
              </div>
              
              <div className="max-h-[400px] overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>概念路径</TableHead>
                      <TableHead>数据类型</TableHead>
                      <TableHead>单位</TableHead>
                      <TableHead>来源</TableHead>
                      <TableHead>描述</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredConcepts.slice(0, 20).map((concept, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">{concept.path}</TableCell>
                        <TableCell>
                          <Badge variant="secondary">{concept.data_type}</Badge>
                        </TableCell>
                        <TableCell>{concept.unit || '-'}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{concept.source}</Badge>
                        </TableCell>
                        <TableCell className="max-w-xs truncate">{concept.description}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {filteredConcepts.length > 20 && (
                  <p className="text-sm text-muted-foreground mt-2">
                    显示前20个概念，共{filteredConcepts.length}个
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="mapping-management" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>统一映射管理</CardTitle>
              <CardDescription>
                管理协议间的映射规则和转换关系
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="space-y-2">
                    <Label htmlFor="source-filter">源协议过滤</Label>
                    <Select 
                      value={mappingFilter.source_protocol} 
                      onValueChange={(value) => setMappingFilter(prev => ({...prev, source_protocol: value}))}
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="全部" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部</SelectItem>
                        <SelectItem value="MIL-STD-6016">MIL-STD-6016</SelectItem>
                        <SelectItem value="MAVLink">MAVLink</SelectItem>
                        <SelectItem value="MQTT">MQTT</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="target-filter">目标协议过滤</Label>
                    <Select 
                      value={mappingFilter.target_protocol} 
                      onValueChange={(value) => setMappingFilter(prev => ({...prev, target_protocol: value}))}
                    >
                      <SelectTrigger className="w-40">
                        <SelectValue placeholder="全部" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">全部</SelectItem>
                        <SelectItem value="MIL-STD-6016">MIL-STD-6016</SelectItem>
                        <SelectItem value="MAVLink">MAVLink</SelectItem>
                        <SelectItem value="MQTT">MQTT</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">
                  共 {filteredMappings.length} 个映射
                </div>
              </div>
              
              <div className="max-h-[400px] overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>映射关系</TableHead>
                      <TableHead>源协议</TableHead>
                      <TableHead>目标协议</TableHead>
                      <TableHead>版本</TableHead>
                      <TableHead>来源</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredMappings.slice(0, 20).map((mapping, index) => (
                      <TableRow key={index}>
                        <TableCell className="font-medium">
                          {mapping.source_protocol} → {mapping.target_protocol}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{mapping.source_protocol}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{mapping.target_protocol}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary">{mapping.version}</Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">{mapping.source}</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                {filteredMappings.length > 20 && (
                  <p className="text-sm text-muted-foreground mt-2">
                    显示前20个映射，共{filteredMappings.length}个
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system-overview" className="space-y-4">
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">处理总数</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{statistics?.total_processed || 0}</div>
                <p className="text-sm text-muted-foreground mt-1">
                  已处理消息/文件
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">成功率</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statistics?.success_rate ? `${(statistics.success_rate * 100).toFixed(1)}%` : '0%'}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  处理成功率
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">平均处理时间</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statistics?.average_processing_time ? `${statistics.average_processing_time.toFixed(3)}s` : '0s'}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  平均处理时间
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">支持协议</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {statistics?.supported_protocols?.length || 0}
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  支持的协议数量
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>系统功能概览</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">核心功能</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 统一消息转换 - 支持多种协议互转</li>
                    <li>• 多格式文件处理 - PDF/XML/JSON/CSV</li>
                    <li>• 概念化管理 - CDM和语义字段统一管理</li>
                    <li>• 映射规则管理 - 灵活的转换规则配置</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">技术特性</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 四层法架构 - 语义层→映射层→校验层→运行层</li>
                    <li>• 声明式配置 - YAML规则配置，无需编程</li>
                    <li>• 实时处理 - 高性能消息转换引擎</li>
                    <li>• 质量保证 - 多维度校验和回归测试</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default UnifiedProcessorInterface;
