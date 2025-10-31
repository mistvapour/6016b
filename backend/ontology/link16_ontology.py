#!/usr/bin/env python3
"""
Link16术语库建设：
- 建立6016B标准术语本体
- 单位/枚举字典入库
- 术语映射与一致性验证
- 支持字段自动链接到标准库
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set
import json
from pathlib import Path


@dataclass
class TermNode:
    """术语节点"""
    id: str
    label: str
    description: str
    category: str  # field, unit, enum, message, etc.
    aliases: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)
    standard_ref: str = "MIL-STD-6016B"
    confidence: float = 1.0


@dataclass
class UnitsEntry:
    """单位条目"""
    symbol: str
    name: str
    base_si: str
    factor: float
    offset: float = 0.0
    description: str = ""
    aliases: List[str] = field(default_factory=list)


@dataclass
class EnumEntry:
    """枚举条目"""
    key: str
    name: str
    items: List[Dict[str, str]]  # [{"code": "0", "label": "Safe", "description": "..."}]
    description: str = ""
    aliases: List[str] = field(default_factory=list)


class Link16Ontology:
    """Link16术语本体"""
    
    def __init__(self):
        self.terms: Dict[str, TermNode] = {}
        self.units: Dict[str, UnitsEntry] = {}
        self.enums: Dict[str, EnumEntry] = {}
        self.field_mappings: Dict[str, str] = {}  # field_name -> term_id
        
        # 初始化标准术语
        self._init_standard_terms()
        self._init_standard_units()
        self._init_standard_enums()
    
    def _init_standard_terms(self):
        """初始化标准术语"""
        standard_terms = [
            # J消息类型
            TermNode("J0", "Initial Entry", "Initial entry message", "message", 
                    aliases=["J0.0", "Initial", "Entry"]),
            TermNode("J1", "Track Management", "Track management message", "message",
                    aliases=["J1.0", "Track", "Management"]),
            TermNode("J2", "Air Track", "Air track message", "message",
                    aliases=["J2.0", "Air", "Track"]),
            TermNode("J3", "Surface Track", "Surface track message", "message",
                    aliases=["J3.0", "Surface", "Track"]),
            TermNode("J4", "Weapon Status", "Weapon status message", "message",
                    aliases=["J4.0", "Weapon", "Status"]),
            TermNode("J5", "Electronic Warfare", "Electronic warfare message", "message",
                    aliases=["J5.0", "EW", "Electronic Warfare"]),
            TermNode("J6", "Information Management", "Information management message", "message",
                    aliases=["J6.0", "Information", "Management"]),
            TermNode("J7", "Route Planning", "Route planning message", "message",
                    aliases=["J7.0", "Route", "Planning"]),
            TermNode("J8", "Unit Designation", "Unit designation message", "message",
                    aliases=["J8.0", "Unit", "Designation"]),
            TermNode("J9", "Command", "Command message", "message",
                    aliases=["J9.0", "Command"]),
            
            # 字段术语
            TermNode("track_id", "Track ID", "Track identification number", "field",
                    aliases=["TrackID", "Track Number", "ID"]),
            TermNode("latitude", "Latitude", "Geographic latitude", "field",
                    aliases=["Lat", "Latitude", "Y Coordinate"]),
            TermNode("longitude", "Longitude", "Geographic longitude", "field",
                    aliases=["Lon", "Longitude", "X Coordinate"]),
            TermNode("altitude", "Altitude", "Altitude above sea level", "field",
                    aliases=["Alt", "Height", "Elevation"]),
            TermNode("speed", "Speed", "Ground speed", "field",
                    aliases=["Velocity", "Ground Speed"]),
            TermNode("heading", "Heading", "Track heading", "field",
                    aliases=["Course", "Bearing", "Direction"]),
            TermNode("weapon_status", "Weapon Status", "Current weapon status", "field",
                    aliases=["Weapon State", "Arms Status"]),
            TermNode("range", "Range", "Distance to target", "field",
                    aliases=["Distance", "Range to Target"]),
            TermNode("bearing", "Bearing", "Bearing to target", "field",
                    aliases=["Azimuth", "Direction to Target"]),
            TermNode("elevation", "Elevation", "Elevation angle", "field",
                    aliases=["Elevation Angle", "Vertical Angle"]),
        ]
        
        for term in standard_terms:
            self.terms[term.id] = term
    
    def _init_standard_units(self):
        """初始化标准单位"""
        standard_units = [
            UnitsEntry("deg", "degrees", "rad", 0.0174532925, description="Angular measurement"),
            UnitsEntry("rad", "radians", "rad", 1.0, description="Angular measurement (SI base)"),
            UnitsEntry("m", "meters", "m", 1.0, description="Length measurement (SI base)"),
            UnitsEntry("km", "kilometers", "m", 1000.0, description="Length measurement"),
            UnitsEntry("nm", "nautical miles", "m", 1852.0, description="Nautical distance"),
            UnitsEntry("ft", "feet", "m", 0.3048, description="Length measurement"),
            UnitsEntry("kts", "knots", "m/s", 0.514444, description="Speed measurement"),
            UnitsEntry("m/s", "meters per second", "m/s", 1.0, description="Speed measurement (SI base)"),
            UnitsEntry("km/h", "kilometers per hour", "m/s", 0.277778, description="Speed measurement"),
            UnitsEntry("sec", "seconds", "s", 1.0, description="Time measurement"),
            UnitsEntry("min", "minutes", "s", 60.0, description="Time measurement"),
            UnitsEntry("hour", "hours", "s", 3600.0, description="Time measurement"),
        ]
        
        for unit in standard_units:
            self.units[unit.symbol] = unit
    
    def _init_standard_enums(self):
        """初始化标准枚举"""
        standard_enums = [
            EnumEntry(
                "weapon_status",
                "Weapon Status",
                [
                    {"code": "0", "label": "Safe", "description": "Weapon is safe"},
                    {"code": "1", "label": "Armed", "description": "Weapon is armed"},
                    {"code": "2", "label": "Firing", "description": "Weapon is firing"},
                    {"code": "3", "label": "Malfunction", "description": "Weapon malfunction"},
                ],
                description="Weapon system status codes"
            ),
            EnumEntry(
                "track_type",
                "Track Type",
                [
                    {"code": "0", "label": "Unknown", "description": "Unknown track type"},
                    {"code": "1", "label": "Air", "description": "Air track"},
                    {"code": "2", "label": "Surface", "description": "Surface track"},
                    {"code": "3", "label": "Subsurface", "description": "Subsurface track"},
                ],
                description="Track type classification"
            ),
            EnumEntry(
                "threat_level",
                "Threat Level",
                [
                    {"code": "0", "label": "Unknown", "description": "Unknown threat level"},
                    {"code": "1", "label": "Low", "description": "Low threat"},
                    {"code": "2", "label": "Medium", "description": "Medium threat"},
                    {"code": "3", "label": "High", "description": "High threat"},
                ],
                description="Threat level assessment"
            ),
        ]
        
        for enum in standard_enums:
            self.enums[enum.key] = enum
    
    def find_term(self, text: str) -> Optional[TermNode]:
        """查找术语"""
        text_lower = text.lower().strip()
        
        # 直接匹配
        for term_id, term in self.terms.items():
            if text_lower == term.label.lower():
                return term
            if text_lower == term_id.lower():
                return term
            if text_lower in [alias.lower() for alias in term.aliases]:
                return term
        
        # 模糊匹配
        for term_id, term in self.terms.items():
            if text_lower in term.label.lower() or term.label.lower() in text_lower:
                return term
        
        return None
    
    def find_unit(self, text: str) -> Optional[UnitsEntry]:
        """查找单位"""
        text_lower = text.lower().strip()
        
        # 直接匹配
        if text_lower in self.units:
            return self.units[text_lower]
        
        # 别名匹配
        for unit in self.units.values():
            if text_lower in [alias.lower() for alias in unit.aliases]:
                return unit
            if text_lower == unit.name.lower():
                return unit
        
        return None
    
    def find_enum(self, text: str) -> Optional[EnumEntry]:
        """查找枚举"""
        text_lower = text.lower().strip()
        
        # 直接匹配
        if text_lower in self.enums:
            return self.enums[text_lower]
        
        # 别名匹配
        for enum in self.enums.values():
            if text_lower in [alias.lower() for alias in enum.aliases]:
                return enum
            if text_lower == enum.name.lower():
                return enum
        
        return None
    
    def link_field_to_term(self, field_name: str) -> Optional[str]:
        """将字段链接到术语"""
        term = self.find_term(field_name)
        if term:
            self.field_mappings[field_name] = term.id
            return term.id
        return None
    
    def get_consistency_report(self, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成一致性报告"""
        report = {
            "total_fields": len(fields),
            "linked_fields": 0,
            "unlinked_fields": 0,
            "unit_matches": 0,
            "enum_matches": 0,
            "issues": [],
            "suggestions": []
        }
        
        for field in fields:
            field_name = field.get("field", field.get("name", ""))
            if not field_name:
                continue
            
            # 术语链接
            term_id = self.link_field_to_term(field_name)
            if term_id:
                report["linked_fields"] += 1
            else:
                report["unlinked_fields"] += 1
                report["issues"].append(f"Field '{field_name}' not found in ontology")
            
            # 单位匹配
            units = field.get("units")
            if units:
                unit_entry = self.find_unit(units)
                if unit_entry:
                    report["unit_matches"] += 1
                else:
                    report["issues"].append(f"Unit '{units}' not found in ontology")
            
            # 枚举匹配
            enum_ref = field.get("enum_ref")
            if enum_ref:
                enum_entry = self.find_enum(enum_ref)
                if enum_entry:
                    report["enum_matches"] += 1
                else:
                    report["issues"].append(f"Enum '{enum_ref}' not found in ontology")
        
        # 生成建议
        if report["unlinked_fields"] > 0:
            report["suggestions"].append("Consider adding missing field terms to ontology")
        if report["unit_matches"] < report["total_fields"]:
            report["suggestions"].append("Review unit mappings for consistency")
        
        return report
    
    def export_ontology(self, output_dir: Path):
        """导出本体"""
        output_dir.mkdir(exist_ok=True)
        
        # 导出术语
        terms_data = {
            term_id: {
                "id": term.id,
                "label": term.label,
                "description": term.description,
                "category": term.category,
                "aliases": term.aliases,
                "synonyms": term.synonyms,
                "parent": term.parent,
                "children": term.children,
                "standard_ref": term.standard_ref,
                "confidence": term.confidence
            }
            for term_id, term in self.terms.items()
        }
        
        with open(output_dir / "terms.json", 'w', encoding='utf-8') as f:
            json.dump(terms_data, f, ensure_ascii=False, indent=2)
        
        # 导出单位
        units_data = {
            symbol: {
                "symbol": unit.symbol,
                "name": unit.name,
                "base_si": unit.base_si,
                "factor": unit.factor,
                "offset": unit.offset,
                "description": unit.description,
                "aliases": unit.aliases
            }
            for symbol, unit in self.units.items()
        }
        
        with open(output_dir / "units.json", 'w', encoding='utf-8') as f:
            json.dump(units_data, f, ensure_ascii=False, indent=2)
        
        # 导出枚举
        enums_data = {
            key: {
                "key": enum.key,
                "name": enum.name,
                "items": enum.items,
                "description": enum.description,
                "aliases": enum.aliases
            }
            for key, enum in self.enums.items()
        }
        
        with open(output_dir / "enums.json", 'w', encoding='utf-8') as f:
            json.dump(enums_data, f, ensure_ascii=False, indent=2)
        
        # 导出字段映射
        with open(output_dir / "field_mappings.json", 'w', encoding='utf-8') as f:
            json.dump(self.field_mappings, f, ensure_ascii=False, indent=2)


__all__ = ["Link16Ontology", "TermNode", "UnitsEntry", "EnumEntry"]
