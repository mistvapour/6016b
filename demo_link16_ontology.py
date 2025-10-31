#!/usr/bin/env python3
"""
Link16术语库演示
"""
from pathlib import Path
import json
from backend.ontology.link16_ontology import Link16Ontology


def main():
    print("== Link16术语库演示 ==")
    
    # 创建本体
    ontology = Link16Ontology()
    
    print(f"术语数量: {len(ontology.terms)}")
    print(f"单位数量: {len(ontology.units)}")
    print(f"枚举数量: {len(ontology.enums)}")
    
    # 测试术语查找
    print("\n[术语查找测试]")
    test_terms = ["J2", "Track ID", "Weapon Status", "Latitude", "Unknown Field"]
    for term in test_terms:
        found = ontology.find_term(term)
        if found:
            print(f"✓ '{term}' -> {found.id} ({found.category})")
        else:
            print(f"✗ '{term}' -> 未找到")
    
    # 测试单位查找
    print("\n[单位查找测试]")
    test_units = ["deg", "m", "kts", "feet", "unknown_unit"]
    for unit in test_units:
        found = ontology.find_unit(unit)
        if found:
            print(f"✓ '{unit}' -> {found.symbol} ({found.name})")
        else:
            print(f"✗ '{unit}' -> 未找到")
    
    # 测试枚举查找
    print("\n[枚举查找测试]")
    test_enums = ["weapon_status", "track_type", "threat_level", "unknown_enum"]
    for enum in test_enums:
        found = ontology.find_enum(enum)
        if found:
            print(f"✓ '{enum}' -> {found.name} ({len(found.items)} items)")
        else:
            print(f"✗ '{enum}' -> 未找到")
    
    # 测试字段链接
    print("\n[字段链接测试]")
    test_fields = [
        {"field": "track_id", "units": "m"},
        {"field": "latitude", "units": "deg"},
        {"field": "weapon_status", "enum_ref": "weapon_status"},
        {"field": "unknown_field", "units": "unknown_unit"},
    ]
    
    for field in test_fields:
        field_name = field["field"]
        term_id = ontology.link_field_to_term(field_name)
        if term_id:
            print(f"✓ '{field_name}' -> 链接到术语 '{term_id}'")
        else:
            print(f"✗ '{field_name}' -> 无法链接")
    
    # 一致性报告
    print("\n[一致性报告]")
    report = ontology.get_consistency_report(test_fields)
    print(f"总字段数: {report['total_fields']}")
    print(f"已链接字段: {report['linked_fields']}")
    print(f"未链接字段: {report['unlinked_fields']}")
    print(f"单位匹配: {report['unit_matches']}")
    print(f"枚举匹配: {report['enum_matches']}")
    
    if report["issues"]:
        print("\n问题:")
        for issue in report["issues"]:
            print(f"  - {issue}")
    
    if report["suggestions"]:
        print("\n建议:")
        for suggestion in report["suggestions"]:
            print(f"  - {suggestion}")
    
    # 导出本体
    output_dir = Path("ontology_output")
    ontology.export_ontology(output_dir)
    
    print(f"\n本体已导出到: {output_dir}")
    print("文件:")
    for file in output_dir.glob("*.json"):
        print(f"  - {file.name}")
    
    print("\n== 完成 ==")


if __name__ == "__main__":
    main()
