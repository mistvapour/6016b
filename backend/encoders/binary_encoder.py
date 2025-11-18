#!/usr/bin/env python3
"""
二进制消息编码器
支持Protocol Buffer、TLV、ASN.1等格式的二进制编码
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import struct
from dataclasses import asdict

from backend.schema.message_definition import MessageDefinition, MessageField


class BinaryFormat(str, Enum):
    """二进制格式类型"""
    PROTOBUF = "protobuf"
    TLV = "tlv"
    ASN1 = "asn1"
    RAW = "raw"  # 原始字节对齐格式


class BinaryMessageEncoder:
    """二进制消息编码器"""
    
    def __init__(self, format_type: BinaryFormat = BinaryFormat.RAW, 
                 endianness: str = "big"):
        """
        初始化编码器
        
        Args:
            format_type: 编码格式
            endianness: 字节序（"big" 或 "little"）
        """
        self.format_type = format_type
        self.endianness = endianness
        self.byte_order = ">" if endianness == "big" else "<"
    
    def encode(self, message_def: MessageDefinition, 
               instance: Dict[str, Any],
               alignment: int = 4) -> bytes:
        """
        编码消息实例为二进制
        
        Args:
            message_def: 消息定义
            instance: 消息实例数据
            alignment: 字节对齐（默认4字节）
        
        Returns:
            二进制数据
        """
        if self.format_type == BinaryFormat.PROTOBUF:
            return self._encode_protobuf(message_def, instance)
        elif self.format_type == BinaryFormat.TLV:
            return self._encode_tlv(message_def, instance)
        elif self.format_type == BinaryFormat.ASN1:
            return self._encode_asn1(message_def, instance)
        else:  # RAW
            return self._encode_raw(message_def, instance, alignment)
    
    def _encode_raw(self, message_def: MessageDefinition, 
                    instance: Dict[str, Any],
                    alignment: int) -> bytes:
        """编码为原始字节对齐格式"""
        if not message_def.fields:
            return b''
        
        # 按位段顺序排序字段
        sorted_fields = sorted(
            [f for f in message_def.fields if f.bits],
            key=lambda f: f.bits[0] if f.bits else 0
        )
        
        # 计算总位长度
        max_bit = max([f.bits[1] for f in sorted_fields if f.bits], default=0)
        total_bits = max_bit + 1
        total_bytes = (total_bits + 7) // 8
        
        # 对齐到指定字节数
        aligned_bytes = ((total_bytes + alignment - 1) // alignment) * alignment
        
        # 创建字节数组
        data = bytearray(aligned_bytes)
        
        # 填充字段值
        for field in sorted_fields:
            if field.bits and field.name in instance:
                value = instance[field.name]
                self._pack_field_value(data, field, value)
        
        return bytes(data)
    
    def _pack_field_value(self, data: bytearray, field: MessageField, value: Any):
        """将字段值打包到位段中"""
        if not field.bits:
            return
        
        start_bit = field.bits[0]
        end_bit = field.bits[1]
        bit_length = end_bit - start_bit + 1
        
        # 根据数据类型打包值
        dtype = field.dtype.lower()
        
        if dtype in ["uint", "uint8", "uint16", "uint32"]:
            int_value = int(value)
            # 限制在位段长度内
            max_val = (1 << bit_length) - 1
            int_value = min(int_value, max_val)
            
            # 写入位段
            self._write_bits(data, start_bit, bit_length, int_value)
        
        elif dtype in ["int", "int8", "int16", "int32"]:
            int_value = int(value)
            # 处理有符号数
            if int_value < 0:
                # 转换为无符号表示
                max_val = (1 << bit_length) - 1
                int_value = (1 << bit_length) + int_value
            
            self._write_bits(data, start_bit, bit_length, int_value)
        
        elif dtype in ["float", "double", "float32", "float64"]:
            float_value = float(value)
            # 转换为整数表示（简化处理）
            if bit_length <= 32:
                int_value = int(float_value * (1 << 16))  # 定点数表示
                self._write_bits(data, start_bit, bit_length, int_value)
    
    def _write_bits(self, data: bytearray, start_bit: int, bit_length: int, value: int):
        """在位段中写入值"""
        for i in range(bit_length):
            bit_pos = start_bit + i
            byte_idx = bit_pos // 8
            bit_idx = bit_pos % 8
            
            if byte_idx < len(data):
                if (value >> i) & 1:
                    data[byte_idx] |= (1 << bit_idx)
                else:
                    data[byte_idx] &= ~(1 << bit_idx)
    
    def _encode_protobuf(self, message_def: MessageDefinition, 
                        instance: Dict[str, Any]) -> bytes:
        """编码为Protocol Buffer格式（简化实现）"""
        # Protocol Buffer需要.proto文件定义，这里实现简化版本
        # 实际应用应该使用protobuf库
        
        result = bytearray()
        field_num = 1
        
        if message_def.fields:
            for field in message_def.fields:
                if field.name in instance:
                    value = instance[field.name]
                    field_bytes = self._encode_protobuf_field(field_num, field, value)
                    result.extend(field_bytes)
                    field_num += 1
        
        return bytes(result)
    
    def _encode_protobuf_field(self, field_num: int, field: MessageField, value: Any) -> bytes:
        """编码Protocol Buffer字段"""
        # 字段标签：field_number << 3 | wire_type
        wire_type = self._get_protobuf_wire_type(field.dtype)
        tag = (field_num << 3) | wire_type
        
        result = bytearray()
        result.extend(self._varint_encode(tag))
        
        # 编码值
        if wire_type == 0:  # Varint
            int_value = int(value)
            result.extend(self._varint_encode(int_value))
        elif wire_type == 1:  # 64-bit
            float_value = float(value)
            result.extend(struct.pack(f"{self.byte_order}d", float_value))
        elif wire_type == 2:  # Length-delimited
            str_value = str(value).encode('utf-8')
            result.extend(self._varint_encode(len(str_value)))
            result.extend(str_value)
        
        return bytes(result)
    
    def _get_protobuf_wire_type(self, dtype: str) -> int:
        """获取Protocol Buffer wire type"""
        dtype_lower = dtype.lower()
        if dtype_lower in ["uint", "int", "uint8", "int8", "uint16", "int16", "uint32", "int32", "bool"]:
            return 0  # Varint
        elif dtype_lower in ["float64", "double"]:
            return 1  # 64-bit
        elif dtype_lower in ["string", "bytes"]:
            return 2  # Length-delimited
        elif dtype_lower in ["float", "float32"]:
            return 5  # 32-bit
        else:
            return 2  # 默认Length-delimited
    
    def _varint_encode(self, value: int) -> bytes:
        """Varint编码"""
        result = bytearray()
        while value > 0x7F:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    def _encode_tlv(self, message_def: MessageDefinition, 
                   instance: Dict[str, Any]) -> bytes:
        """编码为TLV（Tag-Length-Value）格式"""
        result = bytearray()
        
        if message_def.fields:
            for field in message_def.fields:
                if field.name in instance:
                    value = instance[field.name]
                    tlv_bytes = self._encode_tlv_field(field, value)
                    result.extend(tlv_bytes)
        
        return bytes(result)
    
    def _encode_tlv_field(self, field: MessageField, value: Any) -> bytes:
        """编码TLV字段"""
        result = bytearray()
        
        # Tag: 使用字段名的哈希值（简化）
        tag = hash(field.name) % 65535
        result.extend(struct.pack(f"{self.byte_order}H", tag))
        
        # Value: 根据类型编码
        value_bytes = self._encode_value_bytes(field.dtype, value)
        
        # Length
        length = len(value_bytes)
        result.extend(struct.pack(f"{self.byte_order}H", length))
        
        # Value
        result.extend(value_bytes)
        
        return bytes(result)
    
    def _encode_asn1(self, message_def: MessageDefinition, 
                     instance: Dict[str, Any]) -> bytes:
        """编码为ASN.1格式（简化实现）"""
        # ASN.1需要完整的BER/DER编码，这里实现简化版本
        result = bytearray()
        
        # SEQUENCE标签
        result.append(0x30)  # SEQUENCE
        
        # 编码所有字段
        content_bytes = bytearray()
        if message_def.fields:
            for field in message_def.fields:
                if field.name in instance:
                    value = instance[field.name]
                    field_bytes = self._encode_asn1_field(field, value)
                    content_bytes.extend(field_bytes)
        
        # 长度（简化，假设长度<127）
        result.append(len(content_bytes))
        result.extend(content_bytes)
        
        return bytes(result)
    
    def _encode_asn1_field(self, field: MessageField, value: Any) -> bytes:
        """编码ASN.1字段"""
        result = bytearray()
        
        # 根据数据类型选择标签
        tag = self._get_asn1_tag(field.dtype)
        result.append(tag)
        
        # 编码值
        value_bytes = self._encode_value_bytes(field.dtype, value)
        
        # 长度
        result.append(len(value_bytes))
        result.extend(value_bytes)
        
        return bytes(result)
    
    def _get_asn1_tag(self, dtype: str) -> int:
        """获取ASN.1标签"""
        dtype_lower = dtype.lower()
        if dtype_lower in ["int", "uint", "int8", "uint8", "int16", "uint16", "int32", "uint32"]:
            return 0x02  # INTEGER
        elif dtype_lower in ["float", "double", "float32", "float64"]:
            return 0x09  # REAL
        elif dtype_lower == "string":
            return 0x1A  # UTF8String
        elif dtype_lower == "bool":
            return 0x01  # BOOLEAN
        else:
            return 0x1A  # 默认UTF8String
    
    def _encode_value_bytes(self, dtype: str, value: Any) -> bytes:
        """将值编码为字节"""
        dtype_lower = dtype.lower()
        
        if dtype_lower in ["uint", "int", "uint8", "int8", "uint16", "int16", "uint32", "int32"]:
            int_value = int(value)
            if dtype_lower in ["uint8", "int8"]:
                return struct.pack(f"{self.byte_order}B", int_value)
            elif dtype_lower in ["uint16", "int16"]:
                return struct.pack(f"{self.byte_order}H", int_value)
            elif dtype_lower in ["uint32", "int32"]:
                return struct.pack(f"{self.byte_order}I", int_value)
            else:
                return struct.pack(f"{self.byte_order}I", int_value)
        
        elif dtype_lower in ["float", "float32"]:
            return struct.pack(f"{self.byte_order}f", float(value))
        elif dtype_lower in ["double", "float64"]:
            return struct.pack(f"{self.byte_order}d", float(value))
        elif dtype_lower == "bool":
            return struct.pack(f"{self.byte_order}B", 1 if value else 0)
        elif dtype_lower == "string":
            return str(value).encode('utf-8')
        else:
            return str(value).encode('utf-8')
    
    def decode(self, message_def: MessageDefinition, data: bytes) -> Dict[str, Any]:
        """
        解码二进制数据为消息实例（简化实现）
        
        Args:
            message_def: 消息定义
            data: 二进制数据
        
        Returns:
            消息实例字典
        """
        if self.format_type == BinaryFormat.RAW:
            return self._decode_raw(message_def, data)
        else:
            # 其他格式的解码需要更复杂的实现
            raise NotImplementedError(f"解码格式 {self.format_type} 尚未实现")
    
    def _decode_raw(self, message_def: MessageDefinition, data: bytes) -> Dict[str, Any]:
        """解码原始字节对齐格式"""
        instance = {}
        
        if not message_def.fields:
            return instance
        
        # 按位段顺序排序字段
        sorted_fields = sorted(
            [f for f in message_def.fields if f.bits],
            key=lambda f: f.bits[0] if f.bits else 0
        )
        
        # 解码字段值
        for field in sorted_fields:
            if field.bits:
                value = self._unpack_field_value(data, field)
                instance[field.name] = value
        
        return instance
    
    def _unpack_field_value(self, data: bytes, field: MessageField) -> Any:
        """从位段中解包字段值"""
        if not field.bits:
            return None
        
        start_bit = field.bits[0]
        end_bit = field.bits[1]
        bit_length = end_bit - start_bit + 1
        
        # 读取位段
        value = self._read_bits(data, start_bit, bit_length)
        
        # 根据数据类型转换
        dtype = field.dtype.lower()
        
        if dtype in ["int", "int8", "int16", "int32"]:
            # 处理有符号数
            max_val = (1 << (bit_length - 1)) - 1
            if value > max_val:
                value = value - (1 << bit_length)
            return value
        
        elif dtype in ["float", "double", "float32", "float64"]:
            # 从定点数转换（简化处理）
            return float(value) / (1 << 16)
        
        else:
            return value
    
    def _read_bits(self, data: bytes, start_bit: int, bit_length: int) -> int:
        """从位段中读取值"""
        value = 0
        for i in range(bit_length):
            bit_pos = start_bit + i
            byte_idx = bit_pos // 8
            bit_idx = bit_pos % 8
            
            if byte_idx < len(data):
                if (data[byte_idx] >> bit_idx) & 1:
                    value |= (1 << i)
        
        return value


