# backend/mqtt_adapter/extract_tables.py
# import camelot  # 暂时注释掉，需要系统依赖
import pdfplumber
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def read_tables(pdf_path, pages):
    """返回每页的候选表格列表（DataFrame 序列）"""
    out = {}
    for p in pages:
        dfs = []
        try:
            # Camelot lattice模式
            t = camelot.read_pdf(pdf_path, pages=str(p), flavor="lattice")
            dfs += [x.df for x in t if len(x.df) > 1]
            logger.debug(f"Page {p}: Found {len(t)} lattice tables")
        except Exception as e:
            logger.debug(f"Page {p}: Lattice failed: {e}")
            
        try:
            # Camelot stream模式
            t = camelot.read_pdf(pdf_path, pages=str(p), flavor="stream")
            dfs += [x.df for x in t if len(x.df) > 1]
            logger.debug(f"Page {p}: Found {len(t)} stream tables")
        except Exception as e:
            logger.debug(f"Page {p}: Stream failed: {e}")
            
        # pdfplumber备选
        if not dfs:
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    if p <= len(pdf.pages):
                        tables = pdf.pages[p-1].extract_tables()
                        for tbl in tables:
                            if tbl and len(tbl) > 1:
                                df = pd.DataFrame(tbl)
                                if not df.empty:
                                    dfs.append(df)
                logger.debug(f"Page {p}: Found {len(tables)} pdfplumber tables")
            except Exception as e:
                logger.debug(f"Page {p}: pdfplumber failed: {e}")
        
        out[p] = dfs
        logger.info(f"Page {p}: Total {len(dfs)} tables extracted")
    
    return out

def score_table(df):
    """按列头/列数/位段可解析性打分，挑最优表"""
    if df.empty or len(df) < 2:
        return 0
    
    # 获取第一行作为表头
    headers = ""
    try:
        headers = "".join(df.iloc[0].astype(str).str.lower().tolist())
    except:
        return 0
    
    score = 0
    
    # MQTT相关关键词
    mqtt_keywords = [
        "bits", "bit", "field", "name", "description", "property", "id", "length",
        "bytes", "byte", "type", "value", "flag", "reserved", "packet", "control",
        "variable", "payload", "header", "identifier", "qos", "retain", "dup"
    ]
    
    for kw in mqtt_keywords:
        if kw in headers:
            score += 1
    
    # 额外评分规则
    if "property" in headers and "id" in headers:
        score += 2  # MQTT属性表特征
    
    if "byte" in headers and ("1" in headers or "2" in headers):
        score += 2  # 字节偏移表特征
    
    # 列数合理性
    col_count = len(df.columns)
    if 3 <= col_count <= 8:
        score += 1
    
    # 行数合理性
    row_count = len(df)
    if 3 <= row_count <= 50:
        score += 1
    
    logger.debug(f"Table score: {score}, headers: {headers[:100]}")
    return score

def pick_best_tables(per_page_tables):
    """挑选每页的最佳表格"""
    best = {}
    for p, dfs in per_page_tables.items():
        if not dfs:
            continue
        
        # 按分数排序，选择最高分的表格
        dfs_scored = [(df, score_table(df)) for df in dfs]
        dfs_scored.sort(key=lambda x: x[1], reverse=True)
        
        if dfs_scored and dfs_scored[0][1] > 0:
            best[p] = dfs_scored[0][0]
            logger.info(f"Page {p}: Selected table with score {dfs_scored[0][1]}")
        else:
            logger.warning(f"Page {p}: No suitable table found")
    
    return best

def extract_mqtt_tables(pdf_path, page_range="10-130"):
    """MQTT PDF表格提取的便捷函数"""
    # 解析页面范围
    page_list = []
    for part in page_range.split(","):
        if "-" in part:
            a, b = part.split("-")
            page_list += list(range(int(a), int(b) + 1))
        else:
            page_list.append(int(part))
    
    logger.info(f"Extracting tables from {pdf_path}, pages: {page_list[:5]}{'...' if len(page_list) > 5 else ''}")
    
    # 提取表格
    per_page = read_tables(pdf_path, page_list)
    best = pick_best_tables(per_page)
    
    logger.info(f"Successfully extracted {len(best)} tables from {len(page_list)} pages")
    return best, page_list
