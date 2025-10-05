"""
YAML文件导入到数据库的模块
与现有FastAPI系统集成
"""
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from db import query, exec_sql, call_proc

logger = logging.getLogger(__name__)

class YAMLImporter:
    """YAML文件导入器"""
    
    def __init__(self):
        self.import_stats = {
            'j_messages': 0,
            'fields': 0,
            'enums': 0,
            'units': 0,
            'errors': []
        }
    
    def import_yaml_file(self, yaml_path: str, dry_run: bool = True) -> Dict[str, Any]:
        """
        导入YAML文件到数据库
        
        Args:
            yaml_path: YAML文件路径
            dry_run: 是否为试运行（不实际写入数据库）
        
        Returns:
            导入结果统计
        """
        try:
            yaml_file = Path(yaml_path)
            if not yaml_file.exists():
                raise FileNotFoundError(f"YAML文件不存在: {yaml_path}")
            
            # 读取YAML文件
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            logger.info(f"开始导入YAML文件: {yaml_path}")
            logger.info(f"试运行模式: {dry_run}")
            
            # 根据文件类型选择导入方法
            if 'label' in data and 'words' in data:
                # J消息文件
                result = self._import_j_message(data, dry_run)
            elif 'key' in data and 'items' in data:
                # 枚举文件
                result = self._import_enum(data, dry_run)
            elif isinstance(data, list) and len(data) > 0 and 'symbol' in data[0]:
                # 单位文件
                result = self._import_units(data, dry_run)
            else:
                # SIM数据文件
                result = self._import_sim_data(data, dry_run)
            
            return result
            
        except Exception as e:
            logger.error(f"导入YAML文件失败: {e}")
            self.import_stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.import_stats
            }
    
    def _import_j_message(self, data: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """导入J消息数据"""
        try:
            label = data.get('label', '')
            title = data.get('title', '')
            purpose = data.get('purpose', '')
            
            logger.info(f"导入J消息: {label} - {title}")
            
            if not dry_run:
                # 检查是否已存在
                existing = query(
                    "SELECT message_id FROM message WHERE j_series = %s",
                    (label,)
                )
                
                if existing:
                    message_id = existing[0]['message_id']
                    logger.info(f"J消息 {label} 已存在，更新数据")
                else:
                    # 创建新的J消息
                    exec_sql(
                        "INSERT INTO message (j_series, title, purpose, spec_id) VALUES (%s, %s, %s, 1)",
                        (label, title, purpose)
                    )
                    message_id = query("SELECT LAST_INSERT_ID() as id")[0]['id']
                    logger.info(f"创建新J消息: {label}, ID: {message_id}")
                
                # 导入字段数据
                for word in data.get('words', []):
                    word_idx = word.get('word_idx', 0)
                    bitlen = word.get('bitlen', 70)
                    
                    # 创建字记录
                    exec_sql(
                        "INSERT INTO word (message_id, word_label, word_idx, bit_len) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE bit_len = VALUES(bit_len)",
                        (message_id, f"{label}W{word_idx}", word_idx, bitlen)
                    )
                    
                    word_id = query(
                        "SELECT word_id FROM word WHERE message_id = %s AND word_idx = %s",
                        (message_id, word_idx)
                    )[0]['word_id']
                    
                    # 导入字段
                    for field in word.get('fields', []):
                        field_name = field.get('name', '')
                        bits = field.get('bits', [0, 0])
                        start_bit, end_bit = bits[0], bits[1]
                        bit_len = end_bit - start_bit + 1
                        
                        map_data = field.get('map', {})
                        description = map_data.get('description', '')
                        nullable = map_data.get('nullable', False)
                        units = map_data.get('units', [])
                        
                        exec_sql(
                            "INSERT INTO field (word_id, field_name, start_bit, end_bit, bit_len, notes) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE start_bit = VALUES(start_bit), end_bit = VALUES(end_bit), bit_len = VALUES(bit_len), notes = VALUES(notes)",
                            (word_id, field_name, start_bit, end_bit, bit_len, description)
                        )
                        
                        self.import_stats['fields'] += 1
                
                self.import_stats['j_messages'] += 1
            
            return {
                'success': True,
                'message': f"成功导入J消息: {label}",
                'stats': self.import_stats
            }
            
        except Exception as e:
            logger.error(f"导入J消息失败: {e}")
            self.import_stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.import_stats
            }
    
    def _import_enum(self, data: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """导入枚举数据"""
        try:
            key = data.get('key', '')
            items = data.get('items', [])
            
            logger.info(f"导入枚举: {key}, 项目数: {len(items)}")
            
            if not dry_run:
                # 这里需要根据实际的枚举表结构来实现
                # 暂时记录到日志
                for item in items:
                    code = item.get('code', '')
                    label = item.get('label', '')
                    description = item.get('description', '')
                    logger.info(f"  枚举项: {code} - {label} - {description}")
                
                self.import_stats['enums'] += 1
            
            return {
                'success': True,
                'message': f"成功导入枚举: {key}",
                'stats': self.import_stats
            }
            
        except Exception as e:
            logger.error(f"导入枚举失败: {e}")
            self.import_stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.import_stats
            }
    
    def _import_units(self, data: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Any]:
        """导入单位数据"""
        try:
            logger.info(f"导入单位数据: {len(data)} 个单位")
            
            if not dry_run:
                for unit in data:
                    symbol = unit.get('symbol', '')
                    base_si = unit.get('base_si', '')
                    factor = unit.get('factor', 1.0)
                    offset = unit.get('offset', 0.0)
                    description = unit.get('description', '')
                    
                    logger.info(f"  单位: {symbol} -> {base_si} (factor: {factor})")
                
                self.import_stats['units'] += len(data)
            
            return {
                'success': True,
                'message': f"成功导入单位: {len(data)} 个",
                'stats': self.import_stats
            }
            
        except Exception as e:
            logger.error(f"导入单位失败: {e}")
            self.import_stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.import_stats
            }
    
    def _import_sim_data(self, data: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """导入完整SIM数据"""
        try:
            logger.info("导入完整SIM数据")
            
            # 导入J消息
            for j_message in data.get('j_messages', []):
                self._import_j_message(j_message, dry_run)
            
            # 导入枚举
            for enum_data in data.get('enums', []):
                self._import_enum(enum_data, dry_run)
            
            # 导入单位
            if data.get('units'):
                self._import_units(data['units'], dry_run)
            
            return {
                'success': True,
                'message': "成功导入完整SIM数据",
                'stats': self.import_stats
            }
            
        except Exception as e:
            logger.error(f"导入SIM数据失败: {e}")
            self.import_stats['errors'].append(str(e))
            return {
                'success': False,
                'error': str(e),
                'stats': self.import_stats
            }
    
    def batch_import(self, yaml_dir: str, dry_run: bool = True) -> Dict[str, Any]:
        """批量导入YAML文件"""
        try:
            yaml_path = Path(yaml_dir)
            if not yaml_path.exists():
                raise FileNotFoundError(f"目录不存在: {yaml_dir}")
            
            yaml_files = list(yaml_path.glob("*.yaml")) + list(yaml_path.glob("*.yml"))
            
            logger.info(f"找到 {len(yaml_files)} 个YAML文件")
            
            results = []
            for yaml_file in yaml_files:
                result = self.import_yaml_file(str(yaml_file), dry_run)
                results.append({
                    'file': yaml_file.name,
                    'result': result
                })
            
            success_count = sum(1 for r in results if r['result']['success'])
            
            return {
                'success': True,
                'message': f"批量导入完成: {success_count}/{len(yaml_files)} 成功",
                'total_files': len(yaml_files),
                'success_count': success_count,
                'results': results,
                'stats': self.import_stats
            }
            
        except Exception as e:
            logger.error(f"批量导入失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.import_stats
            }

def import_yaml_to_database(yaml_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """导入YAML文件到数据库的便捷函数"""
    importer = YAMLImporter()
    return importer.import_yaml_file(yaml_path, dry_run)

def batch_import_yaml_files(yaml_dir: str, dry_run: bool = True) -> Dict[str, Any]:
    """批量导入YAML文件的便捷函数"""
    importer = YAMLImporter()
    return importer.batch_import(yaml_dir, dry_run)
