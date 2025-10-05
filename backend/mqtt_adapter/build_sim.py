# backend/mqtt_adapter/build_sim.py
import logging
from .normalize_bits import normalize_table_data, group_fields_by_segment, calculate_offsets

logger = logging.getLogger(__name__)

def build_spec_message(label, pages, tables_for_pages, page_texts=None):
    """
    根据已挑选的 CONNECT/PUBLISH... 页面的最佳表格，生成通用消息描述
    返回 spec_message: {label, title, transport_unit, segments:[{type, seg_idx, fields:[...]}]}
    """
    logger.info(f"Building spec message for {label}")
    
    # 收集所有相关表格的字段
    all_fields = []
    
    for page_no in pages:
        df = tables_for_pages.get(page_no)
        if df is not None and not df.empty:
            logger.debug(f"Processing table from page {page_no}")
            fields = normalize_table_data(df)
            all_fields.extend(fields)
    
    if not all_fields:
        logger.warning(f"No fields extracted for {label}")
        return None
    
    logger.info(f"Extracted {len(all_fields)} fields for {label}")
    
    # 根据MQTT结构分组字段
    segments_data = group_fields_by_segment(all_fields)
    
    # 构建段列表
    segments = []
    seg_idx = 0
    
    # MQTT报文标准结构顺序
    standard_order = ['Fixed Header', 'Variable Header', 'Properties', 'Payload']
    
    for seg_type in standard_order:
        if seg_type in segments_data and segments_data[seg_type]:
            fields = segments_data[seg_type]
            
            # 计算字段偏移量
            fields = calculate_offsets(fields)
            
            segment = {
                "type": seg_type,
                "seg_idx": seg_idx,
                "fields": fields,
                "description": f"{label} {seg_type} fields"
            }
            
            segments.append(segment)
            seg_idx += 1
            
            logger.debug(f"Added segment {seg_type} with {len(fields)} fields")
    
    # 如果没有按标准分组，创建一个通用段
    if not segments and all_fields:
        segment = {
            "type": "General",
            "seg_idx": 0,
            "fields": calculate_offsets(all_fields),
            "description": f"{label} fields"
        }
        segments.append(segment)
        logger.debug(f"Created general segment with {len(all_fields)} fields")
    
    result = {
        "label": label,
        "title": f"{label.title()} Packet",
        "transport_unit": "byte",
        "segments": segments,
        "pages": pages,
        "field_count": len(all_fields)
    }
    
    logger.info(f"Built spec message {label} with {len(segments)} segments and {len(all_fields)} total fields")
    return result

def build_mqtt_enums():
    """构建MQTT标准枚举定义"""
    return [
        {
            "key": "mqtt_qos",
            "items": [
                {"code": "0", "label": "At most once", "description": "Fire and forget"},
                {"code": "1", "label": "At least once", "description": "Acknowledged delivery"},
                {"code": "2", "label": "Exactly once", "description": "Assured delivery"}
            ]
        },
        {
            "key": "mqtt_packet_type",
            "items": [
                {"code": "1", "label": "CONNECT", "description": "Client request to connect to Server"},
                {"code": "2", "label": "CONNACK", "description": "Connect acknowledgment"},
                {"code": "3", "label": "PUBLISH", "description": "Publish message"},
                {"code": "4", "label": "PUBACK", "description": "Publish acknowledgment"},
                {"code": "5", "label": "PUBREC", "description": "Publish received"},
                {"code": "6", "label": "PUBREL", "description": "Publish release"},
                {"code": "7", "label": "PUBCOMP", "description": "Publish complete"},
                {"code": "8", "label": "SUBSCRIBE", "description": "Client subscribe request"},
                {"code": "9", "label": "SUBACK", "description": "Subscribe acknowledgment"},
                {"code": "10", "label": "UNSUBSCRIBE", "description": "Unsubscribe request"},
                {"code": "11", "label": "UNSUBACK", "description": "Unsubscribe acknowledgment"},
                {"code": "12", "label": "PINGREQ", "description": "PING request"},
                {"code": "13", "label": "PINGRESP", "description": "PING response"},
                {"code": "14", "label": "DISCONNECT", "description": "Client is disconnecting"},
                {"code": "15", "label": "AUTH", "description": "Authentication exchange"}
            ]
        },
        {
            "key": "mqtt_property_type",
            "items": [
                {"code": "1", "label": "Payload Format Indicator", "description": "Byte"},
                {"code": "2", "label": "Message Expiry Interval", "description": "Four Byte Integer"},
                {"code": "3", "label": "Content Type", "description": "UTF-8 Encoded String"},
                {"code": "8", "label": "Response Topic", "description": "UTF-8 Encoded String"},
                {"code": "9", "label": "Correlation Data", "description": "Binary Data"},
                {"code": "11", "label": "Subscription Identifier", "description": "Variable Byte Integer"},
                {"code": "17", "label": "Session Expiry Interval", "description": "Four Byte Integer"},
                {"code": "18", "label": "Assigned Client Identifier", "description": "UTF-8 Encoded String"},
                {"code": "19", "label": "Server Keep Alive", "description": "Two Byte Integer"},
                {"code": "21", "label": "Authentication Method", "description": "UTF-8 Encoded String"},
                {"code": "22", "label": "Authentication Data", "description": "Binary Data"}
            ]
        }
    ]

