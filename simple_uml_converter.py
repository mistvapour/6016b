#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版UML转PNG转换器
支持多种转换方式，包括在线服务和本地工具
"""

import os
import subprocess
import sys
import argparse
import json
import requests
import base64
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleUMLConverter:
    """简化版UML转换器"""
    
    def __init__(self):
        self.supported_formats = {
            '.puml': 'plantuml',
            '.plantuml': 'plantuml',
            '.mmd': 'mermaid',
            '.mermaid': 'mermaid'
        }
        
        # PlantUML在线服务URL
        self.plantuml_server = "http://www.plantuml.com/plantuml/png/"
    
    def detect_format(self, file_path: Path) -> Optional[str]:
        """检测文件格式"""
        suffix = file_path.suffix.lower()
        return self.supported_formats.get(suffix)
    
    def convert(self, input_file: Path, output_dir: Path, 
                format_type: str = None, method: str = 'auto') -> bool:
        """转换UML文件为PNG"""
        if format_type is None:
            format_type = self.detect_format(input_file)
        
        if format_type == 'plantuml':
            return self._convert_plantuml(input_file, output_dir, method)
        elif format_type == 'mermaid':
            return self._convert_mermaid(input_file, output_dir, method)
        else:
            logger.error(f"不支持的文件格式: {input_file.suffix}")
            return False
    
    def _convert_plantuml(self, input_file: Path, output_dir: Path, method: str) -> bool:
        """转换PlantUML文件"""
        if method == 'auto':
            # 自动选择最佳方法
            if self._check_local_plantuml():
                return self._convert_plantuml_local(input_file, output_dir)
            else:
                return self._convert_plantuml_online(input_file, output_dir)
        elif method == 'local':
            return self._convert_plantuml_local(input_file, output_dir)
        elif method == 'online':
            return self._convert_plantuml_online(input_file, output_dir)
        else:
            logger.error(f"不支持的转换方法: {method}")
            return False
    
    def _convert_plantuml_local(self, input_file: Path, output_dir: Path) -> bool:
        """使用本地PlantUML转换"""
        try:
            # 检查PlantUML jar文件
            jar_path = self._find_plantuml_jar()
            if not jar_path:
                logger.error("未找到PlantUML jar文件")
                return False
            
            # 检查Java
            if not self._check_java():
                logger.error("Java未安装或不可用")
                return False
            
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建命令
            cmd = [
                'java',
                '-jar', str(jar_path),
                '-tpng',
                '-o', str(output_dir),
                str(input_file)
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                png_file = output_dir / f"{input_file.stem}.png"
                if png_file.exists():
                    logger.info(f"转换成功: {png_file}")
                    return True
                else:
                    logger.error(f"PNG文件未生成: {png_file}")
                    return False
            else:
                logger.error(f"PlantUML转换失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("转换超时")
            return False
        except Exception as e:
            logger.error(f"转换过程中出错: {e}")
            return False
    
    def _convert_plantuml_online(self, input_file: Path, output_dir: Path) -> bool:
        """使用在线PlantUML服务转换"""
        try:
            # 读取PlantUML源码
            with open(input_file, 'r', encoding='utf-8') as f:
                plantuml_code = f.read()
            
            # 编码PlantUML源码
            encoded = self._encode_plantuml(plantuml_code)
            
            # 构建请求URL
            url = f"{self.plantuml_server}{encoded}"
            
            logger.info(f"请求在线转换: {url[:100]}...")
            
            # 发送请求
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存PNG文件
            png_file = output_dir / f"{input_file.stem}.png"
            with open(png_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"在线转换成功: {png_file}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"在线转换失败: {e}")
            return False
        except Exception as e:
            logger.error(f"转换过程中出错: {e}")
            return False
    
    def _convert_mermaid(self, input_file: Path, output_dir: Path, method: str) -> bool:
        """转换Mermaid文件"""
        logger.warning("Mermaid转换功能暂未实现")
        return False
    
    def _find_plantuml_jar(self) -> Optional[Path]:
        """查找PlantUML jar文件"""
        possible_paths = [
            Path("plantuml.jar"),
            Path("华东师范大学硕_博_士论文LaTex模板_/plantuml.jar"),
            Path("./plantuml.jar"),
            Path("../plantuml.jar")
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"找到PlantUML jar文件: {path}")
                return path
        
        return None
    
    def _check_java(self) -> bool:
        """检查Java是否可用"""
        try:
            result = subprocess.run(['java', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_local_plantuml(self) -> bool:
        """检查本地PlantUML是否可用"""
        return self._find_plantuml_jar() is not None and self._check_java()
    
    def _encode_plantuml(self, code: str) -> str:
        """编码PlantUML源码为URL安全格式"""
        # 移除注释和空行
        lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith('@startuml') and not line.startswith('@enduml'):
                lines.append(line)
        
        # 重新组合
        clean_code = '\n'.join(lines)
        
        # 使用PlantUML的编码方式
        import zlib
        compressed = zlib.compress(clean_code.encode('utf-8'))
        encoded = base64.b64encode(compressed).decode('ascii')
        
        # 转换为PlantUML URL编码
        result = ""
        for i in range(0, len(encoded), 3):
            chunk = encoded[i:i+3]
            if len(chunk) == 3:
                result += chunk
            else:
                result += chunk
        
        return result
    
    def batch_convert(self, input_dir: Path, output_dir: Path, 
                     recursive: bool = False, method: str = 'auto') -> Dict[str, Any]:
        """批量转换UML文件"""
        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        # 查找UML文件
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        uml_files = []
        for suffix in self.supported_formats.keys():
            uml_files.extend(input_dir.glob(f"{pattern}{suffix}"))
        
        results['total'] = len(uml_files)
        
        if results['total'] == 0:
            logger.warning(f"在目录 {input_dir} 中未找到UML文件")
            return results
        
        logger.info(f"找到 {results['total']} 个UML文件")
        
        # 转换每个文件
        for uml_file in uml_files:
            logger.info(f"正在转换: {uml_file.name}")
            
            result = {
                'file': str(uml_file),
                'success': False,
                'error': None
            }
            
            try:
                if self.convert(uml_file, output_dir, method=method):
                    results['success'] += 1
                    result['success'] = True
                else:
                    results['failed'] += 1
                    result['error'] = "转换失败"
            except Exception as e:
                results['failed'] += 1
                result['error'] = str(e)
                logger.error(f"转换 {uml_file} 时出错: {e}")
            
            results['details'].append(result)
        
        logger.info(f"批量转换完成: {results['success']}/{results['total']} 成功")
        return results

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='简化版UML转PNG转换器')
    parser.add_argument('input', nargs='?', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='输出目录', default='./output')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='递归处理子目录')
    parser.add_argument('-f', '--format', choices=['plantuml', 'mermaid'],
                       help='强制指定格式')
    parser.add_argument('-m', '--method', choices=['auto', 'local', 'online'],
                       default='auto', help='转换方法')
    parser.add_argument('--batch', action='store_true', 
                       help='批量转换模式')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='详细输出')
    parser.add_argument('--test', action='store_true', 
                       help='测试环境')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建转换器
    converter = SimpleUMLConverter()
    
    if args.test:
        # 测试模式
        print("环境测试")
        print("=" * 50)
        print(f"Java可用: {converter._check_java()}")
        print(f"PlantUML jar文件: {converter._find_plantuml_jar()}")
        print(f"本地PlantUML可用: {converter._check_local_plantuml()}")
        return
    
    if not args.input:
        parser.error("需要指定输入文件或目录")
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"输入路径不存在: {input_path}")
        return
    
    if args.batch or input_path.is_dir():
        # 批量转换模式
        logger.info("批量转换模式")
        results = converter.batch_convert(input_path, output_path, args.recursive, args.method)
        
        # 保存结果报告
        report_file = output_path / 'conversion_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"转换报告已保存: {report_file}")
        
    else:
        # 单文件转换模式
        logger.info("单文件转换模式")
        if converter.convert(input_path, output_path, args.format, args.method):
            logger.info("转换成功")
        else:
            logger.error("转换失败")

if __name__ == "__main__":
    main()
