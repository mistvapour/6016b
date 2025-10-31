#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def add_citedate_to_entries():
    """为缺少citedate字段的条目添加该字段"""
    
    with open('references/paper.bib', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有条目，为没有citedate字段的条目添加该字段
    # 匹配条目模式：@type{key, ... }
    entry_pattern = r'(@\w+\{[^,]+,[^@]*?)(?=@|\Z)'
    entries = re.findall(entry_pattern, content, re.DOTALL)
    
    modified_count = 0
    
    for entry in entries:
        # 检查是否已经有citedate字段
        if 'citedate' not in entry:
            # 查找year字段
            year_match = re.search(r'year\s*=\s*\{[^}]+\}', entry)
            if year_match:
                # 在year字段后添加citedate
                year_end = year_match.end()
                new_entry = (entry[:year_end] + 
                           ',\n  citedate     = {2024-09-22}' + 
                           entry[year_end:])
                content = content.replace(entry, new_entry)
                modified_count += 1
    
    # 写回文件
    with open('references/paper.bib', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Added citedate to {modified_count} entries")

if __name__ == "__main__":
    add_citedate_to_entries()
