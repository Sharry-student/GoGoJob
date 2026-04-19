from collections import Counter, defaultdict
from statistics import mean
from typing import Dict, List

import numpy as np
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import mean_absolute_error
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split

from app.models import Job

# This analytics module contains the core statistical analysis,
# salary prediction logic, and job matching algorithms.
# The initial structure and algorithm ideas were assisted by Gemini
# through a vibe-coding approach, especially for ML model selection
# and similarity-based matching logic.
#
# We reviewed each part to understand how data flows from raw job records
# to analytical insights, and adjusted the implementation to better fit
# our dataset and project requirements.


CATEGORY_GROUPS = [
    {
        "group": "内容生产&运营",
        "items": [
            {"label": "编辑", "value": "编辑"},
            {"label": "内容运营", "value": "内容运营"},
            {"label": "广告", "value": "广告"},
            {"label": "公关", "value": "公关"},
            {"label": "调研分析", "value": "调研分析"},
            {"label": "产品经理", "value": "产品经理"},
            {"label": "政府事务", "value": "政府事务"},
        ],
    },
    {
        "group": "商业增长&支持",
        "items": [
            {"label": "市场营销", "value": "市场营销"},
            {"label": "推广投放", "value": "推广投放"},
            {"label": "电商运营", "value": "电商运营"},
            {"label": "线下运营", "value": "线下运营"},
            {"label": "业务运营", "value": "业务运营"},
            {"label": "销售招聘", "value": "销售招聘"},
            {"label": "人力资源", "value": "人力资源"},
        ],
    },
]

PROVINCE_MAP_NAME = {
    "北京市": "北京",
    "天津市": "天津",
    "上海市": "上海",
    "重庆市": "重庆",
    "内蒙古自治区": "内蒙古",
    "广西壮族自治区": "广西",
    "西藏自治区": "西藏",
    "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆",
    "香港特别行政区": "香港",
    "澳门特别行政区": "澳门",
}
CHINA_VALID_PROVINCES = {
    "北京市", "天津市", "上海市", "重庆市", "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省", "江苏省", "浙江省", "安徽省",
    "福建省", "江西省", "山东省", "河南省", "湖北省", "湖南省", "广东省", "海南省", "四川省", "贵州省", "云南省", "陕西省",
    "甘肃省", "青海省", "内蒙古自治区", "广西壮族自治区", "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区", "香港特别行政区",
    "澳门特别行政区", "台湾省"
}

_salary_vec = None
_salary_model = None
_salary_mae = None
_salary_stats_exact = None
_category_jobs_cache = None
_match_vec = None
_match_matrix_by_category = None
_match_jobs_by_category = None


def base_filters(query, category=None, province=None, city=None):
    if category and category != "全部":
        query = query.filter(Job.category == category)
    if province and province != "全部":
        query = query.filter(Job.province == province)
    if city and city != "全部":
        query = query.filter(Job.city == city)
    return query


def is_company_size_value(value: str) -> bool:
    text = str(value or "")
    if not text or text == "未知":
        return False
    has_digit = any(ch.isdigit() for ch in text)
    return has_digit and ("人" in text or "-" in text or "以上" in text or "以下" in text)


def is_valid_china_row(job: Job) -> bool:
    province = str(job.province or "")
    city = str(job.city or "")
    if not province or province == "未知" or province not in CHINA_VALID_PROVINCES:
        return False
    if not city or city == "未知":
        return False
    if city in {"其他"}:
        return False
    if any(token in city for token in ["巴布亚", "沙特", "津巴布韦", "坦桑尼亚", "印度尼西亚"]):
        return False
    return True


