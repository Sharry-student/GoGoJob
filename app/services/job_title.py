import re

# This module is used to normalize messy job titles into a smaller set
# of standardized categories. At the beginning, we used Gemini as a
# vibe-coding assistant to help think about how real-world job titles
# should be cleaned and grouped.

# Gemini helped us draft the general idea, such as removing noise words,
# using regular expressions, and mapping different titles to a unified role.


STOPWORDS = [
    "五险一金",
    "双休",
    "无责底",
    "上市公司",
    "急聘",
    "高薪",
    "底薪",
    "可居家",
    "提供住宿",
    "包吃",
    "包住",
    "六险一金",
]

TARGET_RULES = [
    (r"(人力资源|hr)", "人力资源"),
    (r"(产品经理)", "产品经理"),
    (r"(政府事务)", "政府事务"),
    (r"(调研|市场调研|分析师|数据分析)", "调研分析"),
    (r"(广告)", "广告"),
    (r"(公关)", "公关"),
    (r"(编辑)", "编辑"),
    (r"(内容运营|新媒体运营|小红书运营|抖音运营)", "内容运营"),
    (r"(电商运营)", "电商运营"),
    (r"(线下运营|地推运营)", "线下运营"),
    (r"(业务运营|运营经理|运营专员|运营主管|运营岗|运营)", "业务运营"),
    (r"(市场营销|营销|市场专员|市场经理|品牌营销)", "市场营销"),
    (r"(推广投放|投放优化|投手|信息流投放)", "推广投放"),
    (r"(销售招聘|招聘销售|销售代表|销售经理|商务经理|业务经理)", "销售招聘"),
]


def normalize_job_title(raw_title: str) -> str:
    if not raw_title:
        return "未知"
    text = str(raw_title)
    text = re.sub(r"[（(].*?[)）]", " ", text)
    text = re.sub(r"[-—_/·|]", " ", text)
    for token in STOPWORDS:
        text = text.replace(token, " ")
    text = re.sub(r"\d+[kK万Ww元/月薪\.]*", " ", text)
    text = re.sub(r"\s+", "", text)
    if not text:
        return "未知"
    for pattern, normalized in TARGET_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return normalized
    if len(text) > 12:
        return text[:12]
    return text
