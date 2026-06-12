#!/usr/bin/env python3
"""Generate a tagged index for the PPT Studio template library.

The template library is intentionally heterogeneous. This script converts the
existing template inventory into a machine-readable tag index so later deck
matching can reason about:

- scenario / use case
- structure / page jobs
- visual language
- density and image-text balance
- recommended and rejected usages

The output is intentionally descriptive rather than decorative. It should help
the PPT workflow quickly match a request to the right template family.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "template-library"
INDEX_PATH = TEMPLATE_ROOT / "template-library-index.json"
OUT_JSON = TEMPLATE_ROOT / "template-library-tag-index.json"
OUT_MD = TEMPLATE_ROOT / "template-library-tag-index.md"


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def is_template_item(item: dict[str, Any]) -> bool:
    return str(item.get("extension", "")).lower() == "pptx"


def is_font_item(item: dict[str, Any]) -> bool:
    return str(item.get("extension", "")).lower() in {"otf", "ttf", "ttc"}


def color_tags(name: str) -> list[str]:
    patterns = [
        ("深蓝白", "深蓝白"),
        ("深蓝色系", "深蓝色系"),
        ("亮蓝白", "亮蓝白"),
        ("白蓝", "白蓝"),
        ("蓝白", "蓝白"),
        ("蓝色", "蓝色"),
        ("绿色", "绿色"),
        ("红色", "红色"),
        ("紫色", "紫色"),
        ("橙色", "橙色"),
        ("黄色", "黄色"),
        ("深色", "深色"),
        ("浅色", "浅色"),
        ("青蓝", "青蓝"),
        ("墨绿", "墨绿"),
    ]
    tags = [tag for needle, tag in patterns if needle in name]
    if not tags and "蓝" in name:
        tags.append("蓝系")
    return unique(tags)


def motion_tags(item: dict[str, Any]) -> list[str]:
    name = str(item.get("name", ""))
    hint = str(item.get("motion_hint", ""))
    if "动态" in name or hint == "dynamic":
        return ["动态版", "可动效"]
    if "静态" in name or hint == "static":
        return ["静态版"]
    return ["静态版", "原始文件"]


def density_tags(item: dict[str, Any], category_profile: dict[str, Any]) -> list[str]:
    slide_count = int(item.get("slide_count") or 0)
    media_count = int(item.get("media_count") or 0)
    image_media_count = int(item.get("image_media_count") or 0)
    text_sample = item.get("text_sample") or []
    text_blob = " ".join(str(t) for t in text_sample)
    text_len = len(text_blob)
    tags: list[str] = []

    if category_profile.get("density"):
        tags.append(category_profile["density"])
    elif slide_count >= 25 or media_count >= 30:
        tags.append("高密度")
    elif slide_count <= 18 and media_count <= 20:
        tags.append("中密度")
    else:
        tags.append("中高密度")

    if image_media_count >= max(1, media_count // 2):
        tags.append("图片密度高")
    if text_len >= 120:
        tags.append("文字密度高")
    if media_count >= 35:
        tags.append("图文混合密度高")

    return unique(tags)


def editable_strategy(profile: dict[str, Any]) -> list[str]:
    family = str(profile.get("family", ""))
    if family in {"科研申报", "学术答辩"}:
        return [
            "标题、章节编号、结论句、注释和引用编号必须保留为 PPT 原生文本",
            "框架图、路线图、表格和证据截图用原图或可编辑形状承载，不把正文烧进背景图",
            "长文放入备注或资料页，正文页保持 claim + evidence + boundary",
        ]
    if family in {"数据图表"}:
        return [
            "指标标题、数值标签、图例和结论句保留为可编辑文本",
            "图表优先用可编辑图形或源图原样嵌入，避免重新压缩截图",
            "每页保留一个主结论，避免把多个复杂图塞入同一区域",
        ]
    if family in {"科技汇报", "商务汇报", "工作汇报", "年度总结", "融资路演"}:
        return [
            "业务结论、模块标签、流程节点和 KPI 数字保留为 PPT 原生文本",
            "产品截图、架构图和流程图作为证据图，不作为不可编辑整页底图",
            "使用网格、分栏、流程带和数据块建立结构，不依赖装饰背景",
        ]
    if family in {"教学设计", "学生展示"}:
        return [
            "教学目标、活动步骤、任务提示和学生表达保留为可编辑文本",
            "课堂照片、作品图和 Roil 场景只承担情境或证据角色",
            "每页控制为一个教学动作，避免堆叠长段说明",
        ]
    if family in {"企业宣传", "多图展示", "庆典活动"}:
        return [
            "口号、人物/案例标题、图片说明和页码保留为可编辑文本",
            "大图承担情绪和展示，正文不要嵌入图片",
            "适合少字多图，不适合高密度论证",
        ]
    return [
        "标题、要点、标签和页码保留为 PPT 原生文本",
        "图片只承担证据、氛围或示意角色，不替代正文结构",
    ]


def fit_score_rules(profile: dict[str, Any], item: dict[str, Any]) -> dict[str, list[str]]:
    family = str(profile.get("family", "通用"))
    scenario = [str(v) for v in profile.get("scenario", [])]
    structure = [str(v) for v in profile.get("recommended_page_jobs", [])]
    visual = [str(v) for v in profile.get("visual", [])]
    avoid = [str(v) for v in profile.get("avoid", [])]
    density = str(profile.get("density", "中"))

    boost = [
        f"任务场景命中 {family} 或 {', '.join(scenario[:3])}",
        f"需要这些页面结构：{', '.join(structure[:5])}",
        f"期望视觉气质接近：{', '.join(visual[:4])}",
        f"内容密度接近模板密度：{density}",
    ]
    penalize = [
        f"任务属于这些方向时降权：{', '.join(avoid)}",
        "用户要求极强可编辑图表但模板主要由整页图片构成时降权",
        "用户需要低密度演讲稿而模板是高密度报告型时降权",
    ]

    slide_count = int(item.get("slide_count") or 0)
    media_count = int(item.get("media_count") or 0)
    if slide_count >= 28:
        boost.append("页数较多，适合拆成完整章节或长报告")
    elif slide_count <= 18:
        boost.append("页数较少，适合短汇报、样张或轻量改造")
    if media_count >= 35:
        boost.append("媒体位较多，适合截图、图表或作品图丰富的材料")

    return {"boost": unique(boost), "penalize": unique(penalize)}


def profile_card(item: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    return {
        "scenario": profile.get("scenario", []),
        "best_for": profile.get("best_for", []),
        "not_for": profile.get("avoid", []),
        "visual_style": profile.get("visual", []),
        "structure_features": profile.get("recommended_page_jobs", []),
        "density": profile.get("density", ""),
        "image_strategy": profile.get("image_strategy", []),
        "editable_strategy": editable_strategy(profile),
        "matching_keywords": unique(
            [
                *profile.get("scenario", []),
                *profile.get("structure", []),
                *profile.get("visual", []),
                *color_tags(str(item.get("name", ""))),
                *motion_tags(item),
            ]
        ),
        "fit_score_rules": fit_score_rules(profile, item),
    }


def guess_style_tags(category: str, name: str) -> dict[str, list[str]]:
    base = {
        "scenario": [],
        "structure": [],
        "visual": [],
        "image_strategy": [],
        "text_strategy": [],
        "best_for": [],
        "avoid": [],
        "recommended_page_jobs": [],
        "family": "",
        "density": "",
    }

    # Research / academic families
    if "国家自然科学" in category or "联合基金" in name:
        base.update(
            family="科研申报",
            scenario=["科研申报", "基金答辩", "研究汇报"],
            structure=["封面", "目录", "研究背景", "科学问题", "技术路线", "进度成果", "总结"],
            visual=["正式", "蓝白科研", "章节编号", "矩形证据框", "严谨"],
            image_strategy=["架构图", "流程图", "证据截图", "表格", "研究框架图"],
            text_strategy=["标题+结论句", "高可编辑正文", "编号章节", "短句解释"],
            best_for=["基金申报", "研究答辩", "课题结题", "学术汇报"],
            avoid=["儿童活动", "海报展示", "强插画风"],
            recommended_page_jobs=["封面", "目录", "研究意义", "技术路线", "结果/进度", "总结"],
            density="高",
        )
    elif "毕业答辩" in category:
        base.update(
            family="学术答辩",
            scenario=["毕业答辩", "论文汇报", "学术展示"],
            structure=["封面", "目录", "研究背景", "方法", "实验结果", "总结"],
            visual=["正式", "学术", "蓝白", "清晰编号"],
            image_strategy=["论文图", "流程图", "实验图", "结果图", "表格"],
            text_strategy=["标题+结论", "少量正文", "高可编辑"],
            best_for=["毕业论文答辩", "开题/中期/结题答辩"],
            avoid=["活动海报", "娱乐风"],
            recommended_page_jobs=["封面", "目录", "研究背景", "方法", "结果", "致谢"],
            density="高",
        )
    elif "教师说课" in category:
        base.update(
            family="教学设计",
            scenario=["教师说课", "教案展示", "课堂设计"],
            structure=["封面", "教学目标", "教学流程", "课堂活动", "评价反思"],
            visual=["教育", "清晰", "亲和", "结构明确"],
            image_strategy=["课堂图", "流程图", "板书/教具示意", "学生作品"],
            text_strategy=["教学目标短句", "流程分步", "教师话术短句"],
            best_for=["说课比赛", "教学展示", "课例分享"],
            avoid=["纯商务", "强科技风"],
            recommended_page_jobs=["封面", "教学目标", "教学流程", "课堂活动", "反思"],
            density="中高",
        )
    elif "学生风格" in category:
        base.update(
            family="学生展示",
            scenario=["学生展示", "校园汇报", "学习成果展示"],
            structure=["封面", "任务过程", "作品展示", "收获总结"],
            visual=["年轻", "明快", "活泼", "清爽"],
            image_strategy=["作品图", "课堂照片", "任务过程图"],
            text_strategy=["短标题", "短说明", "少量标签"],
            best_for=["学生汇报", "课堂展示", "校园活动"],
            avoid=["过度严肃科研", "高密度长文"],
            recommended_page_jobs=["封面", "过程", "作品", "收获", "结束"],
            density="中",
        )
    elif "工作汇报" in category:
        base.update(
            family="工作汇报",
            scenario=["工作汇报", "项目进展", "部门总结"],
            structure=["封面", "现状", "进展", "成果", "计划"],
            visual=["稳重", "商务", "清晰", "中性"],
            image_strategy=["流程图", "KPI图", "项目截图", "对比图"],
            text_strategy=["标题+要点", "结果摘要", "结论先行"],
            best_for=["周报/月报/年度汇报", "项目总结"],
            avoid=["儿童风", "活动庆典风"],
            recommended_page_jobs=["封面", "现状", "进展", "成果", "计划"],
            density="中高",
        )
    elif "年会颁奖" in category:
        base.update(
            family="庆典活动",
            scenario=["年会颁奖", "活动庆典", "表彰大会"],
            structure=["封面", "节目/奖项", "致辞", "颁奖", "合影/结束"],
            visual=["舞台感", "庆典", "高对比", "热烈"],
            image_strategy=["大图", "舞台照", "奖项列表", "人物照片"],
            text_strategy=["短口号", "奖项名称", "名单"],
            best_for=["年会", "颁奖", "活动开场"],
            avoid=["科研申报", "技术说明"],
            recommended_page_jobs=["封面", "节目单", "奖项页", "致辞页", "结束页"],
            density="中",
        )
    elif "年终总结" in category:
        base.update(
            family="年度总结",
            scenario=["年终总结", "年度复盘", "成果盘点"],
            structure=["封面", "回顾", "成果", "问题", "计划"],
            visual=["稳重", "年度感", "总结型", "清晰"],
            image_strategy=["图表", "成果图", "事件时间线"],
            text_strategy=["总结句", "要点列表", "数据块"],
            best_for=["年终述职", "年度复盘", "部门总结"],
            avoid=["活动庆典", "课堂教学风"],
            recommended_page_jobs=["封面", "回顾", "成果", "问题", "计划"],
            density="中高",
        )
    elif "扁平风格" in category:
        base.update(
            family="通用扁平",
            scenario=["通用汇报", "基础展示", "轻量介绍"],
            structure=["封面", "概览", "要点", "总结"],
            visual=["扁平", "简洁", "轻图标", "通用"],
            image_strategy=["图标", "扁平插画", "示意图"],
            text_strategy=["短句", "低复杂度标题"],
            best_for=["轻量介绍", "普通汇报"],
            avoid=["高证据科研", "高强度数据说明"],
            recommended_page_jobs=["封面", "概览", "要点", "总结"],
            density="中",
        )
    elif "商务风格" in category:
        base.update(
            family="商务汇报",
            scenario=["商务汇报", "公司介绍", "项目沟通"],
            structure=["封面", "业务", "方案", "成果", "合作"],
            visual=["稳重", "商务", "整齐", "专业"],
            image_strategy=["业务图", "流程图", "数据图", "案例图"],
            text_strategy=["标题+要点", "数据摘要"],
            best_for=["企业汇报", "业务介绍", "项目沟通"],
            avoid=["儿童活动", "强学术风"],
            recommended_page_jobs=["封面", "业务介绍", "方案", "成果", "合作"],
            density="中高",
        )
    elif "企业宣传" in category:
        base.update(
            family="企业宣传",
            scenario=["企业宣传", "品牌介绍", "公司画册"],
            structure=["封面", "公司介绍", "业务板块", "案例展示", "结束页"],
            visual=["品牌感", "大图", "宣传画册", "现代"],
            image_strategy=["品牌图", "产品图", "团队照", "案例图"],
            text_strategy=["短口号", "品牌标签", "少量说明"],
            best_for=["品牌介绍", "宣传手册", "企业展示"],
            avoid=["科研答辩", "高密度长文"],
            recommended_page_jobs=["封面", "公司介绍", "业务板块", "案例", "结束页"],
            density="中",
        )
    elif "医疗风格" in category:
        base.update(
            family="医疗汇报",
            scenario=["医疗汇报", "医院介绍", "临床/健康相关展示"],
            structure=["封面", "问题", "方案", "流程", "结果"],
            visual=["医疗蓝", "洁净", "专业", "克制"],
            image_strategy=["流程图", "示意图", "病例/设备图", "数据图"],
            text_strategy=["短结论", "专业术语短句"],
            best_for=["医疗相关汇报", "健康/临床展示"],
            avoid=["庆典", "儿童风"],
            recommended_page_jobs=["封面", "问题", "方案", "流程", "结果"],
            density="中高",
        )
    elif "数据图表" in category or "可视化图表" in category:
        base.update(
            family="数据图表",
            scenario=["数据分析", "图表汇报", "统计说明"],
            structure=["封面", "指标概览", "图表页", "对比页", "结论"],
            visual=["数据化", "清楚", "网格", "信息密度高"],
            image_strategy=["柱状图", "折线图", "矩阵图", "流程图", "图表截图"],
            text_strategy=["结论句", "图表注释", "指标标签"],
            best_for=["数据分析", "业绩汇报", "统计展示"],
            avoid=["纯情绪海报", "儿童活动风"],
            recommended_page_jobs=["封面", "指标概览", "图表页", "对比页", "结论"],
            density="高",
        )
    elif "多图排版" in category:
        base.update(
            family="多图展示",
            scenario=["图片展示", "作品集", "图像陈列"],
            structure=["封面", "多图网格", "大图展示", "结尾"],
            visual=["图片密集", "陈列型", "留白适中"],
            image_strategy=["多图拼贴", "大图", "图片对比"],
            text_strategy=["少量标题", "图片说明短句"],
            best_for=["作品集", "图片展示", "案例陈列"],
            avoid=["长文报告", "强数据说明"],
            recommended_page_jobs=["封面", "网格页", "大图页", "结尾"],
            density="高图片",
        )
    elif "科技风格" in category:
        base.update(
            family="科技汇报",
            scenario=["科技展示", "技术介绍", "AI/IT汇报"],
            structure=["封面", "系统架构", "流程", "应用", "总结"],
            visual=["科技感", "蓝黑", "模块化", "线条感"],
            image_strategy=["架构图", "UI截图", "流程图", "技术示意图"],
            text_strategy=["简短说明", "模块标签", "标题+结论"],
            best_for=["技术介绍", "AI产品", "系统说明"],
            avoid=["活动庆典", "儿童海报"],
            recommended_page_jobs=["封面", "系统架构", "流程", "应用", "总结"],
            density="中高",
        )
    elif "竞聘述职" in category:
        base.update(
            family="竞聘述职",
            scenario=["竞聘", "述职", "个人总结"],
            structure=["封面", "履历", "工作成果", "优势", "展望"],
            visual=["稳重", "个人汇报", "清晰", "正式"],
            image_strategy=["个人照片", "成果图", "数据图"],
            text_strategy=["要点式", "自我陈述", "结果摘要"],
            best_for=["竞聘汇报", "述职答辩", "晋升展示"],
            avoid=["品牌宣传", "活动庆典"],
            recommended_page_jobs=["封面", "履历", "成果", "优势", "展望"],
            density="中高",
        )
    elif "简约清新" in category:
        base.update(
            family="简约清新",
            scenario=["通用介绍", "轻量汇报", "清爽展示"],
            structure=["封面", "概览", "要点", "总结"],
            visual=["留白", "清爽", "柔和", "通用"],
            image_strategy=["简洁插画", "截图", "小图"],
            text_strategy=["短句", "轻量标题"],
            best_for=["轻量汇报", "通用介绍"],
            avoid=["高密度科研", "重数据报告"],
            recommended_page_jobs=["封面", "概览", "要点", "总结"],
            density="中",
        )
    elif "路演融资" in category:
        base.update(
            family="融资路演",
            scenario=["路演融资", "创业介绍", "投资人汇报"],
            structure=["封面", "痛点", "方案", "市场", "模型", "团队", "融资需求"],
            visual=["冲击力", "商业感", "强对比", "产品感"],
            image_strategy=["产品图", "市场图", "商业模式图", "数据图"],
            text_strategy=["一句话价值主张", "关键指标", "简洁卖点"],
            best_for=["路演", "融资提案", "创业介绍"],
            avoid=["科研申报", "教学说课"],
            recommended_page_jobs=["封面", "痛点", "方案", "市场", "商业模式", "团队", "融资需求"],
            density="中高",
        )
    else:
        base.update(
            family="通用",
            scenario=["通用"],
            structure=["封面", "概览", "正文", "总结"],
            visual=["通用", "可编辑优先"],
            image_strategy=["截图", "图表", "示意图"],
            text_strategy=["标题+要点"],
            best_for=["通用汇报"],
            avoid=["过强风格绑定"],
            recommended_page_jobs=["封面", "概览", "正文", "总结"],
            density="中",
        )

    return base


def derive_tags(item: dict[str, Any]) -> dict[str, Any]:
    name = str(item.get("name", ""))
    category = str(item.get("category", ""))
    profile = guess_style_tags(category, name)

    tags = unique(
        [
            profile["family"],
            *profile["scenario"],
            *profile["structure"],
            *profile["visual"],
            *profile["image_strategy"],
            *profile["text_strategy"],
            *color_tags(name),
            *motion_tags(item),
            *density_tags(item, profile),
        ]
    )

    quick_summary = "；".join(
        [
            f"适合：{', '.join(profile['best_for'])}",
            f"结构：{', '.join(profile['recommended_page_jobs'])}",
            f"视觉：{', '.join(profile['visual'])}",
            f"不适合：{', '.join(profile['avoid'])}",
        ]
    )

    return {
        "kind": "pptx-template",
        "path": item.get("path"),
        "name": name,
        "category": category,
        "source": item.get("source"),
        "slide_count": item.get("slide_count"),
        "media_count": item.get("media_count"),
        "image_media_count": item.get("image_media_count"),
        "motion_hint": item.get("motion_hint"),
        "tags": tags,
        "profile": profile,
        "profile_card": profile_card(item, profile),
        "quick_summary": quick_summary,
        "match_keywords": unique(
            [
                *profile["scenario"],
                *profile["structure"],
                *color_tags(name),
                *motion_tags(item),
            ]
        ),
        "confidence": "high" if profile["family"] != "通用" else "medium",
    }


def font_weight_tags(name: str) -> list[str]:
    weights = [
        "ExtraLight",
        "Light",
        "Normal",
        "Regular",
        "Medium",
        "SemiBold",
        "Bold",
        "Heavy",
    ]
    return [weight for weight in weights if weight.lower() in name.lower()]


def derive_font_asset(item: dict[str, Any]) -> dict[str, Any]:
    name = str(item.get("name", ""))
    family = "思源黑体" if "SourceHanSans" in name else "思源宋体" if "SourceHanSerif" in name else "字体资产"
    usage = (
        "正文、标签、图表注释、科技/科研报告"
        if family == "思源黑体"
        else "标题、封面副标题、学术/正式报告点缀"
        if family == "思源宋体"
        else "按模板原始字体使用"
    )
    return {
        "kind": "font-asset",
        "path": item.get("path"),
        "name": name,
        "category": item.get("category"),
        "source": item.get("source"),
        "extension": item.get("extension"),
        "family": family,
        "weights": font_weight_tags(name),
        "usage": usage,
        "tags": unique([family, *font_weight_tags(name), "中文字体", "模板配套字体"]),
    }


def build_markdown(tagged_items: list[dict[str, Any]], font_assets: list[dict[str, Any]]) -> str:
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in tagged_items:
        by_category[str(item["category"])].append(item)

    lines: list[str] = []
    lines.append("# PPT Studio Template Tag Index")
    lines.append("")
    lines.append("- Generated: " + datetime.now(timezone.utc).isoformat())
    lines.append(f"- Templates tagged: {len(tagged_items)}")
    lines.append(f"- Font assets indexed separately: {len(font_assets)}")
    lines.append("")
    lines.append("## Quick Match Rules")
    lines.append("")
    lines.append("- 先看 `family`，再看 `structure`，最后看 `visual` 和 `density`。")
    lines.append("- 科研申报 / 学术答辩优先选择 `国家自然科学`、`联合基金`、`毕业答辩` 相关模板。")
    lines.append("- 企业宣传 / 路演 / 活动类模板不要拿来做科研汇报。")
    lines.append("")

    for category in sorted(by_category.keys()):
        lines.append(f"## {category}")
        lines.append("")
        for item in by_category[category]:
            tags = " / ".join(item["tags"])
            profile = item["profile"]
            card = item["profile_card"]
            lines.append(f"- `{item['name']}`")
            lines.append(f"  - 标签：{tags}")
            lines.append(f"  - 适合：{', '.join(profile['best_for'])}")
            lines.append(f"  - 结构：{', '.join(profile['recommended_page_jobs'])}")
            lines.append(f"  - 视觉：{', '.join(profile['visual'])}")
            lines.append(f"  - 图像策略：{', '.join(card['image_strategy'])}")
            lines.append(f"  - 可编辑策略：{'；'.join(card['editable_strategy'])}")
            lines.append(f"  - 匹配关键词：{', '.join(card['matching_keywords'][:12])}")
            lines.append(f"  - 加分规则：{'；'.join(card['fit_score_rules']['boost'])}")
            lines.append(f"  - 降权规则：{'；'.join(card['fit_score_rules']['penalize'])}")
            lines.append(f"  - 不适合：{', '.join(profile['avoid'])}")
            lines.append(f"  - 说明：{item['quick_summary']}")
        lines.append("")

    if font_assets:
        lines.append("## Font Assets")
        lines.append("")
        lines.append("These are not PPT templates. They are indexed separately so template counts stay accurate.")
        lines.append("")
        for item in font_assets:
            weights = ", ".join(item["weights"]) if item["weights"] else "default"
            lines.append(f"- `{item['name']}` — {item['family']} / {weights} / {item['usage']}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate template tag index for PPT Studio.")
    parser.add_argument("--index", default=str(INDEX_PATH))
    parser.add_argument("--out-json", default=str(OUT_JSON))
    parser.add_argument("--out-md", default=str(OUT_MD))
    args = parser.parse_args(argv)

    index_path = Path(args.index)
    data = json.loads(index_path.read_text(encoding="utf-8"))
    items = data.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("template library index must contain a non-empty items array")

    template_items = [item for item in items if isinstance(item, dict) and is_template_item(item)]
    font_items = [item for item in items if isinstance(item, dict) and is_font_item(item)]
    skipped_items = [
        item
        for item in items
        if isinstance(item, dict) and not is_template_item(item) and not is_font_item(item)
    ]

    tagged_items = [derive_tags(item) for item in template_items]
    font_assets = [derive_font_asset(item) for item in font_items]

    summary = Counter()
    for item in tagged_items:
        summary[str(item["profile"]["family"])] += 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_index": str(index_path),
        "file_count": len(items),
        "template_count": len(tagged_items),
        "font_asset_count": len(font_assets),
        "skipped_count": len(skipped_items),
        "family_summary": dict(sorted(summary.items(), key=lambda kv: kv[0])),
        "templates": tagged_items,
        "font_assets": font_assets,
        "skipped_assets": [
            {
                "path": item.get("path"),
                "name": item.get("name"),
                "extension": item.get("extension"),
            }
            for item in skipped_items
        ],
    }

    out_json = Path(args.out_json)
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    out_md = Path(args.out_md)
    out_md.write_text(build_markdown(tagged_items, font_assets), encoding="utf-8")

    profile_builder = SKILL_ROOT / "scripts" / "build_template_profiles.py"
    profile_result = subprocess.run(
        [sys.executable, str(profile_builder)],
        check=True,
        cwd=str(SKILL_ROOT),
        capture_output=True,
        text=True,
    )
    profile_summary = {}
    if profile_result.stdout.strip():
        try:
            profile_summary = json.loads(profile_result.stdout.strip().splitlines()[-1])
        except json.JSONDecodeError:
            profile_summary = {"raw": profile_result.stdout.strip()}

    print(
        json.dumps(
            {
                "ok": True,
                "templates": len(tagged_items),
                "font_assets": len(font_assets),
                "skipped": len(skipped_items),
                "json": str(out_json),
                "md": str(out_md),
                "frame_index": profile_summary.get("json"),
                "profiles": profile_summary.get("profiles"),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
