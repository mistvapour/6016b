# backend/mqtt_adapter/export_yaml.py
import yaml
import json
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def export_yaml(sim_obj, out_path):
    """导出SIM对象为YAML文件"""
    try:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 确保数据可序列化
        cleaned_sim = clean_for_yaml(sim_obj)
        
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(cleaned_sim, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"Exported SIM to YAML: {out_path} ({out_path.stat().st_size} bytes)")
        return str(out_path)
        
    except Exception as e:
        logger.error(f"Failed to export YAML to {out_path}: {e}")
        raise

def export_json(sim_obj, out_path):
    """导出SIM对象为JSON文件（备选格式）"""
    try:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 确保数据可序列化
        cleaned_sim = clean_for_yaml(sim_obj)
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(cleaned_sim, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported SIM to JSON: {out_path} ({out_path.stat().st_size} bytes)")
        return str(out_path)
        
    except Exception as e:
        logger.error(f"Failed to export JSON to {out_path}: {e}")
        raise

def clean_for_yaml(obj):
    """清理对象，确保可以序列化为YAML"""
    if isinstance(obj, dict):
        return {k: clean_for_yaml(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [clean_for_yaml(item) for item in obj]
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    elif obj is None:
        return None
    else:
        # 对于其他类型，尝试转换为字符串
        return str(obj)

def export_individual_messages(sim_obj, output_dir):
    """将每个消息导出为单独的YAML文件"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    exported_files = []
    messages = sim_obj.get('spec_messages', [])
    
    for message in messages:
        label = message.get('label', 'unknown')
        filename = f"{label.lower()}_message.yaml"
        filepath = output_dir / filename
        
        # 创建单个消息的YAML结构
        message_yaml = {
            'standard': sim_obj.get('standard'),
            'edition': sim_obj.get('edition'),
            'message': message,
            'relevant_enums': get_relevant_enums(message, sim_obj.get('enums', []))
        }
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                yaml.safe_dump(clean_for_yaml(message_yaml), f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
            
            exported_files.append(str(filepath))
            logger.info(f"Exported {label} message to {filepath}")
            
        except Exception as e:
            logger.error(f"Failed to export {label} message: {e}")
    
    return exported_files

def get_relevant_enums(message, all_enums):
    """获取与消息相关的枚举定义"""
    relevant_enums = []
    
    # 检查消息中的字段是否引用了枚举
    for segment in message.get('segments', []):
        for field in segment.get('fields', []):
            field_name = field.get('name', '').lower()
            field_desc = field.get('description', '').lower()
            
            # 查找相关枚举
            for enum in all_enums:
                enum_key = enum.get('key', '').lower()
                
                # 如果字段名或描述包含枚举关键词
                if any(keyword in field_name or keyword in field_desc 
                      for keyword in ['qos', 'type', 'flag', 'property']):
                    if enum_key not in [e.get('key') for e in relevant_enums]:
                        relevant_enums.append(enum)
    
    return relevant_enums

def create_import_manifest(sim_obj, output_dir, yaml_files):
    """创建导入清单文件"""
    output_dir = Path(output_dir)
    manifest_path = output_dir / "import_manifest.yaml"
    
    manifest = {
        'metadata': {
            'standard': sim_obj.get('standard'),
            'edition': sim_obj.get('edition'),
            'created_at': datetime.now().isoformat(),
            'processor': 'mqtt_pdf_adapter'
        },
        'statistics': {
            'total_messages': len(sim_obj.get('spec_messages', [])),
            'total_enums': len(sim_obj.get('enums', [])),
            'total_fields': sim_obj.get('metadata', {}).get('total_fields', 0)
        },
        'files': [
            {
                'path': str(Path(f).relative_to(output_dir)),
                'type': 'yaml',
                'description': f"MQTT {Path(f).stem.replace('_message', '').upper()} message definition"
            }
            for f in yaml_files
        ]
    }
    
    try:
        with open(manifest_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(manifest, f, sort_keys=False, allow_unicode=True, default_flow_style=False, indent=2)
        
        logger.info(f"Created import manifest: {manifest_path}")
        return str(manifest_path)
        
    except Exception as e:
        logger.error(f"Failed to create import manifest: {e}")
        return None

def export_mqtt_complete(sim_obj, output_dir):
    """完整导出MQTT SIM数据"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting complete MQTT export to {output_dir}")
    
    exported_files = []
    
    try:
        # 1. 导出完整SIM
        main_yaml = output_dir / "mqtt_v5_complete.yaml"
        export_yaml(sim_obj, main_yaml)
        exported_files.append(str(main_yaml))
        
        # 2. 导出JSON格式（备选）
        main_json = output_dir / "mqtt_v5_complete.json"
        export_json(sim_obj, main_json)
        exported_files.append(str(main_json))
        
        # 3. 导出单独的消息文件
        individual_files = export_individual_messages(sim_obj, output_dir / "messages")
        exported_files.extend(individual_files)
        
        # 4. 导出枚举定义
        enums_yaml = output_dir / "mqtt_enums.yaml"
        enums_data = {
            'standard': sim_obj.get('standard'),
            'edition': sim_obj.get('edition'),
            'enums': sim_obj.get('enums', [])
        }
        export_yaml(enums_data, enums_yaml)
        exported_files.append(str(enums_yaml))
        
        # 5. 创建导入清单
        manifest_path = create_import_manifest(sim_obj, output_dir, individual_files)
        if manifest_path:
            exported_files.append(manifest_path)
        
        logger.info(f"Complete export finished: {len(exported_files)} files created")
        
        return {
            'success': True,
            'output_dir': str(output_dir),
            'files': exported_files,
            'main_yaml': str(main_yaml),
            'main_json': str(main_json),
            'manifest': manifest_path
        }
        
    except Exception as e:
        logger.error(f"Complete export failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'output_dir': str(output_dir),
            'files': exported_files
        }

def validate_yaml_output(yaml_path):
    """验证导出的YAML文件"""
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # 基本结构验证
        required_keys = ['standard', 'edition']
        issues = []
        
        for key in required_keys:
            if key not in data:
                issues.append(f"Missing required key: {key}")
        
        if 'spec_messages' in data:
            messages = data['spec_messages']
            if not isinstance(messages, list):
                issues.append("spec_messages should be a list")
            elif len(messages) == 0:
                issues.append("No messages found in spec_messages")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'message_count': len(data.get('spec_messages', [])),
            'enum_count': len(data.get('enums', []))
        }
        
    except Exception as e:
        return {
            'valid': False,
            'issues': [f"Failed to parse YAML: {e}"],
            'message_count': 0,
            'enum_count': 0
        }
