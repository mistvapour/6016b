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
import { toast } from "./ui/toast";

interface CDMConcept {
  path: string;
  data_type: string;
  unit?: string;
  value_range?: [number, number];
  resolution?: number;
  coordinate_frame?: string;
  enum_values?: Record<string, string>;
  description: string;
  confidence: number;
  source: string;
  version: string;
  created_at: string;
}

interface MappingRule {
  source_field: string;
  cdm_path: string;
  target_field: string;
  unit_conversion?: [string, string];
  scale_factor?: number;
  offset?: number;
  enum_mapping?: Record<string, string>;
  bit_range?: [number, number];
  condition?: string;
  default_value?: any;
  version: string;
  author: string;
}

interface ProtocolMapping {
  mapping_key: string;
  source_protocol: string;
  target_protocol: string;
  version: string;
  author: string;
  created_at: string;
  message_types: string[];
  total_rules: number;
}

interface ConversionResult {
  success: boolean;
  result: {
    source_message: any;
    target_message: any;
    validation: {
      is_valid: boolean;
      errors: string[];
      warnings: string[];
      metrics: any;
    };
  };
  timestamp: string;
}

const CDMInteropInterface: React.FC = () => {
  const [concepts, setConcepts] = useState<CDMConcept[]>([]);
  const [mappings, setMappings] = useState<ProtocolMapping[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 消息转换状态
  const [conversionInput, setConversionInput] = useState({
    source_message: '{"message_type": "J2.0", "track_id": "T001", "latitude": 39.9042, "longitude": 116.4074}',
    source_protocol: 'MIL-STD-6016B',
    target_protocol: 'MQTT',
    message_type: 'PositionUpdate'
  });
  const [conversionResult, setConversionResult] = useState<ConversionResult | null>(null);
  
  // 概念创建状态
  const [conceptForm, setConceptForm] = useState({
    path: '',
    data_type: '',
    unit: '',
    value_range_min: '',
    value_range_max: '',
    resolution: '',
    coordinate_frame: '',
    description: '',
    confidence: '1.0',
    source: ''
  });
  
  // 映射规则创建状态
  const [mappingForm, setMappingForm] = useState({
    source_protocol: '',
    target_protocol: '',
    message_type: '',
    rules: [] as any[]
  });

  const API_BASE = 'http://localhost:8000/api/cdm';

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [conceptsRes, mappingsRes] = await Promise.all([
        fetch(`${API_BASE}/concepts`),
        fetch(`${API_BASE}/mappings`)
      ]);

      const [conceptsData, mappingsData] = await Promise.all([
        conceptsRes.json(),
        mappingsRes.json()
      ]);

      setConcepts(conceptsData.concepts || []);
      setMappings(mappingsData.mappings || []);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      toast({
        title: "加载失败",
        description: "无法加载CDM数据，请检查API连接",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const convertMessage = async () => {
    if (!conversionInput.source_message || !conversionInput.source_protocol || 
        !conversionInput.target_protocol || !conversionInput.message_type) {
      toast({
        title: "输入不完整",
        description: "请填写所有必需的转换参数",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const sourceMessage = JSON.parse(conversionInput.source_message);
      const response = await fetch(`${API_BASE}/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_message: sourceMessage,
          source_protocol: conversionInput.source_protocol,
          target_protocol: conversionInput.target_protocol,
          message_type: conversionInput.message_type
        })
      });

      const data = await response.json();
      if (data.success) {
        setConversionResult(data);
        toast({
          title: "转换完成",
          description: `消息已成功从 ${conversionInput.source_protocol} 转换为 ${conversionInput.target_protocol}`,
          variant: "default"
        });
      } else {
        throw new Error(data.detail || '转换失败');
      }
    } catch (error) {
      console.error('Message conversion failed:', error);
      toast({
        title: "转换失败",
        description: error instanceof Error ? error.message : "消息转换失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createConcept = async () => {
    if (!conceptForm.path || !conceptForm.data_type) {
      toast({
        title: "输入不完整",
        description: "请填写概念路径和数据类型",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const conceptData = {
        path: conceptForm.path,
        data_type: conceptForm.data_type,
        unit: conceptForm.unit || null,
        value_range: conceptForm.value_range_min && conceptForm.value_range_max ? 
          [parseFloat(conceptForm.value_range_min), parseFloat(conceptForm.value_range_max)] : null,
        resolution: conceptForm.resolution ? parseFloat(conceptForm.resolution) : null,
        coordinate_frame: conceptForm.coordinate_frame || null,
        description: conceptForm.description,
        confidence: parseFloat(conceptForm.confidence),
        source: conceptForm.source
      };

      const response = await fetch(`${API_BASE}/concepts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(conceptData)
      });

      const data = await response.json();
      if (data.success) {
        toast({
          title: "概念创建成功",
          description: "CDM概念已成功创建",
          variant: "default"
        });
        
        // 重新加载概念列表
        const conceptsRes = await fetch(`${API_BASE}/concepts`);
        const conceptsData = await conceptsRes.json();
        setConcepts(conceptsData.concepts || []);
        
        // 清空表单
        setConceptForm({
          path: '',
          data_type: '',
          unit: '',
          value_range_min: '',
          value_range_max: '',
          resolution: '',
          coordinate_frame: '',
          description: '',
          confidence: '1.0',
          source: ''
        });
      } else {
        throw new Error(data.detail || '概念创建失败');
      }
    } catch (error) {
      console.error('Concept creation failed:', error);
      toast({
        title: "概念创建失败",
        description: error instanceof Error ? error.message : "CDM概念创建失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const addMappingRule = () => {
    setMappingForm(prev => ({
      ...prev,
      rules: [...prev.rules, {
        source_field: '',
        cdm_path: '',
        target_field: '',
        unit_conversion: ['', ''],
        scale_factor: '',
        offset: '',
        enum_mapping: {},
        version: '1.0',
        author: ''
      }]
    }));
  };

  const removeMappingRule = (index: number) => {
    setMappingForm(prev => ({
      ...prev,
      rules: prev.rules.filter((_, i) => i !== index)
    }));
  };

  const updateMappingRule = (index: number, field: string, value: any) => {
    setMappingForm(prev => ({
      ...prev,
      rules: prev.rules.map((rule, i) => 
        i === index ? { ...rule, [field]: value } : rule
      )
    }));
  };

  const createMapping = async () => {
    if (!mappingForm.source_protocol || !mappingForm.target_protocol || 
        !mappingForm.message_type || mappingForm.rules.length === 0) {
      toast({
        title: "输入不完整",
        description: "请填写所有必需的映射信息",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/mappings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          source_protocol: mappingForm.source_protocol,
          target_protocol: mappingForm.target_protocol,
          message_type: mappingForm.message_type,
          rules: mappingForm.rules
        })
      });

      const data = await response.json();
      if (data.success) {
        toast({
          title: "映射创建成功",
          description: "映射规则已成功创建",
          variant: "default"
        });
        
        // 重新加载映射列表
        const mappingsRes = await fetch(`${API_BASE}/mappings`);
        const mappingsData = await mappingsRes.json();
        setMappings(mappingsData.mappings || []);
        
        // 清空表单
        setMappingForm({
          source_protocol: '',
          target_protocol: '',
          message_type: '',
          rules: []
        });
      } else {
        throw new Error(data.detail || '映射创建失败');
      }
    } catch (error) {
      console.error('Mapping creation failed:', error);
      toast({
        title: "映射创建失败",
        description: error instanceof Error ? error.message : "映射规则创建失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const runGoldenSetRegression = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/golden-samples/regression`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        toast({
          title: "回归测试完成",
          description: `金标准回归测试${data.regression_result.is_valid ? '通过' : '失败'}`,
          variant: data.regression_result.is_valid ? "default" : "destructive"
        });
      } else {
        throw new Error(data.detail || '回归测试失败');
      }
    } catch (error) {
      console.error('Golden set regression failed:', error);
      toast({
        title: "回归测试失败",
        description: error instanceof Error ? error.message : "金标准回归测试失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">CDM语义互操作系统</h1>
          <p className="text-muted-foreground">基于四层法的企业级语义互操作解决方案</p>
        </div>
        <div className="flex gap-2">
          <Badge variant="outline" className="text-sm">
            {concepts.length} 个CDM概念
          </Badge>
          <Badge variant="outline" className="text-sm">
            {mappings.length} 个映射规则
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="message-conversion" className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="message-conversion">消息转换</TabsTrigger>
          <TabsTrigger value="concept-management">概念管理</TabsTrigger>
          <TabsTrigger value="mapping-management">映射管理</TabsTrigger>
          <TabsTrigger value="validation-testing">校验测试</TabsTrigger>
          <TabsTrigger value="system-overview">系统概览</TabsTrigger>
        </TabsList>

        <TabsContent value="message-conversion" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>CDM消息转换</CardTitle>
              <CardDescription>
                基于四层法进行跨协议消息转换：源协议 → CDM → 目标协议
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="source-message">源消息 (JSON格式)</Label>
                  <textarea
                    id="source-message"
                    className="min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    placeholder='{"message_type": "J2.0", "track_id": "T001", "latitude": 39.9042}'
                    value={conversionInput.source_message}
                    onChange={(e) => setConversionInput(prev => ({...prev, source_message: e.target.value}))}
                  />
                </div>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-2">
                    <div className="space-y-2">
                      <Label htmlFor="source-protocol">源协议</Label>
                      <Select 
                        value={conversionInput.source_protocol} 
                        onValueChange={(value) => setConversionInput(prev => ({...prev, source_protocol: value}))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="选择源协议" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="MIL-STD-6016B">MIL-STD-6016B</SelectItem>
                          <SelectItem value="MAVLink">MAVLink</SelectItem>
                          <SelectItem value="MQTT">MQTT</SelectItem>
                          <SelectItem value="CDM">CDM</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="target-protocol">目标协议</Label>
                      <Select 
                        value={conversionInput.target_protocol} 
                        onValueChange={(value) => setConversionInput(prev => ({...prev, target_protocol: value}))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="选择目标协议" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="MIL-STD-6016B">MIL-STD-6016B</SelectItem>
                          <SelectItem value="MAVLink">MAVLink</SelectItem>
                          <SelectItem value="MQTT">MQTT</SelectItem>
                          <SelectItem value="CDM">CDM</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="message-type">消息类型</Label>
                    <Input
                      id="message-type"
                      placeholder="例如: J2.0, ATTITUDE, PositionUpdate"
                      value={conversionInput.message_type}
                      onChange={(e) => setConversionInput(prev => ({...prev, message_type: e.target.value}))}
                    />
                  </div>
                </div>
              </div>
              
              <Button onClick={convertMessage} disabled={loading} className="w-full">
                {loading ? "转换中..." : "执行CDM转换"}
              </Button>

              {conversionResult && (
                <div className="mt-4 space-y-4">
                  <div>
                    <h4 className="font-semibold">转换结果</h4>
                    <div className="mt-2 rounded-md bg-muted p-4">
                      <pre className="text-sm overflow-auto">
                        {JSON.stringify(conversionResult.result, null, 2)}
                      </pre>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium">校验状态</h5>
                      <Badge variant={conversionResult.result.validation.is_valid ? "default" : "destructive"}>
                        {conversionResult.result.validation.is_valid ? "✅ 通过" : "❌ 失败"}
                      </Badge>
                    </div>
                    <div>
                      <h5 className="font-medium">错误数量</h5>
                      <span className="text-sm text-muted-foreground">
                        {conversionResult.result.validation.errors.length} 个错误
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="concept-management" className="space-y-4">
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>创建CDM概念</CardTitle>
                <CardDescription>
                  定义统一语义模型中的核心概念
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="concept-path">概念路径</Label>
                  <Input
                    id="concept-path"
                    placeholder="例如: Track.Position.Latitude"
                    value={conceptForm.path}
                    onChange={(e) => setConceptForm(prev => ({...prev, path: e.target.value}))}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="data-type">数据类型</Label>
                    <Select 
                      value={conceptForm.data_type} 
                      onValueChange={(value) => setConceptForm(prev => ({...prev, data_type: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择数据类型" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="identifier">identifier</SelectItem>
                        <SelectItem value="float">float</SelectItem>
                        <SelectItem value="integer">integer</SelectItem>
                        <SelectItem value="string">string</SelectItem>
                        <SelectItem value="enum">enum</SelectItem>
                        <SelectItem value="timestamp">timestamp</SelectItem>
                        <SelectItem value="coordinate">coordinate</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="unit">单位</Label>
                    <Input
                      id="unit"
                      placeholder="例如: degree, meter, radian"
                      value={conceptForm.unit}
                      onChange={(e) => setConceptForm(prev => ({...prev, unit: e.target.value}))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="value-range-min">取值范围最小值</Label>
                    <Input
                      id="value-range-min"
                      type="number"
                      placeholder="例如: -90"
                      value={conceptForm.value_range_min}
                      onChange={(e) => setConceptForm(prev => ({...prev, value_range_min: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="value-range-max">取值范围最大值</Label>
                    <Input
                      id="value-range-max"
                      type="number"
                      placeholder="例如: 90"
                      value={conceptForm.value_range_max}
                      onChange={(e) => setConceptForm(prev => ({...prev, value_range_max: e.target.value}))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="resolution">分辨率</Label>
                    <Input
                      id="resolution"
                      type="number"
                      placeholder="例如: 0.01"
                      value={conceptForm.resolution}
                      onChange={(e) => setConceptForm(prev => ({...prev, resolution: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="coordinate-frame">坐标参考系</Label>
                    <Select 
                      value={conceptForm.coordinate_frame} 
                      onValueChange={(value) => setConceptForm(prev => ({...prev, coordinate_frame: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择坐标参考系" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="WGS84">WGS84</SelectItem>
                        <SelectItem value="NED">NED</SelectItem>
                        <SelectItem value="ENU">ENU</SelectItem>
                        <SelectItem value="BODY">BODY</SelectItem>
                        <SelectItem value="TRUE">TRUE</SelectItem>
                        <SelectItem value="MAGNETIC">MAGNETIC</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">描述</Label>
                  <Input
                    id="description"
                    placeholder="概念描述"
                    value={conceptForm.description}
                    onChange={(e) => setConceptForm(prev => ({...prev, description: e.target.value}))}
                  />
                </div>

                <Button onClick={createConcept} disabled={loading}>
                  {loading ? "创建中..." : "创建CDM概念"}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>CDM概念列表</CardTitle>
                <CardDescription>
                  已定义的CDM概念
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-[400px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>概念路径</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>单位</TableHead>
                        <TableHead>置信度</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {concepts.slice(0, 15).map((concept, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{concept.path}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{concept.data_type}</Badge>
                          </TableCell>
                          <TableCell>{concept.unit || '-'}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{concept.confidence}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {concepts.length > 15 && (
                    <p className="text-sm text-muted-foreground mt-2">
                      显示前15个概念，共{concepts.length}个
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="mapping-management" className="space-y-4">
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>创建映射规则</CardTitle>
                <CardDescription>
                  定义源协议到目标协议的转换规则
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="source-protocol">源协议</Label>
                    <Select 
                      value={mappingForm.source_protocol} 
                      onValueChange={(value) => setMappingForm(prev => ({...prev, source_protocol: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择源协议" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MIL-STD-6016B">MIL-STD-6016B</SelectItem>
                        <SelectItem value="MAVLink">MAVLink</SelectItem>
                        <SelectItem value="MQTT">MQTT</SelectItem>
                        <SelectItem value="CDM">CDM</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="target-protocol">目标协议</Label>
                    <Select 
                      value={mappingForm.target_protocol} 
                      onValueChange={(value) => setMappingForm(prev => ({...prev, target_protocol: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择目标协议" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MIL-STD-6016B">MIL-STD-6016B</SelectItem>
                        <SelectItem value="MAVLink">MAVLink</SelectItem>
                        <SelectItem value="MQTT">MQTT</SelectItem>
                        <SelectItem value="CDM">CDM</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="message-type">消息类型</Label>
                    <Input
                      id="message-type"
                      placeholder="例如: J2.0"
                      value={mappingForm.message_type}
                      onChange={(e) => setMappingForm(prev => ({...prev, message_type: e.target.value}))}
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>字段映射规则</Label>
                    <Button onClick={addMappingRule} variant="outline" size="sm">
                      添加规则
                    </Button>
                  </div>
                  
                  {mappingForm.rules.map((rule, index) => (
                    <div key={index} className="border rounded-md p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">规则 {index + 1}</span>
                        <Button 
                          onClick={() => removeMappingRule(index)} 
                          variant="destructive" 
                          size="sm"
                        >
                          删除
                        </Button>
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <Input
                          placeholder="源字段"
                          value={rule.source_field}
                          onChange={(e) => updateMappingRule(index, 'source_field', e.target.value)}
                        />
                        <Input
                          placeholder="CDM路径"
                          value={rule.cdm_path}
                          onChange={(e) => updateMappingRule(index, 'cdm_path', e.target.value)}
                        />
                        <Input
                          placeholder="目标字段"
                          value={rule.target_field}
                          onChange={(e) => updateMappingRule(index, 'target_field', e.target.value)}
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <Input
                          placeholder="缩放因子"
                          type="number"
                          value={rule.scale_factor || ''}
                          onChange={(e) => updateMappingRule(index, 'scale_factor', e.target.value ? parseFloat(e.target.value) : undefined)}
                        />
                        <Input
                          placeholder="偏移量"
                          type="number"
                          value={rule.offset || ''}
                          onChange={(e) => updateMappingRule(index, 'offset', e.target.value ? parseFloat(e.target.value) : undefined)}
                        />
                        <Input
                          placeholder="版本"
                          value={rule.version}
                          onChange={(e) => updateMappingRule(index, 'version', e.target.value)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <Button onClick={createMapping} disabled={loading}>
                  {loading ? "创建中..." : "创建映射规则"}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>现有映射规则</CardTitle>
                <CardDescription>
                  已配置的协议映射规则
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-[400px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>映射</TableHead>
                        <TableHead>版本</TableHead>
                        <TableHead>消息类型</TableHead>
                        <TableHead>规则数</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mappings.slice(0, 15).map((mapping, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">
                            {mapping.source_protocol} → {mapping.target_protocol}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{mapping.version}</Badge>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              {mapping.message_types.join(', ')}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="secondary">{mapping.total_rules}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {mappings.length > 15 && (
                    <p className="text-sm text-muted-foreground mt-2">
                      显示前15个映射，共{mappings.length}个
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="validation-testing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>校验与测试</CardTitle>
              <CardDescription>
                执行金标准回归测试和概念值校验
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-4">
                  <h4 className="font-semibold">金标准回归测试</h4>
                  <p className="text-sm text-muted-foreground">
                    运行预定义的金标准样例，验证转换的准确性和一致性
                  </p>
                  <Button onClick={runGoldenSetRegression} disabled={loading}>
                    {loading ? "测试中..." : "运行回归测试"}
                  </Button>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-semibold">概念值校验</h4>
                  <p className="text-sm text-muted-foreground">
                    校验特定概念的值是否符合定义的数据类型和约束
                  </p>
                  <div className="space-y-2">
                    <Input placeholder="概念路径，如 Track.Position.Latitude" />
                    <Input placeholder="要校验的值" />
                    <Button variant="outline" size="sm">校验值</Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system-overview" className="space-y-4">
          <div className="grid grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">CDM概念</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{concepts.length}</div>
                <p className="text-sm text-muted-foreground mt-1">
                  已定义的概念
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">映射规则</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mappings.length}</div>
                <p className="text-sm text-muted-foreground mt-1">
                  协议映射对
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">支持协议</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">4</div>
                <p className="text-sm text-muted-foreground mt-1">
                  MIL-STD-6016B, MAVLink, MQTT, CDM
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">四层架构</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">✅</div>
                <p className="text-sm text-muted-foreground mt-1">
                  语义层 → 映射层 → 校验层 → 运行层
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>四层法架构特性</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">第一层：语义层 (CDM + 本体)</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 统一语义模型 (Canonical Data Model)</li>
                    <li>• 概念化字段命名 (Track.Identity, Weapon.EngagementStatus)</li>
                    <li>• SI基准单位统一</li>
                    <li>• 坐标参考系标准化</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">第二层：映射层 (声明式规则)</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• YAML/JSON5声明式映射DSL</li>
                    <li>• 三段式映射 (源→CDM→目标)</li>
                    <li>• 版本治理和审计轨迹</li>
                    <li>• 人工介入只修改规则</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">第三层：校验层 (强约束)</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• JSON Schema/SHACL模式校验</li>
                    <li>• 物理一致性校验 (单位、取值域)</li>
                    <li>• 金标准样例回归测试</li>
                    <li>• 等价性验证</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">第四层：运行层 (协议中介)</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 运行时转换引擎</li>
                    <li>• 语义路由和负载均衡</li>
                    <li>• TTL和重放机制</li>
                    <li>• 软/硬实时分离通道</li>
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

export default CDMInteropInterface;
