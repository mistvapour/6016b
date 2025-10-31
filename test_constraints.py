#!/usr/bin/env python3
"""
回归用例：校验器测试
"""
from backend.schema.constraints import ExtendedConstraint, UnitsDict, EnumDict, ConstraintValidator


def test_basic():
    c = ExtendedConstraint(required=True, min_value=0, max_value=100)
    v = ConstraintValidator()
    ok, msg = v.validate_field(50, c)
    assert ok, msg
    ok, msg = v.validate_field(150, c)
    assert not ok and "max" in msg
    ok, msg = v.validate_field(None, c)
    assert not ok and "Required" in msg
    print("✓ 基础约束通过")


def test_dependencies():
    c = ExtendedConstraint(depends_on=["field_A"])
    v = ConstraintValidator()
    ok, msg = v.validate_field("value", c, context={})
    assert not ok and "Dependency" in msg
    ok, msg = v.validate_field("value", c, context={"field_A": 1})
    assert ok, msg
    print("✓ 依赖校验通过")


def test_units_refs():
    units_ref = UnitsDict("deg", base_si="rad", factor=0.0174532925)
    v = ConstraintValidator(units_dicts={"deg@6016B": units_ref})
    ok, msg = v.validate_field(180.0, ExtendedConstraint(min_value=0, max_value=360))
    assert ok, msg
    print("✓ 单位引用通过")


def test_enum_refs():
    enum = EnumDict(
        key="weapon_status@6016B",
        items=[{"code": "0", "label": "Safe"}, {"code": "1", "label": "Armed"}],
    )
    c = ExtendedConstraint(enum=["Safe", "Armed"], enum_ref="weapon_status@6016B")
    v = ConstraintValidator(enum_dicts={"weapon_status@6016B": enum})
    ok, msg = v.validate_field("Safe", c)
    assert ok, msg
    ok, msg = v.validate_field("Unknown", c)
    assert not ok
    print("✓ 枚举引用通过")


def main():
    print("== 约束校验器回归测试 ==")
    test_basic()
    test_dependencies()
    test_units_refs()
    test_enum_refs()
    print("== 全部通过 ==")


if __name__ == "__main__":
    main()

