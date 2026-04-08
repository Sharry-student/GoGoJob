import csv
import io
import re

from flask import Blueprint, Response, jsonify, render_template, request
from flask_login import login_required

from app.models import Job
from app.services.analytics import (
    category_menu,
    dashboard_summary,
    job_detail_data,
    job_similar_jobs,
    map_salary_data,
    match_jobs,
    province_city_jobs_detail,
    predict_salary,
    refresh_ml_cache,
    salary_model_metrics,
)
try:
    from pypinyin import lazy_pinyin
except Exception:
    lazy_pinyin = None


main_bp = Blueprint("main", __name__)


EDU_ORDER = ["不限", "中专", "高中", "大专", "本科", "硕士", "博士"]
EXP_ORDER = ["经验不限", "在校生", "应届生", "1年以下", "1-3年", "3-5年", "5-10年", "10年以上"]


def alpha_key(text: str):
    value = str(text or "")
    if lazy_pinyin:
        return "".join(lazy_pinyin(value))
    return value


def edu_rank(value: str):
    v = str(value or "")
    for i, token in enumerate(EDU_ORDER):
        if token in v:
            return i
    return len(EDU_ORDER)


def exp_rank(value: str):
    v = str(value or "")
    for i, token in enumerate(EXP_ORDER):
        if token in v:
            return i
    m = re.search(r"(\d+)\s*-\s*(\d+)", v)
    if m:
        return int(m.group(1)) + 2
    m2 = re.search(r"(\d+)\s*年以上", v)
    if m2:
        return int(m2.group(1)) + 5
    return 999


def size_rank(value: str):
    v = str(value or "")
    m = re.search(r"(\d+)", v)
    return int(m.group(1)) if m else 999999


@main_bp.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", menu=category_menu())


@main_bp.route("/category/<category_name>")
@login_required
def category_page(category_name):
    return render_template("category.html", menu=category_menu(), category_name=category_name)


@main_bp.route("/map")
@login_required
def map_page():
    return render_template("map.html", menu=category_menu())


@main_bp.route("/predict")
@login_required
def predict_page():
    return render_template("predict.html", menu=category_menu())


@main_bp.route("/match")
@login_required
def match_page():
    return render_template("match.html", menu=category_menu())


@main_bp.route("/job/<int:job_id>")
@login_required
def job_detail_page(job_id):
    return render_template("job_detail.html", menu=category_menu(), job_id=job_id)


@main_bp.route("/api/options")
@login_required
def options_api():
    rows = Job.query.with_entities(Job.province, Job.city).all()
    province_city_map = {}
    for province, city in rows:
        if not province or province == "未知" or not city or city == "未知":
            continue
        if province not in province_city_map:
            province_city_map[province] = set()
        province_city_map[province].add(city)
    province_city_map = {k: sorted(list(v), key=alpha_key) for k, v in province_city_map.items()}
    provinces = sorted(province_city_map.keys(), key=alpha_key)
    titles = []
    for group in category_menu():
        titles.extend([item["value"] for item in group["items"]])
    educations = sorted({r.education for r in Job.query.with_entities(Job.education).all() if r.education}, key=edu_rank)
    experiences = sorted({r.experience for r in Job.query.with_entities(Job.experience).all() if r.experience}, key=exp_rank)
    sizes = sorted({r.company_size for r in Job.query.with_entities(Job.company_size).all() if r.company_size and r.company_size != "未知"}, key=size_rank)
    categories = sorted({r.category for r in Job.query.with_entities(Job.category).all() if r.category})
    salary_values = sorted({r.avg_salary for r in Job.query.with_entities(Job.avg_salary).all() if r.avg_salary})
    salary_options = []
    for step in [3000, 5000, 8000, 10000, 12000, 15000, 20000, 30000, 50000]:
        salary_options.append(step)
    if salary_values:
        salary_options = sorted(list(set(salary_options + [int(v) for v in salary_values[:: max(1, len(salary_values) // 15)]])))
    return jsonify(
        {
            "provinces": provinces,
            "province_city_map": province_city_map,
            "titles": titles,
            "educations": educations,
            "experiences": experiences,
            "company_sizes": sizes,
            "salary_options": salary_options,
            "categories": categories,
        }
    )


@main_bp.route("/api/dashboard")
@login_required
def dashboard_api():
    payload = dashboard_summary(
        category=request.args.get("category"),
        province=request.args.get("province"),
        city=request.args.get("city"),
    )
    return jsonify(payload)


@main_bp.route("/api/map")
@login_required
def map_api():
    payload = map_salary_data(
        category=request.args.get("category"),
        education=request.args.get("education"),
        experience=request.args.get("experience"),
        company_size=request.args.get("company_size"),
    )
    return jsonify(payload)


@main_bp.route("/api/map/province-detail")
@login_required
def map_province_detail_api():
    province = request.args.get("province", "")
    if not province:
        return jsonify({"province": "", "cities": [], "jobs": []})
    payload = province_city_jobs_detail(
        province=province,
        category=request.args.get("category"),
        education=request.args.get("education"),
        experience=request.args.get("experience"),
        company_size=request.args.get("company_size"),
    )
    return jsonify(payload)


@main_bp.route("/api/ml/refresh", methods=["POST"])
@login_required
def refresh_ml_api():
    refresh_ml_cache()
    return jsonify({"ok": True})


@main_bp.route("/api/predict", methods=["POST"])
@login_required
def predict_api():
    payload = request.get_json(force=True)
    required_fields = ["title", "province", "city", "education", "experience", "company_size"]
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        return jsonify({"error": f"缺少必选条件: {','.join(missing)}"}), 400
    return jsonify(predict_salary(payload))


@main_bp.route("/api/predict/model-metrics")
@login_required
def predict_model_metrics_api():
    return jsonify(salary_model_metrics())


@main_bp.route("/api/match", methods=["POST"])
@login_required
def match_api():
    payload = request.get_json(force=True)
    required_fields = ["expected_title", "province", "city", "expected_min_salary", "expected_max_salary", "education", "experience", "company_size"]
    missing = [f for f in required_fields if payload.get(f) in [None, ""]]
    if missing:
        return jsonify({"error": f"缺少必选条件: {','.join(missing)}"}), 400
    items = match_jobs(payload)
    return jsonify({"items": items, "sample_count": len(items)})


@main_bp.route("/api/job/<int:job_id>")
@login_required
def job_detail_api(job_id):
    return jsonify(job_detail_data(job_id))


@main_bp.route("/api/job/<int:job_id>/similar")
@login_required
def job_similar_api(job_id):
    return jsonify({"items": job_similar_jobs(job_id)})


@main_bp.route("/api/job/<int:job_id>/similar/export")
@login_required
def job_similar_export(job_id):
    items = job_similar_jobs(job_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["岗位ID", "职位名称", "标准岗位", "省份", "城市", "公司名称", "平均薪资", "学历要求", "工作经验"])
    for it in items:
        writer.writerow(
            [
                it.get("id"),
                it.get("title"),
                it.get("normalized_title"),
                it.get("province"),
                it.get("city"),
                it.get("company_name"),
                it.get("avg_salary"),
                it.get("education"),
                it.get("experience"),
            ]
        )
    csv_text = output.getvalue()
    output.close()
    return Response(
        csv_text,
        mimetype="text/csv; charset=utf-8-sig",
        headers={"Content-Disposition": f"attachment; filename=job_{job_id}_similar.csv"},
    )
