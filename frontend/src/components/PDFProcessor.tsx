import React, { useState, useCallback } from 'react';
import { Button } from './ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Upload, FileText, CheckCircle, AlertCircle, Download, Eye } from 'lucide-react';

interface ProcessingResult {
  success: boolean;
  message: string;
  data?: {
    sim: any;
    validation_result: {
      valid: boolean;
      errors: any[];
      warnings: any[];
      coverage: number;
      confidence: number;
    };
    yaml_files: string[];
    report: any;
  };
  error?: string;
}

interface FieldData {
  field_name: string;
  bit_range: {
    start: number;
    end: number;
    length: number;
  };
  description?: string;
  units?: string[];
  confidence?: number;
  data_type?: string;
}

interface DFIDUIDICandidate {
  data_item_id: number;
  dfi: number;
  dui: number;
  di_name: string;
}

interface StandardInfo {
  name: string;
  description: string;
  editions: string[];
  message_types: string[];
  is_custom?: boolean;
}

interface CustomField {
  field_name: string;
  bit_range: {
    start: number;
    end: number;
    length: number;
  };
  description?: string;
  units?: string[];
  data_type?: string;
  confidence?: number;
}

interface CustomStandard {
  name: string;
  description: string;
  edition: string;
  message_types: string[];
  fields: CustomField[];
}

