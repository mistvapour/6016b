"""
批量PDF处理模块
支持批量处理多个PDF文件
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json

from pdf_adapter.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

class BatchProcessor:
    """批量PDF处理器"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.processor = PDFProcessor()
        self.batch_stats = {
            'total_files': 0,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None,
            'results': []
        }
    
    async def process_batch(self, pdf_dir: str, output_dir: str, 
                          standard: str = "MIL-STD-6016", 
                          edition: str = "B") -> Dict[str, Any]:
        """
        批量处理PDF文件
        
        Args:
            pdf_dir: PDF文件目录
            output_dir: 输出目录
            standard: 标准名称
            edition: 版本
        
        Returns:
            批量处理结果
        """
        try:
            pdf_path = Path(pdf_dir)
            if not pdf_path.exists():
                raise FileNotFoundError(f"PDF目录不存在: {pdf_dir}")
            
            # 查找所有PDF文件
            pdf_files = list(pdf_path.glob("*.pdf"))
            if not pdf_files:
                return {
                    'success': False,
                    'message': f"在目录 {pdf_dir} 中未找到PDF文件",
                    'stats': self.batch_stats
                }
            
            self.batch_stats['total_files'] = len(pdf_files)
            self.batch_stats['start_time'] = datetime.now().isoformat()
            
            logger.info(f"开始批量处理 {len(pdf_files)} 个PDF文件")
            
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 并发处理PDF文件
            semaphore = asyncio.Semaphore(self.max_workers)
            tasks = []
            
            for pdf_file in pdf_files:
                task = self._process_single_file(
                    semaphore, str(pdf_file), str(output_path), standard, edition
                )
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.batch_stats['failed'] += 1
                    self.batch_stats['results'].append({
                        'file': pdf_files[i].name,
                        'success': False,
                        'error': str(result)
                    })
                else:
                    self.batch_stats['processed'] += 1
                    if result['success']:
                        self.batch_stats['successful'] += 1
                    else:
                        self.batch_stats['failed'] += 1
                    self.batch_stats['results'].append(result)
            
            self.batch_stats['end_time'] = datetime.now().isoformat()
            
            # 生成批量处理报告
            report_path = output_path / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.batch_stats, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'message': f"批量处理完成: {self.batch_stats['successful']}/{self.batch_stats['total_files']} 成功",
                'stats': self.batch_stats,
                'report_path': str(report_path)
            }
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.batch_stats
            }
    
    async def _process_single_file(self, semaphore: asyncio.Semaphore, 
                                 pdf_path: str, output_dir: str, 
                                 standard: str, edition: str) -> Dict[str, Any]:
        """处理单个PDF文件"""
        async with semaphore:
            try:
                logger.info(f"处理文件: {Path(pdf_path).name}")
                
                # 创建文件特定的输出目录
                file_output_dir = Path(output_dir) / Path(pdf_path).stem
                file_output_dir.mkdir(exist_ok=True)
                
                # 处理PDF文件
                result = self.processor.process_pdf(pdf_path, str(file_output_dir))
                
                return {
                    'file': Path(pdf_path).name,
                    'success': result['success'],
                    'output_dir': str(file_output_dir),
                    'yaml_files': result.get('yaml_files', []),
                    'validation': result.get('validation_result', {}),
                    'error': result.get('error')
                }
                
            except Exception as e:
                logger.error(f"处理文件 {pdf_path} 失败: {e}")
                return {
                    'file': Path(pdf_path).name,
                    'success': False,
                    'error': str(e)
                }
    
    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """获取批量处理状态"""
        # 这里可以实现基于batch_id的状态查询
        # 暂时返回当前统计信息
        return {
            'batch_id': batch_id,
            'status': 'completed' if self.batch_stats['end_time'] else 'processing',
            'stats': self.batch_stats
        }

# 全局批量处理器实例
_batch_processor = BatchProcessor()

async def process_pdf_batch(pdf_dir: str, output_dir: str, 
                          standard: str = "MIL-STD-6016", 
                          edition: str = "B") -> Dict[str, Any]:
    """批量处理PDF文件的便捷函数"""
    return await _batch_processor.process_batch(pdf_dir, output_dir, standard, edition)

def get_batch_status(batch_id: str) -> Dict[str, Any]:
    """获取批量处理状态的便捷函数"""
    return _batch_processor.get_batch_status(batch_id)
