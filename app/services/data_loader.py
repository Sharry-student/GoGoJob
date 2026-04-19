import pandas as pd

from app.extensions import db
from app.models import Job
from app.services.job_title import normalize_job_title

# This module is responsible for loading raw recruitment data from CSV files
# into the database and performing basic data cleaning.
# At the beginning, we used Gemini as a vibe-coding assistant to help us
# design a reasonable data-loading workflow, especially for handling
# messy real-world data such as salary fields, company size, and job titles.


def safe_int(value):
    try:
        if str(value) in {"未知", "nan", "None", ""}:
            return None
        return int(float(value))
    except Exception:
        return None


def looks_like_company_size(text: str) -> bool:
    value = str(text or "").strip()
    if not value or value == "未知":
        return False
    keywords = ["人", "以下", "以上", "-", "少于"]
    has_digit = any(ch.isdigit() for ch in value)
    return has_digit and any(k in value for k in keywords)


def split_company_size_industry(size_value, industry_value):
    size_text = str(size_value or "未知").strip()
    industry_text = str(industry_value or "未知").strip()
    if looks_like_company_size(size_text):
        return size_text, industry_text if industry_text else "未知"
    inferred_industry = size_text if size_text and size_text != "未知" else industry_text
    return "未知", inferred_industry if inferred_industry else "未知"


def load_jobs_from_csv(csv_path: str):
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df = df.fillna("未知")

    Job.query.delete()
    db.session.commit()

    jobs = []
    for _, row in df.iterrows():
        title = str(row.get("职位名称", "未知")).strip()
        standard_title = str(row.get("标准化职位名称", "")).strip()
        company_size, company_industry = split_company_size_industry(row.get("公司规模", "未知"), row.get("公司行业", "未知"))
        jobs.append(
            Job(
                csv_id=safe_int(row.get("主键ID")),
                category=str(row.get("岗位类别", "未知")).strip() or "未知",
                title=title,
                normalized_title=normalize_job_title(standard_title or title),
                province=str(row.get("省份", "未知")),
                city=str(row.get("城市", "未知")),
                region=str(row.get("区域", "未知")),
                company_name=str(row.get("公司名称", "未知")),
                company_size=company_size,
                company_type=str(row.get("公司类别", "未知")),
                company_industry=company_industry,
                min_salary=safe_int(row.get("最低薪资")),
                max_salary=safe_int(row.get("最高薪资")),
                avg_salary=safe_int(row.get("平均薪资")),
                education=str(row.get("学历要求", "未知")),
                experience=str(row.get("工作经验", "未知")),
                description=str(row.get("原始岗位描述", row.get("岗位描述", "未知"))),
            )
        )

    db.session.bulk_save_objects(jobs)
    db.session.commit()

    update_category_by_normalized_title()


def update_category_by_normalized_title():
    category_map = {
        "编辑": "编辑",
        "内容运营": "内容运营",
        "广告": "广告",
        "公关": "公关",
        "调研分析": "调研分析",
        "产品经理": "产品经理",
        "政府事务": "政府事务",
        "市场营销": "市场营销",
        "推广投放": "推广投放",
        "电商运营": "电商运营",
        "线下运营": "线下运营",
        "业务运营": "业务运营",
        "销售招聘": "销售招聘",
        "人力资源": "人力资源",
    }
    rows = Job.query.all()
    for row in rows:
        if not row.category or row.category in {"未知", "其他"}:
            row.category = category_map.get(row.normalized_title, "其他")
        if not looks_like_company_size(row.company_size):
            row.company_size = "未知"
    db.session.commit()