export default function PDFProcessor() {
  const [file, setFile] = useState<File | null>(null);
  const [standard, setStandard] = useState('MIL-STD-6016');
  const [edition, setEdition] = useState('B');
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [selectedFields, setSelectedFields] = useState<FieldData[]>([]);
  const [candidates, setCandidates] = useState<Record<string, DFIDUIDICandidate[]>>({});
  const [annotations, setAnnotations] = useState<Record<string, number>>({});
  const [standards, setStandards] = useState<Record<string, StandardInfo>>({});
  const [availableEditions, setAvailableEditions] = useState<string[]>(['B']);
  const [useCustomStandard, setUseCustomStandard] = useState(false);
  const [customStandard, setCustomStandard] = useState<CustomStandard>({
    name: '',
    description: '',
    edition: '1.0',
    message_types: ['CUSTOM'],
    fields: []
  });
  const [showCustomForm, setShowCustomForm] = useState(false);

  // 加载支持的标准
  const loadStandards = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/pdf/standards');
      const data = await response.json();
      if (data.success) {
        setStandards(data.standards);
        // 设置默认版本的可用版本
        const defaultStandard = data.standards['MIL-STD-6016'];
        if (defaultStandard) {
          setAvailableEditions(defaultStandard.editions);
        }
      }
    } catch (error) {
      console.error('Failed to load standards:', error);
    }
  }, []);

  // 处理标准变更
  const handleStandardChange = useCallback((newStandard: string) => {
    setStandard(newStandard);
    const standardInfo = standards[newStandard];
    if (standardInfo) {
      setAvailableEditions(standardInfo.editions);
      // 设置默认版本为第一个可用版本
      if (standardInfo.editions.length > 0) {
        setEdition(standardInfo.editions[0]);
      }
    }
  }, [standards]);

  // 添加字段到自定义标准
  const addFieldToCustomStandard = useCallback(() => {
    const newField: CustomField = {
      field_name: '',
      bit_range: { start: 0, end: 15, length: 16 },
      description: '',
      units: [],
      data_type: 'uint16',
      confidence: 0.8
    };
    setCustomStandard(prev => ({
      ...prev,
      fields: [...prev.fields, newField]
    }));
  }, []);

  // 更新自定义标准字段
  const updateCustomField = useCallback((index: number, field: CustomField) => {
    setCustomStandard(prev => ({
      ...prev,
      fields: prev.fields.map((f, i) => i === index ? field : f)
    }));
  }, []);

  // 删除自定义标准字段
  const removeCustomField = useCallback((index: number) => {
    setCustomStandard(prev => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index)
    }));
  }, []);

  // 保存自定义标准
  const saveCustomStandard = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/pdf/standards/custom', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(customStandard)
      });

      const data = await response.json();
      if (data.success) {
        alert(`自定义标准 '${customStandard.name}' 创建成功!`);
        setShowCustomForm(false);
        // 重新加载标准列表
        await loadStandards();
      } else {
        alert(`创建自定义标准失败: ${data.error}`);
      }
    } catch (error) {
      console.error('Error saving custom standard:', error);
      alert('保存自定义标准失败，请检查网络连接');
    }
  }, [customStandard, loadStandards]);

  // 使用自定义标准处理PDF
  const processPDFWithCustomStandard = useCallback(async () => {
    if (!file) return;

    setProcessing(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('standard_definition', JSON.stringify(customStandard));

    try {
      const response = await fetch('http://localhost:8000/api/pdf/upload/custom', {
        method: 'POST',
        body: formData,
      });

      const data: ProcessingResult = await response.json();
      setResult(data);

      if (data.success && data.data) {
        // 提取字段数据用于标注
        const fields: FieldData[] = [];
        if (data.data.sim?.fields) {
          data.data.sim.fields.forEach((field: any) => {
            fields.push({
              field_name: field.field_name,
              bit_range: field.bit_range,
              description: field.description,
              units: field.units,
              confidence: field.confidence,
              data_type: field.data_type
            });
          });
        }
        setSelectedFields(fields);

        // 为每个字段获取DFI/DUI/DI候选
        const candidatePromises = fields.map(async (field) => {
          try {
            const response = await fetch(`http://localhost:8000/api/di/candidates?field_name=${encodeURIComponent(field.field_name)}`);
            const data = await response.json();
            return { field_name: field.field_name, candidates: data.results || [] };
          } catch (error) {
            console.warn(`Failed to get candidates for ${field.field_name}:`, error);
            return { field_name: field.field_name, candidates: [] };
          }
        });

        const candidateResults = await Promise.all(candidatePromises);
        const candidateMap: Record<string, DFIDUIDICandidate[]> = {};
        candidateResults.forEach(({ field_name, candidates }) => {
          candidateMap[field_name] = candidates;
        });
        setCandidates(candidateMap);
      }
    } catch (error) {
      console.error('Error processing PDF with custom standard:', error);
      setResult({
        success: false,
        message: '处理失败',
        error: '网络错误'
      });
    } finally {
      setProcessing(false);
    }
  }, [file, customStandard]);

  // 组件挂载时加载标准
  React.useEffect(() => {
    loadStandards();
  }, [loadStandards]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setResult(null);
    } else {
      alert('请选择PDF文件');
    }
  }, []);

  const processPDF = async () => {
    if (!file) return;

    setProcessing(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('standard', standard);
    formData.append('edition', edition);

    try {
      const response = await fetch('http://localhost:8000/api/pdf/upload', {
        method: 'POST',
        body: formData,
      });

      const data: ProcessingResult = await response.json();
      setResult(data);

      if (data.success && data.data) {
        // 提取字段数据用于标注
        const fields: FieldData[] = [];
        if (data.data.sim?.fields) {
          data.data.sim.fields.forEach((field: any) => {
            fields.push({
              field_name: field.field_name,
              bit_range: field.bit_range,
              description: field.description,
              units: field.units,
              confidence: field.confidence,
              data_type: field.data_type
            });
          });
        }
        setSelectedFields(fields);

        // 为每个字段获取DFI/DUI/DI候选
        const candidatePromises = fields.map(async (field) => {
          try {
            const response = await fetch(`http://localhost:8000/api/di/candidates?field_name=${encodeURIComponent(field.field_name)}`);
            const data = await response.json();
            return { field_name: field.field_name, candidates: data.results || [] };
          } catch (error) {
            console.warn(`Failed to get candidates for ${field.field_name}:`, error);
            return { field_name: field.field_name, candidates: [] };
          }
        });

        const candidateResults = await Promise.all(candidatePromises);
        const candidateMap: Record<string, DFIDUIDICandidate[]> = {};
        candidateResults.forEach(({ field_name, candidates }) => {
          candidateMap[field_name] = candidates;
        });
        setCandidates(candidateMap);
      }
    } catch (error) {
      console.error('Error processing PDF:', error);
      setResult({
        success: false,
        message: '处理失败',
        error: '网络错误'
      });
    } finally {
      setProcessing(false);
    }
  };

  const handleAnnotation = (fieldName: string, dataItemId: number) => {
    setAnnotations(prev => ({
      ...prev,
      [fieldName]: dataItemId
    }));
  };

  const exportAnnotations = async () => {
    try {
      const annotationData = {
        annotations,
        timestamp: new Date().toISOString(),
        fields: selectedFields
      };

      const blob = new Blob([JSON.stringify(annotationData, null, 2)], {
        type: 'application/json'
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'annotations.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting annotations:', error);
    }
  };

  const importToDatabase = async (dryRun: boolean = true) => {
    if (!result?.data?.yaml_files) return;

    try {
      const response = await fetch('http://localhost:8000/api/import/yaml/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          yaml_dir: 'test_output',
          dry_run: dryRun
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`数据库导入${dryRun ? '试运行' : '实际'}成功!\n${data.message}`);
      } else {
        alert(`数据库导入失败: ${data.error}`);
      }
    } catch (error) {
      console.error('Error importing to database:', error);
      alert('数据库导入失败，请检查网络连接');
    }
  };

  const batchProcessPDFs = async () => {
    const pdfDir = prompt('请输入PDF文件目录路径:');
    if (!pdfDir) return;

    try {
      const response = await fetch('http://localhost:8000/api/pdf/batch-process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pdf_dir: pdfDir,
          output_dir: 'batch_output',
          standard: 'MIL-STD-6016',
          edition: 'B'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        alert(`批量处理完成!\n${data.message}`);
      } else {
        alert(`批量处理失败: ${data.error}`);
      }
    } catch (error) {
      console.error('Error batch processing:', error);
      alert('批量处理失败，请检查网络连接');
    }
  };

  const getBitRangeColor = (start: number, end: number) => {
    const length = end - start + 1;
    if (length <= 8) return 'bg-blue-200';
    if (length <= 16) return 'bg-green-200';
    if (length <= 32) return 'bg-yellow-200';
    return 'bg-red-200';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            PDF处理与标注
          </CardTitle>
          <CardDescription>
            上传PDF文件进行自动提取，然后进行半自动标注以完善数据质量
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            {/* 标准选择模式 */}
            <div className="flex items-center gap-4">
              <Label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="standardMode"
                  checked={!useCustomStandard}
                  onChange={() => setUseCustomStandard(false)}
                />
                使用预定义标准
              </Label>
              <Label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="standardMode"
                  checked={useCustomStandard}
                  onChange={() => setUseCustomStandard(true)}
                />
                使用自定义标准
              </Label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="file">PDF文件</Label>
                <Input
                  id="file"
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="mt-1"
                />
              </div>
              
              {!useCustomStandard ? (
                <>
                  <div>
                    <Label htmlFor="standard">标准</Label>
                    <Select value={standard} onValueChange={handleStandardChange}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择标准" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(standards).map(([key, info]) => (
                          <SelectItem key={key} value={key}>
                            <div className="flex flex-col">
                              <span className="font-medium">{info.name}</span>
                              <span className="text-xs text-gray-500">{info.description}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="edition">版本</Label>
                    <Select value={edition} onValueChange={setEdition}>
                      <SelectTrigger>
                        <SelectValue placeholder="选择版本" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableEditions.map((ed) => (
                          <SelectItem key={ed} value={ed}>
                            {ed}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </>
              ) : (
                <div className="md:col-span-2">
                  <Label>自定义标准</Label>
                  <div className="flex gap-2 mt-1">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => setShowCustomForm(true)}
                      className="flex-1"
                    >
                      定义自定义标准
                    </Button>
                    {customStandard.name && (
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => setShowCustomForm(true)}
                        className="flex-1"
                      >
                        编辑: {customStandard.name}
                      </Button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={useCustomStandard ? processPDFWithCustomStandard : processPDF} 
              disabled={!file || processing || (useCustomStandard && !customStandard.name)}
              className="flex-1"
            >
              {processing ? '处理中...' : '开始处理'}
            </Button>
            <Button 
              onClick={batchProcessPDFs}
              variant="outline"
              className="flex-1"
            >
              批量处理
            </Button>
          </div>
        </CardContent>
      </Card>

      {result && (
        <Tabs defaultValue="results" className="space-y-4">
          <TabsList>
            <TabsTrigger value="results">处理结果</TabsTrigger>
            <TabsTrigger value="fields">字段标注</TabsTrigger>
            <TabsTrigger value="validation">校验报告</TabsTrigger>
          </TabsList>

          <TabsContent value="results" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {result.success ? (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                  处理结果
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">{result.message}</p>
                
                {result.success && result.data && (
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {result.data.sim.j_messages?.length || 0}
                      </div>
                      <div className="text-sm text-gray-500">J消息</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {result.data.sim.dfi_dui_di?.length || 0}
                      </div>
                      <div className="text-sm text-gray-500">DFI/DUI/DI</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {Math.round(result.data.validation_result.coverage * 100)}%
                      </div>
                      <div className="text-sm text-gray-500">覆盖率</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-orange-600">
                        {Math.round(result.data.validation_result.confidence * 100)}%
                      </div>
                      <div className="text-sm text-gray-500">置信度</div>
                    </div>
                  </div>
                )}

                {result.data?.yaml_files && result.data.yaml_files.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium mb-2">生成的文件:</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.data.yaml_files.map((filename, index) => (
                        <Badge key={index} variant="outline" className="flex items-center gap-1">
                          <FileText className="h-3 w-3" />
                          {filename}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="fields" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>字段标注</CardTitle>
                <CardDescription>
                  为每个字段选择对应的DFI/DUI/DI，提高数据质量
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {selectedFields.map((field, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{field.field_name}</span>
                        <Badge 
                          className={`${getBitRangeColor(field.bit_range.start, field.bit_range.end)} text-black`}
                        >
                          {field.bit_range.start}-{field.bit_range.end}
                        </Badge>
                        {(field as any).data_type && (
                          <Badge variant="secondary">
                            {(field as any).data_type}
                          </Badge>
                        )}
                        {field.confidence && (
                          <Badge variant="outline">
                            置信度: {Math.round(field.confidence * 100)}%
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        长度: {field.bit_range.length} 位
                      </div>
                    </div>

                    {field.description && (
                      <p className="text-sm text-gray-600">{field.description}</p>
                    )}

                    {field.units && field.units.length > 0 && (
                      <div className="flex gap-1">
                        {field.units.map((unit, unitIndex) => (
                          <Badge key={unitIndex} variant="secondary" className="text-xs">
                            {unit}
                          </Badge>
                        ))}
                      </div>
                    )}

                    <div>
                      <Label className="text-sm font-medium">选择DFI/DUI/DI:</Label>
                      <Select
                        value={annotations[field.field_name]?.toString() || ''}
                        onValueChange={(value) => handleAnnotation(field.field_name, parseInt(value))}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="选择对应的数据项" />
                        </SelectTrigger>
                        <SelectContent>
                          {candidates[field.field_name]?.map((candidate) => (
                            <SelectItem 
                              key={candidate.data_item_id} 
                              value={candidate.data_item_id.toString()}
                            >
                              DFI-{candidate.dfi}/DUI-{candidate.dui}: {candidate.di_name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                ))}

                <div className="flex justify-between items-center pt-4 border-t">
                  <div className="text-sm text-gray-500">
                    已标注: {Object.keys(annotations).length} / {selectedFields.length}
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={exportAnnotations} variant="outline">
                      <Download className="h-4 w-4 mr-2" />
                      导出标注
                    </Button>
                    <Button onClick={() => importToDatabase(true)} variant="outline">
                      试运行导入
                    </Button>
                    <Button onClick={() => importToDatabase(false)} variant="default">
                      实际导入
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="validation" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>校验报告</CardTitle>
                <CardDescription>
                  数据质量校验结果和建议
                </CardDescription>
              </CardHeader>
              <CardContent>
                {result.data?.validation_result && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center">
                        <div className={`text-2xl font-bold ${result.data.validation_result.valid ? 'text-green-600' : 'text-red-600'}`}>
                          {result.data.validation_result.valid ? '✓' : '✗'}
                        </div>
                        <div className="text-sm text-gray-500">状态</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">
                          {result.data.validation_result.errors.length}
                        </div>
                        <div className="text-sm text-gray-500">错误</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">
                          {result.data.validation_result.warnings.length}
                        </div>
                        <div className="text-sm text-gray-500">警告</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-600">
                          {Math.round(result.data.validation_result.coverage * 100)}%
                        </div>
                        <div className="text-sm text-gray-500">覆盖率</div>
                      </div>
                    </div>

                    {result.data.validation_result.errors.length > 0 && (
                      <div>
                        <h4 className="font-medium text-red-600 mb-2">错误:</h4>
                        <div className="space-y-2">
                          {result.data.validation_result.errors.map((error, index) => (
                            <div key={index} className="p-3 bg-red-50 border border-red-200 rounded">
                              <div className="font-medium text-red-800">{error.message}</div>
                              <div className="text-sm text-red-600 mt-1">
                                字段: {error.field_path}
                              </div>
                              {error.suggested_fix && (
                                <div className="text-sm text-red-600 mt-1">
                                  建议: {error.suggested_fix}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {result.data.validation_result.warnings.length > 0 && (
                      <div>
                        <h4 className="font-medium text-yellow-600 mb-2">警告:</h4>
                        <div className="space-y-2">
                          {result.data.validation_result.warnings.map((warning, index) => (
                            <div key={index} className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                              <div className="font-medium text-yellow-800">{warning.message}</div>
                              <div className="text-sm text-yellow-600 mt-1">
                                字段: {warning.field_path}
                              </div>
                              {warning.suggested_fix && (
                                <div className="text-sm text-yellow-600 mt-1">
                                  建议: {warning.suggested_fix}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* 自定义标准定义对话框 */}
      {showCustomForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">定义自定义标准</h2>
              <Button
                variant="outline"
                onClick={() => setShowCustomForm(false)}
              >
                ✕
              </Button>
            </div>

            <div className="space-y-4">
              {/* 基本信息 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="customName">标准名称</Label>
                  <Input
                    id="customName"
                    value={customStandard.name}
                    onChange={(e) => setCustomStandard(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="例如: My Custom Protocol"
                  />
                </div>
                <div>
                  <Label htmlFor="customEdition">版本</Label>
                  <Input
                    id="customEdition"
                    value={customStandard.edition}
                    onChange={(e) => setCustomStandard(prev => ({ ...prev, edition: e.target.value }))}
                    placeholder="例如: 1.0"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="customDescription">描述</Label>
                <Input
                  id="customDescription"
                  value={customStandard.description}
                  onChange={(e) => setCustomStandard(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="描述这个自定义标准"
                />
              </div>

              {/* 字段定义 */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <Label>字段定义</Label>
                  <Button onClick={addFieldToCustomStandard} size="sm">
                    + 添加字段
                  </Button>
                </div>

                <div className="space-y-3">
                  {customStandard.fields.map((field, index) => (
                    <div key={index} className="border rounded-lg p-4 space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">字段 {index + 1}</span>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => removeCustomField(index)}
                        >
                          删除
                        </Button>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <Label>字段名称</Label>
                          <Input
                            value={field.field_name}
                            onChange={(e) => updateCustomField(index, { ...field, field_name: e.target.value })}
                            placeholder="例如: ALTITUDE"
                          />
                        </div>
                        <div>
                          <Label>数据类型</Label>
                          <Select
                            value={field.data_type || 'uint16'}
                            onValueChange={(value) => updateCustomField(index, { ...field, data_type: value })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="uint8">uint8</SelectItem>
                              <SelectItem value="uint16">uint16</SelectItem>
                              <SelectItem value="uint32">uint32</SelectItem>
                              <SelectItem value="int8">int8</SelectItem>
                              <SelectItem value="int16">int16</SelectItem>
                              <SelectItem value="int32">int32</SelectItem>
                              <SelectItem value="float32">float32</SelectItem>
                              <SelectItem value="float64">float64</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <Label>起始位</Label>
                          <Input
                            type="number"
                            value={field.bit_range.start}
                            onChange={(e) => {
                              const start = parseInt(e.target.value) || 0;
                              const length = field.bit_range.end - start + 1;
                              updateCustomField(index, {
                                ...field,
                                bit_range: { ...field.bit_range, start, length }
                              });
                            }}
                          />
                        </div>
                        <div>
                          <Label>结束位</Label>
                          <Input
                            type="number"
                            value={field.bit_range.end}
                            onChange={(e) => {
                              const end = parseInt(e.target.value) || 15;
                              const length = end - field.bit_range.start + 1;
                              updateCustomField(index, {
                                ...field,
                                bit_range: { ...field.bit_range, end, length }
                              });
                            }}
                          />
                        </div>
                        <div>
                          <Label>长度</Label>
                          <Input
                            type="number"
                            value={field.bit_range.length}
                            disabled
                            className="bg-gray-100"
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <Label>描述</Label>
                          <Input
                            value={field.description || ''}
                            onChange={(e) => updateCustomField(index, { ...field, description: e.target.value })}
                            placeholder="字段描述"
                          />
                        </div>
                        <div>
                          <Label>单位</Label>
                          <Input
                            value={field.units?.join(', ') || ''}
                            onChange={(e) => updateCustomField(index, { 
                              ...field, 
                              units: e.target.value.split(',').map(u => u.trim()).filter(Boolean)
                            })}
                            placeholder="例如: meters, feet"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex justify-end gap-2 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setShowCustomForm(false)}
                >
                  取消
                </Button>
                <Button
                  onClick={saveCustomStandard}
                  disabled={!customStandard.name || customStandard.fields.length === 0}
                >
                  保存标准
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
