"""
中间语义模型(SIM)构建模块
将PDF提取的数据转换为标准化的语义模型
"""
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
import yaml
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class JMessageField:
    """J消息字段"""
    name: str
    bits: List[int]  # [start, end]
    map: Dict[str, Any]
    description: Optional[str] = None
    units: Optional[List[str]] = None
    resolution: Optional[str] = None

@dataclass
class JMessageWord:
    """J消息字"""
    type: str  # "Initial", "Extension", etc.
    word_idx: int
    bitlen: int
    fields: List[JMessageField]

@dataclass
class JMessage:
    """J消息"""
    label: str  # 如 "J10.2"
    title: str
    purpose: Optional[str]
    words: List[JMessageWord]

@dataclass
class DFI:
    """数据字段标识符"""
    num: int
    name: str
    description: Optional[str] = None

@dataclass
class DUI:
    """数据使用标识符"""
    num: int
    name: str
    dfi_num: int
    description: Optional[str] = None

@dataclass
class DI:
    """数据项"""
    dui_num: int
    code: str
    name: str
    description: Optional[str] = None

@dataclass
class DFIDUIDI:
    """DFI/DUI/DI组合"""
    dfi: DFI
    dui: List[DUI]
    di: List[DI]

@dataclass
class EnumItem:
    """枚举项"""
    code: str
    label: str
    description: Optional[str] = None

@dataclass
class Enum:
    """枚举定义"""
    key: str
    items: List[EnumItem]

@dataclass
class Unit:
    """单位定义"""
    symbol: str
    base_si: str
    factor: float
    offset: float = 0.0
    description: str = ""

@dataclass
class VersionRule:
    """版本规则"""
    from_version: str
    to_version: str
    changes: List[Dict[str, Any]]

@dataclass
class SIM:
    """中间语义模型"""
    standard: str
    edition: str
    j_messages: List[JMessage]
    dfi_dui_di: List[DFIDUIDI]
    enums: List[Enum]
    units: List[Unit]
    version_rules: List[VersionRule]
    metadata: Dict[str, Any]

class SIMBuilder:
    """SIM构建器"""
    
    def __init__(self, standard: str = "MIL-STD-6016", edition: str = "B"):
        self.standard = standard
        self.edition = edition
        self.sim = SIM(
            standard=standard,
            edition=edition,
            j_messages=[],
            dfi_dui_di=[],
            enums=[],
            units=[],
            version_rules=[],
            metadata={}
        )
    
    def add_j_message_from_section(self, section_data: Dict[str, Any]) -> JMessage:
        """从章节数据添加J消息"""
        label = section_data.get('label', '')
        title = section_data.get('title', '')
        fields_data = section_data.get('fields', [])
        
        # 构建字段
        fields = []
        for field_data in fields_data:
            field = JMessageField(
                name=field_data.get('field_name', ''),
                bits=field_data.get('bit_range', {}).get('start', 0),
                map={
                    'nullable': self._infer_nullable(field_data),
                    'description': field_data.get('description', ''),
                    'units': field_data.get('units', [])
                },
                description=field_data.get('description'),
                units=field_data.get('units'),
                resolution=field_data.get('resolution')
            )
            fields.append(field)
        
        # 构建字
        word = JMessageWord(
            type="Initial",
            word_idx=0,
            bitlen=70,  # 标准字长
            fields=fields
        )
        
        # 构建消息
        message = JMessage(
            label=label,
            title=title,
            purpose=None,
            words=[word]
        )
        
        self.sim.j_messages.append(message)
        return message
    
    def add_dfiduidi_from_appendix(self, appendix_data: Dict[str, Any]) -> DFIDUIDI:
        """从Appendix B数据添加DFI/DUI/DI"""
        dfi_data = appendix_data.get('dfi', {})
        dui_data = appendix_data.get('dui', [])
        di_data = appendix_data.get('di', [])
        
        # 构建DFI
        dfi = DFI(
            num=dfi_data.get('num', 0),
            name=dfi_data.get('name', ''),
            description=dfi_data.get('description')
        )
        
        # 构建DUI列表
        duis = []
        for dui_item in dui_data:
            dui = DUI(
                num=dui_item.get('num', 0),
                name=dui_item.get('name', ''),
                dfi_num=dfi.num,
                description=dui_item.get('description')
            )
            duis.append(dui)
        
        # 构建DI列表
        dis = []
        for di_item in di_data:
            di = DI(
                dui_num=di_item.get('dui_num', 0),
                code=di_item.get('code', ''),
                name=di_item.get('name', ''),
                description=di_item.get('description')
            )
            dis.append(di)
        
        dfiduidi = DFIDUIDI(dfi=dfi, dui=duis, di=dis)
        self.sim.dfi_dui_di.append(dfiduidi)
        return dfiduidi
    
    def add_enum(self, enum_data: Dict[str, Any]) -> Enum:
        """添加枚举定义"""
        enum = Enum(
            key=enum_data.get('key', ''),
            items=[
                EnumItem(
                    code=item.get('code', ''),
                    label=item.get('label', ''),
                    description=item.get('description')
                )
                for item in enum_data.get('items', [])
            ]
        )
        self.sim.enums.append(enum)
        return enum
    
    def add_unit(self, unit_data: Dict[str, Any]) -> Unit:
        """添加单位定义"""
        unit = Unit(
            symbol=unit_data.get('symbol', ''),
            base_si=unit_data.get('base_si', ''),
            factor=unit_data.get('factor', 1.0),
            offset=unit_data.get('offset', 0.0),
            description=unit_data.get('description', '')
        )
        self.sim.units.append(unit)
        return unit
    
    def add_version_rule(self, rule_data: Dict[str, Any]) -> VersionRule:
        """添加版本规则"""
        rule = VersionRule(
            from_version=rule_data.get('from_version', ''),
            to_version=rule_data.get('to_version', ''),
            changes=rule_data.get('changes', [])
        )
        self.sim.version_rules.append(rule)
        return rule
    
    def _infer_nullable(self, field_data: Dict[str, Any]) -> bool:
        """推断字段是否可为空"""
        description = field_data.get('description', '').lower()
        nullable_indicators = ['optional', 'may be', 'can be', 'if available', 'if present']
        return any(indicator in description for indicator in nullable_indicators)
    
    def build_sim(self) -> SIM:
        """构建完整的SIM"""
        self.sim.metadata = {
            'created_at': datetime.now().isoformat(),
            'version': '1.0',
            'source': 'pdf_extraction'
        }
        return self.sim