def dashboard_summary(category=None, province=None, city=None) -> Dict:
    query = base_filters(Job.query, category=category, province=province, city=city)
    jobs = [j for j in query.all() if is_valid_china_row(j)]
    total_jobs = len(jobs)
    avg_salary = int(mean([j.avg_salary for j in jobs if j.avg_salary])) if jobs else 0
    edu_counter = Counter(j.education for j in jobs if j.education)
    exp_counter = Counter(j.experience for j in jobs if j.experience)
    company_counter = Counter(j.company_size for j in jobs if is_company_size_value(j.company_size))
    city_counter = Counter(j.city for j in jobs if j.city and j.city != "未知")
    category_counter = Counter(j.category for j in jobs if j.category and j.category != "未知")
    city_salary = defaultdict(list)
    for j in jobs:
        if j.city and j.city != "未知" and j.avg_salary:
            city_salary[j.city].append(j.avg_salary)
    top_city_salary = sorted(
        [{"name": k, "value": int(mean(v)), "count": len(v)} for k, v in city_salary.items() if len(v) >= 20],
        key=lambda x: x["value"],
        reverse=True,
    )[:10]
    top_jobs = sorted(
        [
            {
                "id": j.id,
                "title": j.title,
                "city": j.city,
                "company_name": j.company_name,
                "avg_salary": j.avg_salary or 0,
                "education": j.education,
                "experience": j.experience,
            }
            for j in jobs
        ],
        key=lambda x: x["avg_salary"],
        reverse=True,
    )[:10]
    return {
        "total_jobs": total_jobs,
        "avg_salary": avg_salary,
        "education": [{"name": k, "value": v} for k, v in edu_counter.most_common(8)],
        "experience": [{"name": k, "value": v} for k, v in exp_counter.most_common(8)],
        "company_size": [{"name": k, "value": v} for k, v in company_counter.most_common(8)],
        "top_cities": [{"name": k, "value": v} for k, v in city_counter.most_common(10)],
        "category_counts": [{"name": k, "value": v} for k, v in category_counter.most_common(14)],
        "top_city_salary": [{"name": x["name"], "value": x["value"]} for x in top_city_salary],
        "top_jobs": top_jobs,
    }


def map_salary_data(category=None, education=None, experience=None, company_size=None):
    query = Job.query
    if category and category != "全部":
        query = query.filter(Job.category == category)
    if education and education != "不限":
        query = query.filter(Job.education == education)
    if experience and experience != "不限":
        query = query.filter(Job.experience == experience)
    if company_size and company_size != "不限":
        query = query.filter(Job.company_size == company_size)
    rows = [r for r in query.all() if is_valid_china_row(r)]
    province_salary = defaultdict(list)
    for row in rows:
        if row.province and row.province != "未知" and row.avg_salary:
            province_salary[row.province].append(row.avg_salary)
    data = []
    for p, vals in province_salary.items():
        if len(vals) < 20:
            continue
        data.append({"name": p, "value": int(mean(vals))})
    data.sort(key=lambda x: x["name"])
    values = [x["value"] for x in data] if data else [0]
    return {"map_data": data, "top10": sorted(data, key=lambda x: x["value"], reverse=True)[:10], "min_value": min(values), "max_value": max(values)}


def _row_text(j: Job):
    return " ".join([j.category or "", j.province or "", j.city or "", j.education or "", j.experience or "", j.company_size or "", j.company_name or ""])


def _build_salary_stats(rows):
    stats = defaultdict(list)
    for j in rows:
        if not j.avg_salary:
            continue
        key = (j.category or "", j.province or "", j.city or "", j.education or "", j.experience or "", j.company_size or "")
        stats[key].append(int(j.avg_salary))
    return stats


