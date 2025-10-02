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
}

interface DFIDUIDICandidate {
  data_item_id: number;
  dfi: number;
  dui: number;
  di_name: string;
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
      const response = await fetch('/api/pdf/process', {
        method: 'POST',
        body: formData,
      });

      const data: ProcessingResult = await response.json();
      setResult(data);

      if (data.success && data.data) {
        // 提取字段数据用于标注
        const fields: FieldData[] = [];
        data.data.sim.j_messages?.forEach((message: any) => {
          message.words?.forEach((word: any) => {
            word.fields?.forEach((field: any) => {
              fields.push({
                field_name: field.name,
                bit_range: {
                  start: field.bits[0],
                  end: field.bits[1],
                  length: field.bits[1] - field.bits[0] + 1
                },
                description: field.map?.description,
                units: field.map?.units,
                confidence: field.confidence
              });
            });
          });
        });
        setSelectedFields(fields);

        // 为每个字段获取DFI/DUI/DI候选
        const candidatePromises = fields.map(async (field) => {
          const response = await fetch(`/api/di/candidates?field_name=${encodeURIComponent(field.field_name)}`);
          const data = await response.json();
          return { field_name: field.field_name, candidates: data.results };
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
      const response = await fetch('/api/import/yaml/batch', {
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
      const response = await fetch('/api/pdf/batch-process', {
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
            <div>
              <Label htmlFor="standard">标准</Label>
              <Select value={standard} onValueChange={setStandard}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="MIL-STD-6016">MIL-STD-6016</SelectItem>
                  <SelectItem value="MIL-STD-1553">MIL-STD-1553</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edition">版本</Label>
              <Select value={edition} onValueChange={setEdition}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="A">A</SelectItem>
                  <SelectItem value="B">B</SelectItem>
                  <SelectItem value="C">C</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-2">
            <Button 
              onClick={processPDF} 
              disabled={!file || processing}
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
    </div>
  );
}