class YAMLExporter:
    """YAML导出器"""
    
    def __init__(self, sim: SIM):
        self.sim = sim
    
    def export_j_message_yaml(self, message: JMessage) -> str:
        """导出J消息为YAML格式"""
        yaml_data = {
            'label': message.label,
            'title': message.title,
            'purpose': message.purpose,
            'words': []
        }
        
        for word in message.words:
            word_data = {
                'type': word.type,
                'word_idx': word.word_idx,
                'bitlen': word.bitlen,
                'fields': []
            }
            
            for field in word.fields:
                field_data = {
                    'name': field.name,
                    'bits': field.bits,
                    'map': field.map
                }
                if field.description:
                    field_data['description'] = field.description
                if field.units:
                    field_data['units'] = field.units
                if field.resolution:
                    field_data['resolution'] = field.resolution
                
                word_data['fields'].append(field_data)
            
            yaml_data['words'].append(word_data)
        
        return yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True)
    
    def export_dfiduidi_yaml(self, dfiduidi: DFIDUIDI) -> str:
        """导出DFI/DUI/DI为YAML格式"""
        yaml_data = {
            'dfi': {
                'num': dfiduidi.dfi.num,
                'name': dfiduidi.dfi.name
            },
            'dui': [
                {
                    'num': dui.num,
                    'name': dui.name,
                    'dfi_num': dui.dfi_num
                }
                for dui in dfiduidi.dui
            ],
            'di': [
                {
                    'dui_num': di.dui_num,
                    'code': di.code,
                    'name': di.name
                }
                for di in dfiduidi.di
            ]
        }
        
        return yaml.dump(yaml_data, default_flow_style=False, allow_unicode=True)
    
    def export_all_yaml(self) -> Dict[str, str]:
        """导出所有数据为YAML格式"""
        yaml_files = {}
        
        # 导出J消息
        for message in self.sim.j_messages:
            filename = f"{message.label.replace('.', '_')}.yaml"
            yaml_files[filename] = self.export_j_message_yaml(message)
        
        # 导出DFI/DUI/DI
        for i, dfiduidi in enumerate(self.sim.dfi_dui_di):
            filename = f"dfiduidi_{dfiduidi.dfi.num}_{i}.yaml"
            yaml_files[filename] = self.export_dfiduidi_yaml(dfiduidi)
        
        # 导出枚举
        for enum in self.sim.enums:
            filename = f"enum_{enum.key}.yaml"
            yaml_files[filename] = yaml.dump(asdict(enum), default_flow_style=False, allow_unicode=True)
        
        # 导出单位
        if self.sim.units:
            units_data = [asdict(unit) for unit in self.sim.units]
            yaml_files['units.yaml'] = yaml.dump(units_data, default_flow_style=False, allow_unicode=True)
        
        return yaml_files

def build_sim_from_pdf_data(
    j_sections: List[Dict[str, Any]], 
    appendix_sections: List[Dict[str, Any]],
    standard: str = "MIL-STD-6016",
    edition: str = "B"
) -> SIM:
    """从PDF数据构建SIM"""
    builder = SIMBuilder(standard, edition)
    
    # 处理J消息章节
    for section in j_sections:
        builder.add_j_message_from_section(section)
    
    # 处理Appendix B章节
    for section in appendix_sections:
        builder.add_dfiduidi_from_appendix(section)
    
    return builder.build_sim()

def export_sim_to_yaml(sim: SIM, output_dir: str = ".") -> Dict[str, str]:
    """将SIM导出为YAML文件"""
    exporter = YAMLExporter(sim)
    yaml_files = exporter.export_all_yaml()
    
    # 保存到文件
    import os
    for filename, content in yaml_files.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return yaml_files
