#!/usr/bin/env python3
"""
消息定义模型 schema（最小版）与 JSON/XML 互转。
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import json
import xml.etree.ElementTree as ET


@dataclass
class FieldConstraint:
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    enum: Optional[List[str]] = None
    pattern: Optional[str] = None


@dataclass
class MessageField:
    name: str
    dtype: str
    units: Optional[str] = None
    description: Optional[str] = None
    bits: Optional[List[int]] = None  # [start, end]
    children: Optional[List["MessageField"]] = None
    constraint: Optional[FieldConstraint] = None


@dataclass
class MessageDefinition:
    label: str
    title: str
    version: str = "6016B"
    fields: List[MessageField] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @staticmethod
    def from_json(s: str) -> "MessageDefinition":
        obj = json.loads(s)
        def build_field(d: Dict[str, Any]) -> MessageField:
            constraint = None
            if d.get("constraint"):
                constraint = FieldConstraint(**d["constraint"])
            children = None
            if d.get("children"):
                children = [build_field(c) for c in d["children"]]
            return MessageField(
                name=d["name"], dtype=d["dtype"], units=d.get("units"),
                description=d.get("description"), bits=d.get("bits"),
                children=children, constraint=constraint,
            )
        fields = [build_field(f) for f in obj.get("fields", [])]
        return MessageDefinition(label=obj["label"], title=obj["title"], version=obj.get("version", "6016B"), fields=fields)

    def to_xml(self) -> str:
        root = ET.Element("MessageDefinition", attrib={"label": self.label, "title": self.title, "version": self.version})
        def field_to_xml(parent: ET.Element, f: MessageField) -> None:
            e = ET.SubElement(parent, "Field", attrib={"name": f.name, "dtype": f.dtype})
            if f.units: ET.SubElement(e, "Units").text = f.units
            if f.description: ET.SubElement(e, "Description").text = f.description
            if f.bits: ET.SubElement(e, "Bits").text = f"{f.bits[0]}-{f.bits[1]}"
            if f.constraint:
                c = ET.SubElement(e, "Constraint")
                if f.constraint.required: c.set("required", "true")
                if f.constraint.min_value is not None: c.set("min", str(f.constraint.min_value))
                if f.constraint.max_value is not None: c.set("max", str(f.constraint.max_value))
                if f.constraint.pattern: c.set("pattern", f.constraint.pattern)
                if f.constraint.enum:
                    enums = ET.SubElement(c, "Enum")
                    for item in f.constraint.enum:
                        ET.SubElement(enums, "Item").text = str(item)
            if f.children:
                ch = ET.SubElement(e, "Children")
                for cf in f.children:
                    field_to_xml(ch, cf)
        fields = ET.SubElement(root, "Fields")
        for f in (self.fields or []):
            field_to_xml(fields, f)
        return ET.tostring(root, encoding="unicode")

    @staticmethod
    def from_xml(s: str) -> "MessageDefinition":
        root = ET.fromstring(s)
        label = root.get("label", "")
        title = root.get("title", "")
        version = root.get("version", "6016B")
        def xml_to_field(e: ET.Element) -> MessageField:
            name = e.get("name")
            dtype = e.get("dtype")
            units = e.findtext("Units")
            description = e.findtext("Description")
            bits_text = e.findtext("Bits")
            bits = None
            if bits_text and "-" in bits_text:
                a, b = bits_text.split("-")
                bits = [int(a), int(b)]
            constraint = None
            c = e.find("Constraint")
            if c is not None:
                enum_items = None
                enum_node = c.find("Enum")
                if enum_node is not None:
                    enum_items = [it.text or "" for it in enum_node.findall("Item")]
                constraint = FieldConstraint(
                    required=c.get("required") == "true",
                    min_value=float(c.get("min")) if c.get("min") else None,
                    max_value=float(c.get("max")) if c.get("max") else None,
                    enum=enum_items,
                    pattern=c.get("pattern"),
                )
            children = None
            ch = e.find("Children")
            if ch is not None:
                children = [xml_to_field(x) for x in ch.findall("Field")]
            return MessageField(name=name, dtype=dtype, units=units, description=description, bits=bits, children=children, constraint=constraint)
        fields_node = root.find("Fields")
        fields = []
        if fields_node is not None:
            for fe in fields_node.findall("Field"):
                fields.append(xml_to_field(fe))
        return MessageDefinition(label=label, title=title, version=version, fields=fields)


__all__ = ["MessageDefinition", "MessageField", "FieldConstraint"]


