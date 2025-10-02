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

interface MessageStandard {
  value: string;
  name: string;
  description: string;
}

interface SemanticCategory {
  value: string;
  name: string;
  description: string;
}

interface FieldType {
  value: string;
  name: string;
  description: string;
}

interface SemanticField {
  semantic_id: string;
  name: string;
  category: string;
  type: string;
  unit?: string;
  description: string;
  aliases: string[];
}

interface MessageMapping {
  source_message: string;
  target_message: string;
  source_standard: string;
  target_standard: string;
  field_count: number;
  bidirectional: boolean;
  priority: number;
}

interface FieldMapping {
  source_field: string;
  target_field: string;
  transform_function?: string;
  scaling_factor?: number;
  offset?: number;
  enum_mapping?: Record<string, string>;
}

const SemanticInteropInterface: React.FC = () => {
  const [standards, setStandards] = useState<MessageStandard[]>([]);
  const [categories, setCategories] = useState<SemanticCategory[]>([]);
  const [fieldTypes, setFieldTypes] = useState<FieldType[]>([]);
  const [semanticFields, setSemanticFields] = useState<SemanticField[]>([]);
  const [messageMappings, setMessageMappings] = useState<MessageMapping[]>([]);
  const [loading, setLoading] = useState(false);
  
  // 消息处理状态
  const [messageInput, setMessageInput] = useState('{}');
  const [selectedStandard, setSelectedStandard] = useState('');
  const [processResult, setProcessResult] = useState<any>(null);
  
  // 映射创建状态
  const [mappingForm, setMappingForm] = useState({
    source_message: '',
    target_message: '',
    source_standard: '',
    target_standard: '',
    field_mappings: [] as FieldMapping[]
  });
  
  // 语义标注状态
  const [annotationForm, setAnnotationForm] = useState({
    field_name: '',
    semantic_id: '',
    category: '',
    field_type: '',
    unit: '',
    description: '',
    aliases: ''
  });

  const API_BASE = 'http://localhost:8000/api/semantic';

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      // 并行加载基础数据
      const [standardsRes, categoriesRes, fieldTypesRes, semanticFieldsRes, mappingsRes] = await Promise.all([
        fetch(`${API_BASE}/standards`),
        fetch(`${API_BASE}/semantic-categories`),
        fetch(`${API_BASE}/field-types`),
        fetch(`${API_BASE}/semantic-fields`),
        fetch(`${API_BASE}/mappings`)
      ]);

      const [standardsData, categoriesData, fieldTypesData, semanticFieldsData, mappingsData] = await Promise.all([
        standardsRes.json(),
        categoriesRes.json(),
        fieldTypesRes.json(),
        semanticFieldsRes.json(),
        mappingsRes.json()
      ]);

      setStandards(standardsData.standards || []);
      setCategories(categoriesData.categories || []);
      setFieldTypes(fieldTypesData.field_types || []);
      setSemanticFields(semanticFieldsData.fields || []);
      setMessageMappings(mappingsData.mappings || []);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      toast({
        title: "加载失败",
        description: "无法加载初始数据，请检查API连接",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const analyzeMessage = async () => {
    if (!messageInput || !selectedStandard) {
      toast({
        title: "输入不完整",
        description: "请输入消息内容并选择消息标准",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const message = JSON.parse(messageInput);
      const response = await fetch(`${API_BASE}/analyze-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          standard: selectedStandard
        })
      });

      const data = await response.json();
      if (data.success) {
        setProcessResult(data);
        toast({
          title: "分析完成",
          description: "消息语义分析成功完成",
          variant: "default"
        });
      } else {
        throw new Error(data.detail || '分析失败');
      }
    } catch (error) {
      console.error('Message analysis failed:', error);
      toast({
        title: "分析失败",
        description: error instanceof Error ? error.message : "消息分析失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const processMessageWithRouting = async () => {
    if (!messageInput || !selectedStandard) {
      toast({
        title: "输入不完整",
        description: "请输入消息内容并选择消息标准",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const message = JSON.parse(messageInput);
      const response = await fetch(`${API_BASE}/process-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          standard: selectedStandard
        })
      });

      const data = await response.json();
      if (data.success) {
        setProcessResult(data);
        toast({
          title: "处理完成",
          description: `消息已成功处理并路由到 ${data.result.routed_messages.length} 个目标`,
          variant: "default"
        });
      } else {
        throw new Error(data.detail || '处理失败');
      }
    } catch (error) {
      console.error('Message processing failed:', error);
      toast({
        title: "处理失败",
        description: error instanceof Error ? error.message : "消息处理失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const createSemanticAnnotation = async () => {
    if (!annotationForm.field_name || !annotationForm.semantic_id || !annotationForm.category || !annotationForm.field_type) {
      toast({
        title: "输入不完整",
        description: "请填写所有必需字段",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/semantic-annotation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          field_name: annotationForm.field_name,
          semantic_id: annotationForm.semantic_id,
          category: annotationForm.category,
          field_type: annotationForm.field_type,
          unit: annotationForm.unit || null,
          description: annotationForm.description,
          aliases: annotationForm.aliases.split(',').map(s => s.trim()).filter(s => s)
        })
      });

      const data = await response.json();
      if (data.success) {
        toast({
          title: "标注成功",
          description: "语义标注已成功创建",
          variant: "default"
        });
        
        // 重新加载语义字段
        const fieldsRes = await fetch(`${API_BASE}/semantic-fields`);
        const fieldsData = await fieldsRes.json();
        setSemanticFields(fieldsData.fields || []);
        
        // 清空表单
        setAnnotationForm({
          field_name: '',
          semantic_id: '',
          category: '',
          field_type: '',
          unit: '',
          description: '',
          aliases: ''
        });
      } else {
        throw new Error(data.detail || '标注失败');
      }
    } catch (error) {
      console.error('Semantic annotation failed:', error);
      toast({
        title: "标注失败",
        description: error instanceof Error ? error.message : "语义标注创建失败",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const addFieldMapping = () => {
    setMappingForm(prev => ({
      ...prev,
      field_mappings: [...prev.field_mappings, {
        source_field: '',
        target_field: '',
        transform_function: '',
        scaling_factor: undefined,
        offset: undefined,
        enum_mapping: {}
      }]
    }));
  };

  const removeFieldMapping = (index: number) => {
    setMappingForm(prev => ({
      ...prev,
      field_mappings: prev.field_mappings.filter((_, i) => i !== index)
    }));
  };

  const updateFieldMapping = (index: number, field: keyof FieldMapping, value: any) => {
    setMappingForm(prev => ({
      ...prev,
      field_mappings: prev.field_mappings.map((mapping, i) => 
        i === index ? { ...mapping, [field]: value } : mapping
      )
    }));
  };

  const createMessageMapping = async () => {
    if (!mappingForm.source_message || !mappingForm.target_message || 
        !mappingForm.source_standard || !mappingForm.target_standard) {
      toast({
        title: "输入不完整",
        description: "请填写所有必需的映射信息",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/create-mapping`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mappingForm)
      });

      const data = await response.json();
      if (data.success) {
        toast({
          title: "映射成功",
          description: "消息映射已成功创建",
          variant: "default"
        });
        
        // 重新加载映射列表
        const mappingsRes = await fetch(`${API_BASE}/mappings`);
        const mappingsData = await mappingsRes.json();
        setMessageMappings(mappingsData.mappings || []);
        
        // 清空表单
        setMappingForm({
          source_message: '',
          target_message: '',
          source_standard: '',
          target_standard: '',
          field_mappings: []
        });
      } else {
        throw new Error(data.detail || '映射创建失败');
      }
    } catch (error) {
      console.error('Message mapping failed:', error);
      toast({
        title: "映射失败",
        description: error instanceof Error ? error.message : "消息映射创建失败",
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
          <h1 className="text-3xl font-bold tracking-tight">语义互操作管理</h1>
          <p className="text-muted-foreground">管理消息标准间的语义映射和转发规则</p>
        </div>
        <Badge variant="outline" className="text-sm">
          {standards.length} 个支持的标准
        </Badge>
      </div>

      <Tabs defaultValue="message-processing" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="message-processing">消息处理</TabsTrigger>
          <TabsTrigger value="semantic-annotation">语义标注</TabsTrigger>
          <TabsTrigger value="mapping-management">映射管理</TabsTrigger>
          <TabsTrigger value="system-overview">系统概览</TabsTrigger>
        </TabsList>

        <TabsContent value="message-processing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>消息语义分析与路由</CardTitle>
              <CardDescription>
                输入消息内容，系统将自动分析语义并执行跨标准路由
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="message-input">消息内容 (JSON格式)</Label>
                  <textarea
                    id="message-input"
                    className="min-h-[200px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    placeholder='{"message_type": "J2.0", "track_id": "12345", "latitude": 39.9042, "longitude": 116.4074}'
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="standard-select">消息标准</Label>
                  <Select value={selectedStandard} onValueChange={setSelectedStandard}>
                    <SelectTrigger>
                      <SelectValue placeholder="选择消息标准" />
                    </SelectTrigger>
                    <SelectContent>
                      {standards.map((standard) => (
                        <SelectItem key={standard.value} value={standard.value}>
                          {standard.value}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button onClick={analyzeMessage} disabled={loading}>
                  {loading ? "分析中..." : "语义分析"}
                </Button>
                <Button onClick={processMessageWithRouting} disabled={loading} variant="outline">
                  {loading ? "处理中..." : "处理并路由"}
                </Button>
              </div>

              {processResult && (
                <div className="mt-4 space-y-4">
                  <div>
                    <h4 className="font-semibold">处理结果</h4>
                    <div className="mt-2 rounded-md bg-muted p-4">
                      <pre className="text-sm overflow-auto">
                        {JSON.stringify(processResult, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="semantic-annotation" className="space-y-4">
          <div className="grid grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>创建语义标注</CardTitle>
                <CardDescription>
                  为字段定义语义信息，提高跨标准映射的准确性
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="field-name">字段名称</Label>
                    <Input
                      id="field-name"
                      placeholder="例如: latitude"
                      value={annotationForm.field_name}
                      onChange={(e) => setAnnotationForm(prev => ({...prev, field_name: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="semantic-id">语义标识符</Label>
                    <Input
                      id="semantic-id"
                      placeholder="例如: sem.pos.latitude"
                      value={annotationForm.semantic_id}
                      onChange={(e) => setAnnotationForm(prev => ({...prev, semantic_id: e.target.value}))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category-select">语义类别</Label>
                    <Select 
                      value={annotationForm.category} 
                      onValueChange={(value) => setAnnotationForm(prev => ({...prev, category: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择类别" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((category) => (
                          <SelectItem key={category.value} value={category.value}>
                            {category.value}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="field-type-select">字段类型</Label>
                    <Select 
                      value={annotationForm.field_type} 
                      onValueChange={(value) => setAnnotationForm(prev => ({...prev, field_type: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择类型" />
                      </SelectTrigger>
                      <SelectContent>
                        {fieldTypes.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.value}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="unit">单位 (可选)</Label>
                    <Input
                      id="unit"
                      placeholder="例如: degree"
                      value={annotationForm.unit}
                      onChange={(e) => setAnnotationForm(prev => ({...prev, unit: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="aliases">别名 (逗号分隔)</Label>
                    <Input
                      id="aliases"
                      placeholder="例如: lat, y_coord"
                      value={annotationForm.aliases}
                      onChange={(e) => setAnnotationForm(prev => ({...prev, aliases: e.target.value}))}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">描述</Label>
                  <Input
                    id="description"
                    placeholder="字段描述"
                    value={annotationForm.description}
                    onChange={(e) => setAnnotationForm(prev => ({...prev, description: e.target.value}))}
                  />
                </div>

                <Button onClick={createSemanticAnnotation} disabled={loading}>
                  {loading ? "创建中..." : "创建语义标注"}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>现有语义字段</CardTitle>
                <CardDescription>
                  已定义的语义字段列表
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-[400px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>字段名</TableHead>
                        <TableHead>类别</TableHead>
                        <TableHead>类型</TableHead>
                        <TableHead>单位</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {semanticFields.slice(0, 20).map((field, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{field.name}</TableCell>
                          <TableCell>
                            <Badge variant="secondary">{field.category}</Badge>
                          </TableCell>
                          <TableCell>{field.type}</TableCell>
                          <TableCell>{field.unit || '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {semanticFields.length > 20 && (
                    <p className="text-sm text-muted-foreground mt-2">
                      显示前20个字段，共{semanticFields.length}个
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
                <CardTitle>创建消息映射</CardTitle>
                <CardDescription>
                  定义不同标准间的消息转换规则
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="source-message">源消息类型</Label>
                    <Input
                      id="source-message"
                      placeholder="例如: J2.0"
                      value={mappingForm.source_message}
                      onChange={(e) => setMappingForm(prev => ({...prev, source_message: e.target.value}))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="target-message">目标消息类型</Label>
                    <Input
                      id="target-message"
                      placeholder="例如: GLOBAL_POSITION_INT"
                      value={mappingForm.target_message}
                      onChange={(e) => setMappingForm(prev => ({...prev, target_message: e.target.value}))}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="source-standard">源标准</Label>
                    <Select 
                      value={mappingForm.source_standard} 
                      onValueChange={(value) => setMappingForm(prev => ({...prev, source_standard: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择源标准" />
                      </SelectTrigger>
                      <SelectContent>
                        {standards.map((standard) => (
                          <SelectItem key={standard.value} value={standard.value}>
                            {standard.value}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="target-standard">目标标准</Label>
                    <Select 
                      value={mappingForm.target_standard} 
                      onValueChange={(value) => setMappingForm(prev => ({...prev, target_standard: value}))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="选择目标标准" />
                      </SelectTrigger>
                      <SelectContent>
                        {standards.map((standard) => (
                          <SelectItem key={standard.value} value={standard.value}>
                            {standard.value}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>字段映射</Label>
                    <Button onClick={addFieldMapping} variant="outline" size="sm">
                      添加字段映射
                    </Button>
                  </div>
                  
                  {mappingForm.field_mappings.map((mapping, index) => (
                    <div key={index} className="border rounded-md p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">字段映射 {index + 1}</span>
                        <Button 
                          onClick={() => removeFieldMapping(index)} 
                          variant="destructive" 
                          size="sm"
                        >
                          删除
                        </Button>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <Input
                          placeholder="源字段"
                          value={mapping.source_field}
                          onChange={(e) => updateFieldMapping(index, 'source_field', e.target.value)}
                        />
                        <Input
                          placeholder="目标字段"
                          value={mapping.target_field}
                          onChange={(e) => updateFieldMapping(index, 'target_field', e.target.value)}
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-2">
                        <Input
                          placeholder="转换函数"
                          value={mapping.transform_function || ''}
                          onChange={(e) => updateFieldMapping(index, 'transform_function', e.target.value)}
                        />
                        <Input
                          placeholder="缩放因子"
                          type="number"
                          value={mapping.scaling_factor || ''}
                          onChange={(e) => updateFieldMapping(index, 'scaling_factor', e.target.value ? parseFloat(e.target.value) : undefined)}
                        />
                        <Input
                          placeholder="偏移量"
                          type="number"
                          value={mapping.offset || ''}
                          onChange={(e) => updateFieldMapping(index, 'offset', e.target.value ? parseFloat(e.target.value) : undefined)}
                        />
                      </div>
                    </div>
                  ))}
                </div>

                <Button onClick={createMessageMapping} disabled={loading}>
                  {loading ? "创建中..." : "创建消息映射"}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>现有消息映射</CardTitle>
                <CardDescription>
                  已配置的消息映射规则
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="max-h-[400px] overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>源消息</TableHead>
                        <TableHead>目标消息</TableHead>
                        <TableHead>标准转换</TableHead>
                        <TableHead>字段数</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {messageMappings.slice(0, 15).map((mapping, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{mapping.source_message}</TableCell>
                          <TableCell>{mapping.target_message}</TableCell>
                          <TableCell>
                            <div className="text-sm">
                              {mapping.source_standard} → {mapping.target_standard}
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{mapping.field_count}</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {messageMappings.length > 15 && (
                    <p className="text-sm text-muted-foreground mt-2">
                      显示前15个映射，共{messageMappings.length}个
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="system-overview" className="space-y-4">
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">支持的标准</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{standards.length}</div>
                <div className="space-y-1 mt-2">
                  {standards.map((standard) => (
                    <Badge key={standard.value} variant="outline" className="mr-1">
                      {standard.value}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">语义字段</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{semanticFields.length}</div>
                <p className="text-sm text-muted-foreground mt-1">
                  已定义的语义字段
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base">消息映射</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{messageMappings.length}</div>
                <p className="text-sm text-muted-foreground mt-1">
                  配置的映射规则
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>系统功能特性</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">自动语义分析</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 智能识别消息字段的语义含义</li>
                    <li>• 自动匹配已定义的语义标识符</li>
                    <li>• 检测潜在的跨标准映射机会</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">消息路由转发</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 基于规则的自动消息路由</li>
                    <li>• 支持多目标标准转发</li>
                    <li>• 实时消息格式转换</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">人工标注增强</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 可视化语义字段标注界面</li>
                    <li>• 自定义语义类别和类型</li>
                    <li>• 别名和描述信息管理</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">映射规则管理</h4>
                  <ul className="text-sm space-y-1 text-muted-foreground">
                    <li>• 灵活的字段映射配置</li>
                    <li>• 支持数据转换函数</li>
                    <li>• 双向映射自动生成</li>
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

export default SemanticInteropInterface;