def refresh_ml_cache():
    global _salary_vec, _salary_model, _salary_mae, _salary_stats_exact, _category_jobs_cache
    global _match_vec, _match_matrix_by_category, _match_jobs_by_category
    rows = Job.query.filter(Job.avg_salary.isnot(None)).all()
    _salary_stats_exact = _build_salary_stats(rows)
    _category_jobs_cache = defaultdict(list)
    for j in rows:
        _category_jobs_cache[j.category].append(j)

    texts = []
    y = []
    for j in rows:
        if not j.avg_salary:
            continue
        texts.append(_row_text(j))
        y.append(int(j.avg_salary))
    if len(texts) < 50:
        _salary_vec = None
        _salary_model = None
        _salary_mae = None
        return

    vec = TfidfVectorizer(max_features=1800)
    x = vec.fit_transform(texts)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    candidates = [
        ("rf", RandomForestRegressor(n_estimators=160, random_state=42, n_jobs=-1)),
        ("et", ExtraTreesRegressor(n_estimators=200, random_state=42, n_jobs=-1)),
        ("gbr", GradientBoostingRegressor(random_state=42)),
    ]
    best_model = None
    best_mae = None
    for _, model in candidates:
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        mae = mean_absolute_error(y_test, pred)
        if best_mae is None or mae < best_mae:
            best_mae = mae
            best_model = model
    _salary_vec = vec
    _salary_model = best_model
    _salary_mae = float(best_mae) if best_mae is not None else None

    _match_vec = DictVectorizer(sparse=True)
    match_features = []
    for j in rows:
        match_features.append(
            {
                "province": j.province or "",
                "city": j.city or "",
                "education": j.education or "",
                "experience": j.experience or "",
                "company_size": j.company_size or "",
                "category": j.category or "",
            }
        )
    full_matrix = _match_vec.fit_transform(match_features)
    _match_matrix_by_category = {}
    _match_jobs_by_category = {}
    for cat in _category_jobs_cache.keys():
        cat_rows = [j for j in rows if j.category == cat]
        if not cat_rows:
            continue
        cat_features = [
            {
                "province": j.province or "",
                "city": j.city or "",
                "education": j.education or "",
                "experience": j.experience or "",
                "company_size": j.company_size or "",
                "category": j.category or "",
            }
            for j in cat_rows
        ]
        _match_matrix_by_category[cat] = _match_vec.transform(cat_features)
        _match_jobs_by_category[cat] = cat_rows


def salary_model_metrics():
    get_salary_model()
    model_name = _salary_model.__class__.__name__ if _salary_model is not None else "None"
    sample_size = sum(len(v) for v in (_salary_stats_exact or {}).values())
    return {"model_name": model_name, "mae": round(_salary_mae, 2) if _salary_mae is not None else None, "train_sample_size": sample_size}


def get_salary_model():
    global _salary_vec, _salary_model
    if _salary_vec is None or _salary_model is None:
        refresh_ml_cache()
    return _salary_vec, _salary_model


def get_cache():
    global _salary_stats_exact, _category_jobs_cache
    if _salary_stats_exact is None or _category_jobs_cache is None:
        refresh_ml_cache()
    return _salary_stats_exact, _category_jobs_cache


def _salary_from_stats(stats):
    vals = [int(v) for v in stats]
    vals.sort()
    q10 = vals[max(0, int(len(vals) * 0.1) - 1)]
    q90 = vals[min(len(vals) - 1, int(len(vals) * 0.9))]
    avg = int(mean(vals))
    return q10, q90, avg


def predict_salary(payload: Dict):
    category = payload.get("title", "")
    province = payload.get("province", "")
    city = payload.get("city", "")
    education = payload.get("education", "")
    experience = payload.get("experience", "")
    company_size = payload.get("company_size", "")

    stats_map, _ = get_cache()
    keys = [
        (category, province, city, education, experience, company_size),
        (category, province, city, education, experience, ""),
        (category, province, city, education, "", ""),
        (category, province, city, "", "", ""),
        (category, province, "", "", "", ""),
        (category, "", "", "", "", ""),
    ]
    for key in keys:
        if key in stats_map and len(stats_map[key]) >= 8:
            low, high, avg = _salary_from_stats(stats_map[key])
            confidence = min(96, 60 + len(stats_map[key]))
            metrics = salary_model_metrics()
            return {
                "min_salary": low,
                "max_salary": high,
                "avg_salary": avg,
                "confidence": confidence,
                "sample_count": len(stats_map[key]),
                "model_name": "RuleBasedExact",
                "mae": metrics.get("mae"),
                "train_sample_size": metrics.get("train_sample_size"),
            }

    vec, model = get_salary_model()
    if not vec or not model:
        return {"min_salary": 0, "max_salary": 0, "avg_salary": 0, "confidence": 0, "sample_count": 0, "model_name": "None", "mae": None, "train_sample_size": 0}
    text = " ".join([category, province, city, education, experience, company_size])
    pred = float(model.predict(vec.transform([text]))[0])
    min_salary = int(max(pred * 0.85, 1000))
    max_salary = int(pred * 1.15)
    confidence = 78 if _salary_mae is None else max(65, min(90, int(100 - _salary_mae / 250)))
    metrics = salary_model_metrics()
    return {
        "min_salary": min_salary,
        "max_salary": max_salary,
        "avg_salary": int(pred),
        "confidence": confidence,
        "sample_count": 0,
        "model_name": metrics.get("model_name"),
        "mae": metrics.get("mae"),
        "train_sample_size": metrics.get("train_sample_size"),
    }


