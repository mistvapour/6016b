#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版PPT生成脚本
基于MIL-STD-6016的战术数据链信息标准数据库架构设计与整合应用
"""

import os
import sys

def create_html_ppt():
    """创建HTML版本的PPT"""
    
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>基于MIL-STD-6016的战术数据链信息标准数据库架构设计与整合应用</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            overflow: hidden;
        }
        
        .slide {
            width: 100vw;
            height: 100vh;
            display: none;
            padding: 60px;
            box-sizing: border-box;
            background: white;
            position: relative;
        }
        
        .slide.active {
            display: block;
        }
        
        .slide h1 {
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 30px;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 20px;
        }
        
        .slide h2 {
            color: #34495e;
            font-size: 2em;
            margin-bottom: 25px;
            text-align: center;
        }
        
        .slide h3 {
            color: #2980b9;
            font-size: 1.5em;
            margin-bottom: 15px;
        }
        
        .slide p, .slide li {
            font-size: 1.2em;
            line-height: 1.6;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .slide ul {
            margin-left: 20px;
        }
        
        .slide li {
            margin-bottom: 8px;
        }
        
        .title-slide {
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .title-slide h1 {
            color: white;
            border: none;
            font-size: 2.8em;
            margin-bottom: 40px;
        }
        
        .title-slide .subtitle {
            font-size: 1.4em;
            margin-bottom: 20px;
            opacity: 0.9;
        }
        
        .title-slide .info {
            font-size: 1.1em;
            margin-top: 40px;
            opacity: 0.8;
        }
        
        .navigation {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .nav-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .nav-btn:hover {
            background: #2980b9;
        }
        
        .slide-counter {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .highlight {
            background: #f39c12;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
        }
        
        .table-container {
            margin: 20px 0;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #3498db;
            color: white;
        }
        
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="slide-counter">
        <span id="current-slide">1</span> / <span id="total-slides">20</span>
    </div>
    
    <div class="navigation">
        <button class="nav-btn" onclick="previousSlide()">上一页</button>
        <button class="nav-btn" onclick="nextSlide()">下一页</button>
    </div>

    <!-- 第1页：标题页 -->
    <div class="slide title-slide active">
        <h1>基于MIL-STD-6016的战术数据链信息标准数据库架构设计与整合应用</h1>
        <div class="subtitle">Database Architecture Design and Integration Application of Tactical Data Link Information Standards Based on MIL-STD-6016</div>
        <div class="info">
            答辩人：[您的姓名]<br>
            指导教师：[导师姓名]<br>
            专业：计算机科学与技术<br>
            答辩时间：2025年X月X日<br>
            华东师范大学
        </div>
    </div>

    <!-- 第2页：研究背景与意义 -->
    <div class="slide">
        <h2>研究背景与意义</h2>
        <h3>研究背景</h3>
        <ul>
            <li><span class="highlight">信息化战争发展</span>：战术数据链（TDL）成为现代作战体系核心</li>
            <li><span class="highlight">Link16广泛应用</span>：基于MIL-STD-6016标准，实现跨平台信息交互</li>
            <li><span class="highlight">多链路挑战</span>：信号检测困难、天基拓展需求、多链融合挑战</li>
        </ul>
        
        <h3>研究意义</h3>
        <ul>
            <li><span class="highlight">理论价值</span>：推动不同数据链协议的统一</li>
            <li><span class="highlight">工程意义</span>：为装备间互操作提供技术基础</li>
            <li><span class="highlight">应用价值</span>：支持多链融合与仿真验证</li>
        </ul>
    </div>

    <!-- 第3页：国内外研究现状 -->
    <div class="slide">
        <h2>国内外研究现状</h2>
        <h3>国外研究</h3>
        <ul>
            <li><span class="highlight">标准化体系</span>：MIL-STD-6016、MIL-STD-3011、STANAG 5516</li>
            <li><span class="highlight">技术支撑</span>：MITRE多链融合与互操作工程</li>
            <li><span class="highlight">性能优化</span>：抗干扰建模、态势信息处理</li>
        </ul>
        
        <h3>国内研究</h3>
        <ul>
            <li><span class="highlight">信号检测</span>：Link16信号检测与识别方法</li>
            <li><span class="highlight">天基拓展</span>：天基拓展及其影响研究</li>
            <li><span class="highlight">仿真平台</span>：数据链仿真平台构建</li>
        </ul>
        
        <h3>研究空白</h3>
        <p>标准数据库设计与多链融合整合方面有待深入</p>
    </div>

    <!-- 第4页：研究内容与目标 -->
    <div class="slide">
        <h2>研究内容与目标</h2>
        <h3>主要研究内容</h3>
        <ol>
            <li><span class="highlight">标准梳理</span>：系统梳理Link16消息标准，构建标准化数据库模型</li>
            <li><span class="highlight">架构设计</span>：设计数据库架构，支持消息存储、查询与一致性校验</li>
            <li><span class="highlight">系统对接</span>：实现数据库与仿真系统的对接</li>
            <li><span class="highlight">性能评估</span>：通过实验仿真评估数据库效果</li>
        </ol>
        
        <h3>研究目标</h3>
        <ul>
            <li>实现J系列报文结构、字段及编码规则的统一管理</li>
            <li>支持跨消息字段查询以及数据一致性校验</li>
            <li>验证数据库在态势信息处理和多链融合应用中的可行性</li>
        </ul>
    </div>

    <!-- 第5页：研究方法与技术路线 -->
    <div class="slide">
        <h2>研究方法与技术路线</h2>
        <h3>研究方法</h3>
        <ol>
            <li><span class="highlight">文献调研与标准分析</span>：研读相关研究成果与标准文档</li>
            <li><span class="highlight">数据库建模与架构设计</span>：构建信息标准数据库模型</li>
            <li><span class="highlight">系统实现与整合应用</span>：开发数据库应用接口</li>
            <li><span class="highlight">实验仿真与性能验证</span>：利用仿真平台进行实验评估</li>
        </ol>
        
        <h3>技术路线</h3>
        <p style="text-align: center; font-size: 1.5em; margin-top: 30px;">
            <span class="highlight">标准分析</span> → <span class="highlight">需求分析</span> → <span class="highlight">数据库设计</span> → <span class="highlight">系统实现</span> → <span class="highlight">测试验证</span>
        </p>
    </div>

    <!-- 第6页：系统需求分析 -->
    <div class="slide">
        <h2>系统需求分析</h2>
        <h3>功能需求</h3>
        <ul>
            <li><span class="highlight">标准消息管理</span>：J系列报文的存储、查询与管理</li>
            <li><span class="highlight">字段与语义概念绑定</span>：字段与语义概念的关联</li>
            <li><span class="highlight">多链路互操作支持</span>：跨链路消息对接与映射</li>
        </ul>
        
        <h3>性能需求</h3>
        <ul>
            <li><span class="highlight">查询效率</span>：支持大规模数据的高效检索</li>
            <li><span class="highlight">并发处理</span>：支持多用户同时访问</li>
            <li><span class="highlight">数据一致性</span>：保证数据的完整性和一致性</li>
        </ul>
        
        <h3>安全需求</h3>
        <ul>
            <li><span class="highlight">权限管理</span>：基于角色的访问控制</li>
            <li><span class="highlight">数据保护</span>：敏感信息的安全存储</li>
        </ul>
    </div>

    <!-- 第7页：数据库总体设计 -->
    <div class="slide">
        <h2>数据库总体设计</h2>
        <h3>设计目标</h3>
        <ul>
            <li><span class="highlight">标准化存储</span>：遵循MIL-STD-6016和STANAG 5516标准</li>
            <li><span class="highlight">语义绑定</span>：实现字段与语义概念的绑定</li>
            <li><span class="highlight">互操作支持</span>：支持跨链路数据互操作</li>
            <li><span class="highlight">高性能检索</span>：提供高效的索引与查询机制</li>
        </ul>
        
        <h3>设计原则</h3>
        <ul>
            <li><span class="highlight">模块化</span>：分为消息、字段、概念、映射等子模块</li>
            <li><span class="highlight">分层化</span>：逻辑层、物理层与接口层分离</li>
            <li><span class="highlight">面向应用</span>：充分考虑实际使用场景</li>
        </ul>
    </div>

    <!-- 第8页：数据库架构设计 -->
    <div class="slide">
        <h2>数据库架构设计</h2>
        <h3>四层架构</h3>
        <ol>
            <li><span class="highlight">数据存储层</span>：关系数据库模式，存储核心实体</li>
            <li><span class="highlight">数据管理层</span>：提供数据解析、校验、绑定功能</li>
            <li><span class="highlight">接口服务层</span>：通过RESTful API与外部系统交互</li>
            <li><span class="highlight">应用展示层</span>：提供前端可视化和交互操作</li>
        </ol>
        
        <h3>核心实体</h3>
        <ul>
            <li><span class="highlight">MESSAGE</span>：J报文元数据，带标准版本维度</li>
            <li><span class="highlight">FIELD</span>：位段定义，约束位段不重叠</li>
            <li><span class="highlight">CONCEPT</span>：语义概念库</li>
            <li><span class="highlight">MAPPING</span>：跨链/跨版映射规则与置信度</li>
        </ul>
    </div>

    <!-- 第9页：数据表结构设计 -->
    <div class="slide">
        <h2>数据表结构设计</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>表名</th>
                        <th>主键/唯一约束</th>
                        <th>关键字段</th>
                        <th>说明</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>MESSAGE</td>
                        <td>PK(message_id)</td>
                        <td>j_num, j_series, title</td>
                        <td>J报文元数据</td>
                    </tr>
                    <tr>
                        <td>FIELD</td>
                        <td>PK(field_id)</td>
                        <td>start_bit, end_bit, unit</td>
                        <td>位段定义</td>
                    </tr>
                    <tr>
                        <td>CONCEPT</td>
                        <td>PK(concept_id)</td>
                        <td>name, definition, source</td>
                        <td>语义概念库</td>
                    </tr>
                    <tr>
                        <td>MAPPING</td>
                        <td>PK(map_id)</td>
                        <td>message_id, field_id, rule</td>
                        <td>跨链映射规则</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        <h3>设计特点</h3>
        <ul>
            <li>支持版本管理和审计机制</li>
            <li>提供高效的索引策略</li>
            <li>保证数据一致性和完整性</li>
        </ul>
    </div>

    <!-- 第10页：系统架构设计 -->
    <div class="slide">
        <h2>系统架构设计</h2>
        <h3>总体架构</h3>
        <ul>
            <li><span class="highlight">数据层</span>：MySQL数据库，存储核心数据</li>
            <li><span class="highlight">服务层</span>：FastAPI实现RESTful接口</li>
            <li><span class="highlight">应用层</span>：React前端交互模块</li>
            <li><span class="highlight">外部接口层</span>：与仿真平台、指挥系统对接</li>
        </ul>
        
        <h3>技术栈</h3>
        <ul>
            <li><span class="highlight">后端</span>：FastAPI + MySQL 8.0</li>
            <li><span class="highlight">前端</span>：React + shadcn/ui</li>
            <li><span class="highlight">部署</span>：Docker容器化部署</li>
        </ul>
    </div>

    <!-- 第11页：核心功能实现 -->
    <div class="slide">
        <h2>核心功能实现</h2>
        <h3>数据导入功能</h3>
        <ul>
            <li><span class="highlight">CSV/Excel批量导入</span>：支持大规模数据自动导入</li>
            <li><span class="highlight">数据清洗</span>：自动处理异常数据和格式转换</li>
            <li><span class="highlight">数据校验</span>：确保导入数据的完整性和一致性</li>
        </ul>
        
        <h3>查询检索功能</h3>
        <ul>
            <li><span class="highlight">多条件搜索</span>：支持关键词、J系列、模糊/精确搜索</li>
            <li><span class="highlight">跨标准比较</span>：支持不同版本规范的对比分析</li>
            <li><span class="highlight">语义绑定</span>：实现字段与概念的双向绑定</li>
        </ul>
    </div>

    <!-- 第12页：系统实现展示 -->
    <div class="slide">
        <h2>系统实现展示</h2>
        <h3>主要功能模块</h3>
        <ol>
            <li><span class="highlight">消息管理</span>：J系列报文的增删改查</li>
            <li><span class="highlight">字段管理</span>：位段信息的结构化存储</li>
            <li><span class="highlight">概念管理</span>：语义概念的定义和维护</li>
            <li><span class="highlight">映射管理</span>：跨标准映射关系的建立</li>
        </ol>
        
        <h3>用户界面</h3>
        <ul>
            <li><span class="highlight">搜索界面</span>：提供直观的搜索和筛选功能</li>
            <li><span class="highlight">结果展示</span>：表格化展示搜索结果</li>
            <li><span class="highlight">统计分析</span>：提供数据统计和可视化图表</li>
        </ul>
    </div>

    <!-- 第13页：系统测试方案 -->
    <div class="slide">
        <h2>系统测试方案</h2>
        <h3>测试目标</h3>
        <ul>
            <li><span class="highlight">数据库正确性</span>：验证数据完整性和一致性</li>
            <li><span class="highlight">接口稳定性</span>：测试API的并发性能</li>
            <li><span class="highlight">功能可用性</span>：验证用户界面的易用性</li>
            <li><span class="highlight">安全鲁棒性</span>：测试系统的安全防护能力</li>
        </ul>
        
        <h3>测试方法</h3>
        <ul>
            <li><span class="highlight">功能测试</span>：手工操作与自动化脚本</li>
            <li><span class="highlight">压力测试</span>：Apache JMeter模拟高并发</li>
            <li><span class="highlight">安全测试</span>：SQL注入、参数验证等</li>
        </ul>
    </div>

    <!-- 第14页：性能测试结果 -->
    <div class="slide">
        <h2>性能测试结果</h2>
        <h3>数据库性能</h3>
        <ul>
            <li><span class="highlight">数据规模</span>：支持50万条以上消息字段</li>
            <li><span class="highlight">查询效率</span>：平均响应延迟小于150ms</li>
            <li><span class="highlight">并发处理</span>：支持1000并发用户访问</li>
        </ul>
        
        <h3>接口性能</h3>
        <ul>
            <li><span class="highlight">搜索接口</span>：100并发下延迟<150ms</li>
            <li><span class="highlight">比较接口</span>：跨5个规范版本响应约200ms</li>
            <li><span class="highlight">成功率</span>：1000并发下保持95%成功率</li>
        </ul>
    </div>

    <!-- 第15页：功能测试结果 -->
    <div class="slide">
        <h2>功能测试结果</h2>
        <h3>数据库层面</h3>
        <ul>
            <li><span class="highlight">约束验证</span>：外键约束、唯一约束正常工作</li>
            <li><span class="highlight">数据一致性</span>：位宽一致性检查通过</li>
            <li><span class="highlight">审计功能</span>：异常记录自动记录至审计表</li>
        </ul>
        
        <h3>接口层面</h3>
        <ul>
            <li><span class="highlight">参数验证</span>：非法参数正确返回错误</li>
            <li><span class="highlight">安全防护</span>：SQL注入等攻击有效防护</li>
            <li><span class="highlight">权限控制</span>：RBAC角色分离策略有效</li>
        </ul>
        
        <h3>前端层面</h3>
        <ul>
            <li><span class="highlight">兼容性</span>：多浏览器兼容性良好</li>
            <li><span class="highlight">用户体验</span>：搜索条件正确回显</li>
            <li><span class="highlight">错误处理</span>：弱网条件下降级机制正常</li>
        </ul>
    </div>

    <!-- 第16页：系统特色与创新点 -->
    <div class="slide">
        <h2>系统特色与创新点</h2>
        <h3>主要特色</h3>
        <ol>
            <li><span class="highlight">标准化建模</span>：基于MIL-STD-6016的规范化数据模型</li>
            <li><span class="highlight">语义绑定</span>：字段与概念的双向绑定机制</li>
            <li><span class="highlight">跨链支持</span>：支持多链路互操作和映射</li>
            <li><span class="highlight">高性能</span>：优化的索引和查询策略</li>
        </ol>
        
        <h3>创新点</h3>
        <ul>
            <li><span class="highlight">统一数据模型</span>：首次系统化建模MIL-STD-6016标准</li>
            <li><span class="highlight">语义一致性</span>：通过概念绑定提升跨标准一致性</li>
            <li><span class="highlight">工程化实现</span>：完整的系统架构和接口设计</li>
        </ul>
    </div>

    <!-- 第17页：应用价值与前景 -->
    <div class="slide">
        <h2>应用价值与前景</h2>
        <h3>直接应用</h3>
        <ul>
            <li><span class="highlight">标准管理</span>：为MIL-STD-6016标准提供数字化管理平台</li>
            <li><span class="highlight">研发支持</span>：为数据链系统开发提供标准参考</li>
            <li><span class="highlight">培训教育</span>：为相关专业教学提供实践平台</li>
        </ul>
        
        <h3>扩展应用</h3>
        <ul>
            <li><span class="highlight">多链融合</span>：支持Link16、JREAP、TTNT等多链路整合</li>
            <li><span class="highlight">仿真验证</span>：为战术数据链仿真提供数据支撑</li>
            <li><span class="highlight">互操作测试</span>：为装备互操作性验证提供工具</li>
        </ul>
    </div>

    <!-- 第18页：存在的问题与不足 -->
    <div class="slide">
        <h2>存在的问题与不足</h2>
        <h3>数据规模限制</h3>
        <ul>
            <li><span class="highlight">样本有限</span>：实验数据约50万条，未覆盖全部NATO规范</li>
            <li><span class="highlight">跨链验证</span>：缺乏Link11/22、TTNT的大规模验证</li>
        </ul>
        
        <h3>功能深度</h3>
        <ul>
            <li><span class="highlight">可视化</span>：前端以表格展示为主，缺乏复杂图表分析</li>
            <li><span class="highlight">冲突检测</span>：一致性验证逻辑仍偏基础</li>
        </ul>
        
        <h3>安全运维</h3>
        <ul>
            <li><span class="highlight">加密保护</span>：未覆盖全链路加密、KMI等高级安全要求</li>
            <li><span class="highlight">运维监控</span>：缺乏完整的运维监控体系</li>
        </ul>
    </div>

    <!-- 第19页：未来研究方向 -->
    <div class="slide">
        <h2>未来研究方向</h2>
        <h3>短期目标</h3>
        <ol>
            <li><span class="highlight">数据扩展</span>：导入更多NATO标准数据</li>
            <li><span class="highlight">功能增强</span>：增加复杂查询和可视化功能</li>
            <li><span class="highlight">性能优化</span>：进一步提升查询效率和并发能力</li>
        </ol>
        
        <h3>长期目标</h3>
        <ol>
            <li><span class="highlight">多链融合</span>：支持更多战术数据链标准</li>
            <li><span class="highlight">智能分析</span>：引入AI技术进行智能分析</li>
            <li><span class="highlight">分布式部署</span>：支持大规模分布式部署</li>
        </ol>
    </div>

    <!-- 第20页：总结与致谢 -->
    <div class="slide">
        <h2>总结与致谢</h2>
        <h3>主要贡献</h3>
        <ul>
            <li><span class="highlight">理论贡献</span>：建立了MIL-STD-6016的标准化数据模型</li>
            <li><span class="highlight">技术贡献</span>：实现了高性能的数据库架构和接口设计</li>
            <li><span class="highlight">应用贡献</span>：为战术数据链互操作提供了技术支撑</li>
        </ul>
        
        <h3>致谢</h3>
        <p style="text-align: center; font-size: 1.3em; margin: 30px 0;">
            感谢导师的悉心指导！<br>
            感谢实验室同学的支持！<br>
            感谢各位专家的宝贵意见！
        </p>
        
        <h3 style="text-align: center; color: #e74c3c; margin-top: 40px;">
            请各位专家批评指正！
        </h3>
    </div>

    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        
        document.getElementById('total-slides').textContent = totalSlides;
        
        function showSlide(n) {
            slides[currentSlide].classList.remove('active');
            currentSlide = (n + totalSlides) % totalSlides;
            slides[currentSlide].classList.add('active');
            document.getElementById('current-slide').textContent = currentSlide + 1;
        }
        
        function nextSlide() {
            showSlide(currentSlide + 1);
        }
        
        function previousSlide() {
            showSlide(currentSlide - 1);
        }
        
        // 键盘导航
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                nextSlide();
            } else if (e.key === 'ArrowLeft') {
                previousSlide();
            }
        });
        
        // 鼠标点击导航
        document.addEventListener('click', function(e) {
            if (e.target.tagName !== 'BUTTON') {
                nextSlide();
            }
        });
    </script>
</body>
</html>
"""
    
    return html_content

def main():
    """主函数"""
    try:
        print("正在创建HTML版PPT...")
        html_content = create_html_ppt()
        
        # 保存HTML文件
        filename = "基于MIL-STD-6016的战术数据链信息标准数据库架构设计与整合应用_预答辩.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML版PPT创建成功！文件保存为：{filename}")
        print("PPT包含20页内容，涵盖了论文的所有核心要点")
        print("可以在浏览器中打开查看，支持键盘和鼠标导航")
        print("使用方向键或空格键翻页，点击页面也可以翻页")
        
    except Exception as e:
        print(f"创建PPT时出错：{e}")

if __name__ == "__main__":
    main()