def build_sim(mqtt_sections, best_tables, page_texts=None):
    """
    构建完整的SIM (Semantic Intermediate Model)
    mqtt_sections: [{'label':'CONNECT','pages':[...]}]
    best_tables: {page_no: DataFrame}
    返回 SIM: {standard, edition, enums, spec_messages:[...]}
    """
    logger.info(f"Building SIM with {len(mqtt_sections)} sections and {len(best_tables)} tables")
    
    messages = []
    
    for section in mqtt_sections:
        label = section["label"]
        pages = section["pages"]
        
        # 为该章节的页面收集表格
        tables_for_pages = {p: best_tables.get(p) for p in pages}
        tables_for_pages = {k: v for k, v in tables_for_pages.items() if v is not None}
        
        logger.debug(f"Section {label}: {len(tables_for_pages)} tables found in {len(pages)} pages")
        
        if tables_for_pages:
            msg = build_spec_message(label, pages, tables_for_pages, page_texts)
            if msg:
                messages.append(msg)
                logger.info(f"Added message {label} with {msg['field_count']} fields")
        else:
            logger.warning(f"No tables found for section {label}")
    
    # 构建SIM
    sim = {
        "standard": "OASIS MQTT",
        "edition": "5.0",
        "transport_unit": "byte",
        "enums": build_mqtt_enums(),
        "spec_messages": messages,
        "metadata": {
            "sections_count": len(mqtt_sections),
            "messages_count": len(messages),
            "total_fields": sum(msg.get('field_count', 0) for msg in messages),
            "processor": "mqtt_pdf_adapter"
        }
    }
    
    logger.info(f"Built SIM with {len(messages)} messages and {sim['metadata']['total_fields']} total fields")
    return sim

def validate_sim(sim):
    """验证SIM数据的完整性"""
    issues = []
    
    # 基本结构检查
    required_keys = ['standard', 'edition', 'spec_messages']
    for key in required_keys:
        if key not in sim:
            issues.append(f"Missing required key: {key}")
    
    # 检查消息
    messages = sim.get('spec_messages', [])
    if not messages:
        issues.append("No spec_messages found")
    
    for i, msg in enumerate(messages):
        msg_issues = validate_message(msg, i)
        issues.extend(msg_issues)
    
    return issues

def validate_message(message, msg_index):
    """验证单个消息的结构"""
    issues = []
    prefix = f"Message {msg_index} ({message.get('label', 'Unknown')})"
    
    # 检查必需字段
    required_keys = ['label', 'title', 'segments']
    for key in required_keys:
        if key not in message:
            issues.append(f"{prefix}: Missing required key: {key}")
    
    # 检查段
    segments = message.get('segments', [])
    if not segments:
        issues.append(f"{prefix}: No segments found")
    
    for i, segment in enumerate(segments):
        segment_issues = validate_segment(segment, i, prefix)
        issues.extend(segment_issues)
    
    return issues

def validate_segment(segment, seg_index, msg_prefix):
    """验证单个段的结构"""
    issues = []
    prefix = f"{msg_prefix} Segment {seg_index}"
    
    # 检查必需字段
    required_keys = ['type', 'seg_idx', 'fields']
    for key in required_keys:
        if key not in segment:
            issues.append(f"{prefix}: Missing required key: {key}")
    
    # 检查字段
    fields = segment.get('fields', [])
    if not fields:
        issues.append(f"{prefix}: No fields found")
    
    for i, field in enumerate(fields):
        if not field.get('name'):
            issues.append(f"{prefix} Field {i}: Missing name")
        
        encoding = field.get('encoding')
        length = field.get('length')
        
        if encoding == 'UINT' and length is None:
            issues.append(f"{prefix} Field {field.get('name', i)}: UINT encoding requires fixed length")
    
    return issues