def match_jobs(payload: Dict):
    category = payload.get("expected_title", "")
    expected_province = payload.get("province", "")
    expected_city = payload.get("city", "")
    expected_min = int(payload.get("expected_min_salary") or 0)
    expected_max = int(payload.get("expected_max_salary") or 99999999)
    education = payload.get("education", "")
    experience = payload.get("experience", "")
    company_size = payload.get("company_size", "")

    _, category_cache = get_cache()
    global _match_vec, _match_matrix_by_category, _match_jobs_by_category
    if _match_vec is None or _match_matrix_by_category is None or _match_jobs_by_category is None:
        refresh_ml_cache()
    base_rows = category_cache.get(category, [])
    if not base_rows:
        return []
    base_matrix = _match_matrix_by_category.get(category)
    if base_matrix is None:
        return []
    query_vector = _match_vec.transform(
        [
            {
                "province": expected_province,
                "city": expected_city,
                "education": education,
                "experience": experience,
                "company_size": company_size,
                "category": category,
            }
        ]
    )
    sim_arr = cosine_similarity(query_vector, base_matrix).flatten()

    results = []
    salary_center = (expected_min + expected_max) / 2 if expected_max > 0 else 0
    for idx, j in enumerate(base_rows):
        city_score = 100 if j.city == expected_city else 55
        province_score = 100 if j.province == expected_province else 60
        loc_score = int(0.72 * city_score + 0.28 * province_score)
        salary_ok = j.avg_salary and expected_min <= j.avg_salary <= expected_max
        salary_gap = abs((j.avg_salary or 0) - salary_center)
        salary_score = 100 if salary_ok else max(28, 100 - int(salary_gap / 180))
        edu_score = 100 if j.education == education else 70
        exp_score = 100 if j.experience == experience else 70
        size_score = 100 if j.company_size == company_size else 72
        ml_score = int(sim_arr[idx] * 100)
        score = round(0.36 * loc_score + 0.24 * salary_score + 0.2 * ml_score + 0.08 * edu_score + 0.06 * exp_score + 0.06 * size_score + ((j.id % 997) / 1000), 3)
        results.append(
            {
                "id": j.id,
                "title": j.title,
                "normalized_title": j.normalized_title,
                "province": j.province,
                "city": j.city,
                "company_name": j.company_name,
                "education": j.education,
                "experience": j.experience,
                "avg_salary": j.avg_salary,
                "score": score,
                "score_breakdown": {"title_score": 100, "location_score": loc_score, "salary_score": salary_score, "skill_score": 0},
                "matched_skills": 0,
                "total_skills": 0,
            }
        )
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]


