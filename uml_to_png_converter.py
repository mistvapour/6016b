#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UML转PNG转换器
支持PlantUML、Mermaid等UML格式转换为PNG图片
"""

import os
import subprocess
import sys
import argparse
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('uml_converter.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class UMLConverter:
    """UML转换器基类"""
    
    def __init__(self):
        self.supported_formats = {
            '.puml': 'plantuml',
            '.plantuml': 'plantuml',
            '.mmd': 'mermaid',
            '.mermaid': 'mermaid'
        }
    
    def detect_format(self, file_path: Path) -> Optional[str]:
        """检测文件格式"""
        suffix = file_path.suffix.lower()
        return self.supported_formats.get(suffix)
    
    def convert(self, input_file: Path, output_dir: Path, 
                format_type: str = None) -> bool:
        """转换UML文件为PNG"""
        if format_type is None:
            format_type = self.detect_format(input_file)
        
        if format_type == 'plantuml':
            return self._convert_plantuml(input_file, output_dir)
        elif format_type == 'mermaid':
            return self._convert_mermaid(input_file, output_dir)
        else:
            logger.error(f"不支持的文件格式: {input_file.suffix}")
            return False
    
    def _convert_plantuml(self, input_file: Path, output_dir: Path) -> bool:
        """转换PlantUML文件"""
        try:
            # 检查PlantUML是否可用
            if not self._check_plantuml():
                logger.error("PlantUML未安装或不可用")
                return False
            
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建命令
            cmd = [
                'plantuml',
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
    
    def _convert_mermaid(self, input_file: Path, output_dir: Path) -> bool:
        """转换Mermaid文件"""
        try:
            # 检查mermaid-cli是否可用
            if not self._check_mermaid():
                logger.error("Mermaid CLI未安装或不可用")
                return False
            
            # 确保输出目录存在
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 构建输出文件路径
            output_file = output_dir / f"{input_file.stem}.png"
            
            # 构建命令
            cmd = [
                'mmdc',
                '-i', str(input_file),
                '-o', str(output_file),
                '-t', 'neutral',
                '-b', 'white'
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                if output_file.exists():
                    logger.info(f"转换成功: {output_file}")
                    return True
                else:
                    logger.error(f"PNG文件未生成: {output_file}")
                    return False
            else:
                logger.error(f"Mermaid转换失败: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("转换超时")
            return False
        except Exception as e:
            logger.error(f"转换过程中出错: {e}")
            return False
    
    def _check_plantuml(self) -> bool:
        """检查PlantUML是否可用"""
        try:
            result = subprocess.run(['plantuml', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def _check_mermaid(self) -> bool:
        """检查Mermaid CLI是否可用"""
        try:
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def batch_convert(self, input_dir: Path, output_dir: Path, 
                     recursive: bool = False) -> Dict[str, Any]:
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
                if self.convert(uml_file, output_dir):
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

def install_dependencies():
    """安装必要的依赖"""
    dependencies = {
        'plantuml': 'plantuml',
        'mermaid': '@mermaid-js/mermaid-cli'
    }
    
    for name, package in dependencies.items():
        logger.info(f"检查 {name} 依赖...")
        
        if name == 'plantuml':
            # 检查PlantUML
            try:
                result = subprocess.run(['plantuml', '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info("PlantUML已安装")
                    continue
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            logger.warning("PlantUML未安装，请手动安装:")
            logger.warning("1. 下载 plantuml.jar")
            logger.warning("2. 安装 Java 运行环境")
            logger.warning("3. 将 plantuml.jar 添加到 PATH")
            
        elif name == 'mermaid':
            # 检查Mermaid CLI
            try:
                result = subprocess.run(['mmdc', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info("Mermaid CLI已安装")
                    continue
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            logger.info(f"正在安装 {package}...")
            try:
                subprocess.run(['npm', 'install', '-g', package], 
                              check=True, timeout=300)
                logger.info(f"{package} 安装成功")
            except subprocess.CalledProcessError as e:
                logger.error(f"{package} 安装失败: {e}")
            except subprocess.TimeoutExpired:
                logger.error(f"{package} 安装超时")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='UML转PNG转换器')
    parser.add_argument('input', nargs='?', help='输入文件或目录')
    parser.add_argument('-o', '--output', help='输出目录', default='./output')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='递归处理子目录')
    parser.add_argument('-f', '--format', choices=['plantuml', 'mermaid'],
                       help='强制指定格式')
    parser.add_argument('--install', action='store_true', 
                       help='安装依赖')
    parser.add_argument('--batch', action='store_true', 
                       help='批量转换模式')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.install:
        install_dependencies()
        return
    
    if not args.input:
        parser.error("需要指定输入文件或目录，或使用 --install 安装依赖")
    
    # 创建转换器
    converter = UMLConverter()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if not input_path.exists():
        logger.error(f"输入路径不存在: {input_path}")
        return
    
    if args.batch or input_path.is_dir():
        # 批量转换模式
        logger.info("批量转换模式")
        results = converter.batch_convert(input_path, output_path, args.recursive)
        
        # 保存结果报告
        report_file = output_path / 'conversion_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"转换报告已保存: {report_file}")
        
    else:
        # 单文件转换模式
        logger.info("单文件转换模式")
        if converter.convert(input_path, output_path, args.format):
            logger.info("转换成功")
        else:
            logger.error("转换失败")

if __name__ == "__main__":
    main()