def job_detail_data(job_id: int) -> Dict:
    job = Job.query.get(job_id)
    if not job:
        return {}
    peer_jobs = Job.query.filter(Job.normalized_title == job.normalized_title).all()
    if not peer_jobs:
        peer_jobs = [job]
    salaries = [r.avg_salary for r in peer_jobs if r.avg_salary]
    avg_salary = int(mean(salaries)) if salaries else 0

    token_counter = Counter()
    for r in peer_jobs:
        text = (r.description or "").replace("，", "、")
        for token in text.split("、"):
            token = token.strip()
            if token and token != "未知":
                token_counter[token] += 1

    company_counter = Counter(r.company_size for r in peer_jobs if r.company_size)

    ordered = sorted([r.avg_salary for r in peer_jobs if r.avg_salary])
    if not ordered:
        trend_values = [0] * 6
    else:
        chunks = np.array_split(np.array(ordered), 6)
        trend_values = [int(c.mean()) if len(c) > 0 else 0 for c in chunks]
    trend_labels = ["阶段1", "阶段2", "阶段3", "阶段4", "阶段5", "阶段6"]

    return {
        "job": {
            "id": job.id,
            "title": job.title,
            "normalized_title": job.normalized_title,
            "city": job.city,
            "company_name": job.company_name,
            "education": job.education,
            "experience": job.experience,
            "avg_salary": job.avg_salary,
            "peer_count": len(peer_jobs),
            "peer_avg_salary": avg_salary,
        },
        "trend": [{"name": trend_labels[i], "value": trend_values[i]} for i in range(6)],
        "skills_top10": [{"name": k, "value": v} for k, v in token_counter.most_common(10)],
        "company_distribution": [{"name": k, "value": v} for k, v in company_counter.most_common(10)],
    }


def job_similar_jobs(job_id: int):
    job = Job.query.get(job_id)
    if not job:
        return []
    query = Job.query.filter(Job.normalized_title == job.normalized_title, Job.id != job.id)
    rows = query.limit(100).all()
    scored = []
    for r in rows:
        score = 0
        if r.province == job.province:
            score += 25
        if r.city == job.city:
            score += 30
        if r.education == job.education:
            score += 15
        if r.experience == job.experience:
            score += 15
        if r.company_size == job.company_size:
            score += 15
        scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    result = []
    for score, r in scored[:20]:
        result.append(
            {
                "id": r.id,
                "title": r.title,
                "normalized_title": r.normalized_title,
                "province": r.province,
                "city": r.city,
                "company_name": r.company_name,
                "avg_salary": r.avg_salary,
                "education": r.education,
                "experience": r.experience,
                "similarity": score,
            }
        )
    return result


def province_city_jobs_detail(province: str, category=None, education=None, experience=None, company_size=None):
    query = Job.query.filter(Job.province == province)
    if category and category != "全部":
        query = query.filter(Job.category == category)
    if education and education != "不限":
        query = query.filter(Job.education == education)
    if experience and experience != "不限":
        query = query.filter(Job.experience == experience)
    if company_size and company_size != "不限":
        query = query.filter(Job.company_size == company_size)
    rows = query.limit(3000).all()
    city_stats = defaultdict(lambda: {"count": 0, "salaries": []})
    for r in rows:
        city_key = r.city or "未知"
        city_stats[city_key]["count"] += 1
        if r.avg_salary:
            city_stats[city_key]["salaries"].append(r.avg_salary)
    city_rows = []
    for city_name, v in city_stats.items():
        avg_salary = int(mean(v["salaries"])) if v["salaries"] else 0
        city_rows.append({"city": city_name, "job_count": v["count"], "avg_salary": avg_salary})
    city_rows.sort(key=lambda x: (x["job_count"], x["avg_salary"]), reverse=True)
    top_jobs = sorted(
        [
            {
                "id": r.id,
                "title": r.title,
                "city": r.city,
                "company_name": r.company_name,
                "avg_salary": r.avg_salary or 0,
                "education": r.education,
                "experience": r.experience,
            }
            for r in rows
        ],
        key=lambda x: x["avg_salary"],
        reverse=True,
    )[:20]
    return {"province": province, "cities": city_rows[:20], "jobs": top_jobs}


def category_menu() -> List[Dict]:
    return CATEGORY_GROUPS
