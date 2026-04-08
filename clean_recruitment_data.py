import re
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


RAW_DIR = Path(r"c:\Users\TANG\PycharmProjects\GoGoJob\raw_data")
OUTPUT_DIR = Path(r"c:\Users\TANG\PycharmProjects\GoGoJob\clean_data")

PROVINCE_CITY_MAP = {
    "北京市": ["北京"],
    "天津市": ["天津"],
    "上海市": ["上海"],
    "重庆市": ["重庆"],
    "河北省": ["石家庄", "唐山", "秦皇岛", "邯郸", "邢台", "保定", "张家口", "承德", "沧州", "廊坊", "衡水"],
    "山西省": ["太原", "大同", "阳泉", "长治", "晋城", "朔州", "晋中", "运城", "忻州", "临汾", "吕梁"],
    "辽宁省": ["沈阳", "大连", "鞍山", "抚顺", "本溪", "丹东", "锦州", "营口", "阜新", "辽阳", "盘锦", "铁岭", "朝阳", "葫芦岛"],
    "吉林省": ["长春", "吉林", "四平", "辽源", "通化", "白山", "松原", "白城", "延边"],
    "黑龙江省": ["哈尔滨", "齐齐哈尔", "鸡西", "鹤岗", "双鸭山", "大庆", "伊春", "佳木斯", "七台河", "牡丹江", "黑河", "绥化", "大兴安岭"],
    "江苏省": ["南京", "无锡", "徐州", "常州", "苏州", "南通", "连云港", "淮安", "盐城", "扬州", "镇江", "泰州", "宿迁"],
    "浙江省": ["杭州", "宁波", "温州", "嘉兴", "湖州", "绍兴", "金华", "衢州", "舟山", "台州", "丽水"],
    "安徽省": ["合肥", "芜湖", "蚌埠", "淮南", "马鞍山", "淮北", "铜陵", "安庆", "黄山", "滁州", "阜阳", "宿州", "六安", "亳州", "池州", "宣城"],
    "福建省": ["福州", "厦门", "莆田", "三明", "泉州", "漳州", "南平", "龙岩", "宁德"],
    "江西省": ["南昌", "景德镇", "萍乡", "九江", "新余", "鹰潭", "赣州", "吉安", "宜春", "抚州", "上饶"],
    "山东省": ["济南", "青岛", "淄博", "枣庄", "东营", "烟台", "潍坊", "济宁", "泰安", "威海", "日照", "临沂", "德州", "聊城", "滨州", "菏泽"],
    "河南省": ["郑州", "开封", "洛阳", "平顶山", "安阳", "鹤壁", "新乡", "焦作", "濮阳", "许昌", "漯河", "三门峡", "南阳", "商丘", "信阳", "周口", "驻马店", "济源"],
    "湖北省": ["武汉", "黄石", "十堰", "宜昌", "襄阳", "鄂州", "荆门", "孝感", "荆州", "黄冈", "咸宁", "随州", "恩施", "仙桃", "潜江", "天门", "神农架林区"],
    "湖南省": ["长沙", "株洲", "湘潭", "衡阳", "邵阳", "岳阳", "常德", "张家界", "益阳", "郴州", "永州", "怀化", "娄底", "湘西"],
    "广东省": ["广州", "深圳", "珠海", "汕头", "佛山", "韶关", "湛江", "肇庆", "江门", "茂名", "惠州", "梅州", "汕尾", "河源", "阳江", "清远", "东莞", "中山", "潮州", "揭阳", "云浮"],
    "海南省": ["海口", "三亚", "三沙", "儋州", "琼海", "文昌", "万宁", "东方", "五指山", "澄迈", "临高", "定安", "屯昌", "昌江", "乐东", "陵水", "保亭", "琼中", "白沙"],
    "四川省": ["成都", "自贡", "攀枝花", "泸州", "德阳", "绵阳", "广元", "遂宁", "内江", "乐山", "南充", "眉山", "宜宾", "广安", "达州", "雅安", "巴中", "资阳", "阿坝", "甘孜", "凉山"],
    "贵州省": ["贵阳", "六盘水", "遵义", "安顺", "毕节", "铜仁", "黔西南", "黔东南", "黔南"],
    "云南省": ["昆明", "曲靖", "玉溪", "保山", "昭通", "丽江", "普洱", "临沧", "楚雄", "红河", "文山", "西双版纳", "大理", "德宏", "怒江", "迪庆"],
    "陕西省": ["西安", "铜川", "宝鸡", "咸阳", "渭南", "延安", "汉中", "榆林", "安康", "商洛"],
    "甘肃省": ["兰州", "嘉峪关", "金昌", "白银", "天水", "武威", "张掖", "平凉", "酒泉", "庆阳", "定西", "陇南", "临夏", "甘南"],
    "青海省": ["西宁", "海东", "海北", "黄南", "海南", "果洛", "玉树", "海西"],
    "内蒙古自治区": ["呼和浩特", "包头", "乌海", "赤峰", "通辽", "鄂尔多斯", "呼伦贝尔", "巴彦淖尔", "乌兰察布", "兴安盟", "锡林郭勒盟", "阿拉善盟"],
    "广西壮族自治区": ["南宁", "柳州", "桂林", "梧州", "北海", "防城港", "钦州", "贵港", "玉林", "百色", "贺州", "河池", "来宾", "崇左"],
    "西藏自治区": ["拉萨", "日喀则", "昌都", "林芝", "山南", "那曲", "阿里"],
    "宁夏回族自治区": ["银川", "石嘴山", "吴忠", "固原", "中卫"],
    "新疆维吾尔自治区": ["乌鲁木齐", "克拉玛依", "吐鲁番", "哈密", "昌吉", "博尔塔拉", "巴音郭楞", "阿克苏", "克孜勒苏", "喀什", "和田", "伊犁", "塔城", "阿勒泰", "石河子", "阿拉尔", "图木舒克", "五家渠", "北屯", "铁门关", "双河", "可克达拉", "昆玉", "胡杨河", "新星"],
    "香港特别行政区": ["香港"],
    "澳门特别行政区": ["澳门"],
    "台湾省": ["台北", "高雄", "台中", "台南", "新北", "桃园", "新竹", "基隆", "嘉义"],
}

DIRECT_CITIES = {
    "北京": "北京市",
    "天津": "天津市",
    "上海": "上海市",
    "重庆": "重庆市",
}

WELFARE_KEYWORDS = [
    "五险一金",
    "六险一金",
    "双休",
    "带薪年假",
    "包吃",
    "包住",
    "免费住宿",
    "提供住宿",
    "餐补",
    "交通补贴",
    "话补",
    "年终奖金",
    "绩效奖金",
    "节日福利",
    "定期体检",
    "员工旅游",
    "住房补贴",
    "弹性工作",
]

INVALID_JOB_NAME_PATTERNS = [
    r"[（(【\[].*?(高薪|急招|热招|诚聘|扩招|福利|推荐|应届|校招|底薪|月薪|年薪|综合薪资|K|k|W|w).*?[)）】\]]",
    r"(底薪|月薪|年薪|综合薪资|月入|综合收入)\s*\d+(\.\d+)?[kK千wW万]?",
    r"\d+(\.\d+)?\s*[-~至]\s*\d+(\.\d+)?\s*[kK千wW万]?",
    r"\d+(\.\d+)?\s*[kK千wW万]\s*(起|以上|以下)?",
    r"^[【\[(（].*?[】\])）]\s*[：:]",
    r"^.*?(高薪招聘|急招|诚聘|寻找|招募|扩招)\s*[：:]",
    r"(高薪|急招|热招|诚聘|扩招|推荐|福利好|小白可入|零基础|无经验可投)",
]

JOB_DESC_CATEGORY = {
    "岗位福利": WELFARE_KEYWORDS,
    "岗位技能要求": [
        "要求",
        "具备",
        "需要",
        "熟悉",
        "掌握",
        "了解",
        "精通",
        "经验",
        "学历",
        "证书",
        "能力",
        "技能",
        "软件",
        "工具",
        "本科",
        "大专",
        "硕士",
        "博士",
    ],
    "工作内容": [
        "负责",
        "执行",
        "开展",
        "制定",
        "维护",
        "拓展",
        "跟进",
        "完成",
        "组织",
        "协调",
        "调研",
        "分析",
        "策划",
        "推广",
        "销售",
        "运营",
        "管理",
        "对接",
    ],
}


def city_key(name: str) -> str:
    base = str(name).replace("\u3000", "").replace("\xa0", "")
    base = re.sub(r"\s+", "", base)
    if base.lower() == "nan":
        return ""
    if not base:
        return ""
    base = re.sub(r"(特别行政区|自治区|自治州|地区|盟|市)$", "", base)
    return base


def build_city_to_province():
    mapping = {}
    for province, cities in PROVINCE_CITY_MAP.items():
        for city in cities:
            key = city_key(city)
            if key:
                mapping[key] = province
    return mapping


CITY_TO_PROVINCE = build_city_to_province()


def normalize_city_display(city: str) -> str:
    value = normalize_text(city)
    if not value:
        return ""
    key = city_key(value)
    if key in DIRECT_CITIES:
        return DIRECT_CITIES[key]
    if re.search(r"(市|自治州|地区|盟|林区)$", value):
        return value
    if key in CITY_TO_PROVINCE:
        return f"{value}市"
    return value


def infer_province_city_region(city: str, district: str, area: str) -> Tuple[str, str, str]:
    city_clean = normalize_text(city)
    district_clean = normalize_text(district)
    area_clean = normalize_text(area)
    if not city_clean:
        return "", "", district_clean or area_clean
    key = city_key(city_clean)
    if key in DIRECT_CITIES:
        municipality = DIRECT_CITIES[key]
        region = district_clean or area_clean
        return municipality, municipality, region
    province = CITY_TO_PROVINCE.get(key, "")
    city_name = normalize_city_display(city_clean)
    region = district_clean or area_clean
    return province, city_name, region


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\u3000", " ").replace("\xa0", " ")
    text = re.sub(r"\s+", "", text)
    if text.lower() == "nan":
        return ""
    return text


def normalize_free_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\u3000", " ").replace("\xa0", " ")
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text.lower() == "nan":
        return ""
    return text


def normalize_list_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\u3000", " ").replace("\xa0", " ")
    parts = re.split(r"[\r\n]+", text)
    cleaned = []
    seen = set()
    for part in parts:
        token = re.sub(r"\s+", "", part)
        if not token or token.lower() == "nan":
            continue
        if token not in seen:
            seen.add(token)
            cleaned.append(token)
    return "、".join(cleaned)


def normalize_column_name(col: str) -> str:
    return normalize_text(col)


def unit_factor(unit: str) -> float:
    if unit == "万":
        return 10000.0
    if unit == "千":
        return 1000.0
    return 1.0


def parse_salary(raw_salary: str) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    text = normalize_text(raw_salary)
    if not text or "面议" in text:
        return None, None, None

    monthly_period = 12
    monthly_period_match = re.search(r"[·\.]?(\d{1,2})薪", text)
    if monthly_period_match:
        monthly_period = int(monthly_period_match.group(1))

    day_pattern = re.match(r"^(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?元/(?:天|日)$", text)
    if day_pattern:
        low = float(day_pattern.group(1))
        high = float(day_pattern.group(2)) if day_pattern.group(2) else low
        low_month = low * 22
        high_month = high * 22
        avg_month = (low_month + high_month) / 2
        return round(low_month, 2), round(high_month, 2), round(avg_month, 2)

    hour_pattern = re.match(r"^(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?元/时$", text)
    if hour_pattern:
        low = float(hour_pattern.group(1))
        high = float(hour_pattern.group(2)) if hour_pattern.group(2) else low
        low_month = low * 8 * 22
        high_month = high * 8 * 22
        avg_month = (low_month + high_month) / 2
        return round(low_month, 2), round(high_month, 2), round(avg_month, 2)

    week_pattern = re.match(r"^(\d+(?:\.\d+)?)(?:-(\d+(?:\.\d+)?))?元/周$", text)
    if week_pattern:
        low = float(week_pattern.group(1))
        high = float(week_pattern.group(2)) if week_pattern.group(2) else low
        low_month = low * 4.33
        high_month = high * 4.33
        avg_month = (low_month + high_month) / 2
        return round(low_month, 2), round(high_month, 2), round(avg_month, 2)

    interval_pattern = re.match(r"^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)(万|千|元)(?:[·\.]?(\d{1,2})薪)?$", text)
    if interval_pattern:
        low = float(interval_pattern.group(1)) * unit_factor(interval_pattern.group(3))
        high = float(interval_pattern.group(2)) * unit_factor(interval_pattern.group(3))
        period = int(interval_pattern.group(4)) if interval_pattern.group(4) else monthly_period
        low_month = low * period / 12
        high_month = high * period / 12
        avg_month = ((low + high) / 2) * period / 12
        return round(low_month, 2), round(high_month, 2), round(avg_month, 2)

    fixed_pattern = re.match(r"^(\d+(?:\.\d+)?)(万|千|元)(?:[·\.]?(\d{1,2})薪)?$", text)
    if fixed_pattern:
        salary = float(fixed_pattern.group(1)) * unit_factor(fixed_pattern.group(2))
        period = int(fixed_pattern.group(3)) if fixed_pattern.group(3) else monthly_period
        month_salary = salary * period / 12
        month_salary = round(month_salary, 2)
        return month_salary, month_salary, month_salary

    bound_pattern = re.match(r"^(\d+(?:\.\d+)?)(万|千|元)(?:以上|以下)$", text)
    if bound_pattern:
        salary = float(bound_pattern.group(1)) * unit_factor(bound_pattern.group(2))
        salary = round(salary, 2)
        return salary, salary, salary

    return None, None, None


def parse_company_profile(value) -> Tuple[str, str, str]:
    text = normalize_free_text(value)
    if not text:
        return "", "", ""
    parts = re.split(r"[\r\n]+", str(value))
    cleaned = []
    for part in parts:
        token = normalize_text(part)
        if token:
            cleaned.append(token)
    if not cleaned:
        fallback = [item for item in re.split(r"\s+", text) if item]
        cleaned = [normalize_text(item) for item in fallback if normalize_text(item)]
    if not cleaned:
        return "", "", ""
    company_type = cleaned[0] if len(cleaned) >= 1 else ""
    company_size = cleaned[1] if len(cleaned) >= 2 else ""
    company_industry = "、".join(cleaned[2:]) if len(cleaned) >= 3 else ""
    return company_type, company_size, company_industry


def normalize_location(value) -> Tuple[str, str, str, str]:
    text = normalize_text(value)
    if not text:
        return "", "", "", ""
    text = re.sub(r"[，,;/\\|]+", "·", text)
    text = re.sub(r"[•・]+", "·", text)
    text = re.sub(r"·{2,}", "·", text).strip("·")
    parts = [p for p in text.split("·") if p]
    if not parts:
        return "", "", "", ""
    city = parts[0] if len(parts) >= 1 else ""
    district = parts[1] if len(parts) >= 2 else ""
    area = parts[2] if len(parts) >= 3 else ""
    normalized = "·".join(parts)
    return normalized, city, district, area


def is_company_size_text(text: str) -> bool:
    value = normalize_text(text)
    if not value:
        return False
    has_digit = any(ch.isdigit() for ch in value)
    return has_digit and ("人" in value or "-" in value or "以上" in value or "以下" in value)


def normalize_city_suffix(city: str) -> str:
    value = normalize_text(city)
    if not value or value == "未知":
        return value
    if re.search(r"(市|自治州|州|地区|盟|林区)$", value):
        return value
    key = city_key(value)
    if key in DIRECT_CITIES:
        return DIRECT_CITIES[key]
    if key in CITY_TO_PROVINCE:
        return f"{value}市"
    return value


def extract_welfare_from_title(raw_title: str) -> str:
    title = normalize_free_text(raw_title)
    if not title:
        return "未知"
    hits = []
    for kw in WELFARE_KEYWORDS:
        if kw in title and kw not in hits:
            hits.append(kw)
    return "、".join(hits) if hits else "未知"


def clean_standard_job_name(raw_title: str) -> str:
    title = normalize_free_text(raw_title)
    if not title:
        return "未知"
    cleaned = title
    for pattern in INVALID_JOB_NAME_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[!！?？#￥$%^&*<>《》/\\|]+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return title
    return cleaned


def split_job_description(raw_desc: str) -> Tuple[str, str, str]:
    text = normalize_free_text(raw_desc)
    if not text or text == "未知":
        return "未知", "未知", "未知"
    parts = [p.strip() for p in re.split(r"[。；;，,\n\r]+", text) if p.strip()]
    welfare_parts, skill_parts, content_parts = [], [], []
    for sent in parts:
        if any(k in sent for k in JOB_DESC_CATEGORY["岗位福利"]):
            welfare_parts.append(sent)
        elif any(k in sent for k in JOB_DESC_CATEGORY["岗位技能要求"]):
            skill_parts.append(sent)
        elif any(k in sent for k in JOB_DESC_CATEGORY["工作内容"]):
            content_parts.append(sent)
    welfare = "；".join(dict.fromkeys(welfare_parts)) if welfare_parts else "未知"
    skills = "；".join(dict.fromkeys(skill_parts)) if skill_parts else "未知"
    content = "；".join(dict.fromkeys(content_parts)) if content_parts else "未知"
    return content, skills, welfare


def first_existing_column(df: pd.DataFrame, candidates) -> str:
    for col in candidates:
        if col in df.columns:
            return col
    return ""


def clean_single_file(file_path: Path) -> pd.DataFrame:
    last_error = None
    df = None
    for encoding in ("utf-8-sig", "gbk", "utf-8"):
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            break
        except Exception as exc:
            last_error = exc
    if df is None:
        raise RuntimeError(f"{file_path.name} 读取失败: {last_error}")

    df.columns = [normalize_column_name(col) for col in df.columns]

    salary_col = first_existing_column(df, ["薪水"])
    job_col = first_existing_column(df, ["信息", "标题"])
    company_col = first_existing_column(df, ["公司3", "公司"])
    if "信息" in df.columns:
        company_col = first_existing_column(df, ["标题", "公司3", "公司"])
        job_col = "信息"

    keyword_col = first_existing_column(df, ["关键词"])
    tag_col = first_existing_column(df, ["标签"])
    exp_col = first_existing_column(df, ["其它"])
    edu_col = first_existing_column(df, ["其它1"])
    location_col = first_existing_column(df, ["其它2"])
    profile_col = first_existing_column(df, ["关键词3", "关键词4"])

    records = []
    for _, row in df.iterrows():
        company_name = normalize_free_text(row.get(company_col, "")) if company_col else ""
        job_name = normalize_free_text(row.get(job_col, "")) if job_col else ""
        salary_raw = normalize_text(row.get(salary_col, "")) if salary_col else ""
        salary_min, salary_max, salary_avg = parse_salary(salary_raw)

        location_raw = normalize_text(row.get(location_col, "")) if location_col else ""
        location_norm, city, district, area = normalize_location(location_raw)
        company_type, company_size, company_industry = parse_company_profile(row.get(profile_col, "")) if profile_col else ("", "", "")

        record = {
            "数据来源文件": file_path.name,
            "公司名称": company_name,
            "岗位名称": job_name,
            "原始薪资": salary_raw,
            "最低薪资元每月": salary_min,
            "最高薪资元每月": salary_max,
            "平均薪资元每月": salary_avg,
            "关键词": normalize_list_text(row.get(keyword_col, "")) if keyword_col else "",
            "标签": normalize_free_text(row.get(tag_col, "")) if tag_col else "",
            "经验要求": normalize_free_text(row.get(exp_col, "")) if exp_col else "",
            "学历要求": normalize_free_text(row.get(edu_col, "")) if edu_col else "",
            "原始工作地点": location_raw,
            "标准工作地点": location_norm,
            "城市": city,
            "区县": district,
            "商圈乡镇": area,
            "公司性质": company_type,
            "公司规模": company_size,
            "公司行业": company_industry,
        }
        records.append(record)

    cleaned_df = pd.DataFrame(records)

    cleaned_df.drop_duplicates(
        subset=["公司名称", "岗位名称", "标准工作地点", "原始薪资"],
        keep="first",
        inplace=True,
    )

    cleaned_df["最低薪资元每月"] = cleaned_df["最低薪资元每月"].map(lambda x: round(x, 2) if pd.notna(x) else None)
    cleaned_df["最高薪资元每月"] = cleaned_df["最高薪资元每月"].map(lambda x: round(x, 2) if pd.notna(x) else None)
    cleaned_df["平均薪资元每月"] = cleaned_df["平均薪资元每月"].map(lambda x: round(x, 2) if pd.notna(x) else None)

    fill_unknown_cols = [
        "公司名称",
        "岗位名称",
        "关键词",
        "标签",
        "经验要求",
        "学历要求",
        "原始工作地点",
        "标准工作地点",
        "城市",
        "区县",
        "商圈乡镇",
        "公司性质",
        "公司规模",
        "公司行业",
    ]
    for col in fill_unknown_cols:
        cleaned_df[col] = cleaned_df[col].replace("", "未知")
        cleaned_df[col] = cleaned_df[col].fillna("未知")

    for col in ["最低薪资元每月", "最高薪资元每月", "平均薪资元每月"]:
        cleaned_df[col] = cleaned_df[col].where(cleaned_df[col].notna(), "未知")

    return cleaned_df


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_frames = []
    for file_path in sorted(RAW_DIR.glob("*.csv")):
        cleaned = clean_single_file(file_path)
        output_file = OUTPUT_DIR / f"{file_path.stem}_cleaned.csv"
        cleaned.to_csv(output_file, index=False, encoding="utf-8-sig")
        all_frames.append(cleaned)

    if all_frames:
        merged = pd.concat(all_frames, ignore_index=True)
        merged.drop_duplicates(
            subset=["公司名称", "岗位名称", "标准工作地点", "原始薪资"],
            keep="first",
            inplace=True,
        )

        geo_values = merged.apply(lambda r: infer_province_city_region(r.get("城市", ""), r.get("区县", ""), r.get("商圈乡镇", "")), axis=1)
        merged[["省份", "城市", "区域"]] = pd.DataFrame(geo_values.tolist(), index=merged.index)
        merged["省份"] = merged["省份"].map(lambda x: normalize_text(x).replace(" ", ""))
        merged["城市"] = merged["城市"].map(normalize_city_suffix)
        swap_mask = (~merged["公司规模"].map(is_company_size_text)) & (merged["公司性质"].map(is_company_size_text))
        if swap_mask.any():
            tmp = merged.loc[swap_mask, "公司规模"].copy()
            merged.loc[swap_mask, "公司规模"] = merged.loc[swap_mask, "公司性质"]
            merged.loc[swap_mask, "公司性质"] = tmp
        merged.loc[~merged["公司规模"].map(is_company_size_text), "公司规模"] = "未知"
        merged["省份"] = merged["省份"].replace("", "未知").fillna("未知")
        merged["城市"] = merged["城市"].replace("", "未知").fillna("未知")
        merged["区域"] = merged["区域"].replace("", "未知").fillna("未知")
        before_drop = len(merged)
        merged = merged[~((merged["省份"] == "未知") & (merged["城市"] == "未知"))].copy()
        removed_all_unknown_geo_rows = before_drop - len(merged)
        merged.loc[merged["省份"] == "未知", "省份"] = "海外"
        if "岗位类别" in merged.columns:
            merged = merged.drop(columns=["岗位类别"])
        merged["岗位类别"] = merged["数据来源文件"].map(lambda x: normalize_text(x).replace(".csv", ""))
        merged["原始岗位描述"] = merged["关键词"]
        merged["岗位描述"] = merged["原始岗位描述"]
        merged["职位名称"] = merged["岗位名称"]
        merged["标准化职位名称"] = merged["职位名称"].map(clean_standard_job_name)
        merged["福利待遇"] = merged["职位名称"].map(extract_welfare_from_title)
        desc_split = merged["原始岗位描述"].map(split_job_description)
        merged[["工作内容", "岗位技能要求", "岗位福利"]] = pd.DataFrame(desc_split.tolist(), index=merged.index)
        merged["公司类别"] = merged["公司性质"]
        merged["工作经验"] = merged["经验要求"]

        for source_col, target_col in [
            ("最低薪资元每月", "最低薪资"),
            ("最高薪资元每月", "最高薪资"),
            ("平均薪资元每月", "平均薪资"),
        ]:
            numeric_salary = pd.to_numeric(merged[source_col], errors="coerce")
            merged[target_col] = numeric_salary.round(0).astype("Int64").astype(str)
            merged.loc[numeric_salary.isna(), target_col] = "未知"

        final_columns = [
            "主键ID",
            "岗位类别",
            "职位名称",
            "标准化职位名称",
            "省份",
            "城市",
            "区域",
            "公司名称",
            "公司规模",
            "公司类别",
            "最低薪资",
            "最高薪资",
            "平均薪资",
            "学历要求",
            "工作经验",
            "原始岗位描述",
            "工作内容",
            "岗位技能要求",
            "岗位福利",
            "福利待遇",
            "岗位描述",
        ]
        final_df = merged[
            [
                "职位名称",
                "标准化职位名称",
                "省份",
                "城市",
                "区域",
                "公司名称",
                "公司规模",
                "公司类别",
                "最低薪资",
                "最高薪资",
                "平均薪资",
                "学历要求",
                "工作经验",
                "原始岗位描述",
                "工作内容",
                "岗位技能要求",
                "岗位福利",
                "福利待遇",
                "岗位描述",
                "岗位类别",
            ]
        ].copy()
        final_df.insert(0, "主键ID", range(1, len(final_df) + 1))
        final_df = final_df[final_columns]
        final_df.columns = [normalize_text(col) for col in final_df.columns]
        final_df.to_csv(OUTPUT_DIR / "all_jobs_cleaned.csv", index=False, encoding="utf-8-sig")

        cleaned_file_count = len(all_frames)
        summary = pd.DataFrame(
            [
                {
                    "原始文件数": len(list(RAW_DIR.glob("*.csv"))),
                    "清洗后文件数": cleaned_file_count,
                    "清洗后总岗位数": len(final_df),
                    "省市全未知删除行数": removed_all_unknown_geo_rows,
                    "标准化职位名称生成条数": (final_df["标准化职位名称"] != "未知").sum(),
                    "福利待遇提取条数": (final_df["福利待遇"] != "未知").sum(),
                    "工作内容可拆分条数": (final_df["工作内容"] != "未知").sum(),
                    "岗位技能要求可拆分条数": (final_df["岗位技能要求"] != "未知").sum(),
                    "岗位福利可拆分条数": (final_df["岗位福利"] != "未知").sum(),
                    "最低薪资可解析条数": (final_df["最低薪资"] != "未知").sum(),
                    "最高薪资可解析条数": (final_df["最高薪资"] != "未知").sum(),
                    "平均薪资可解析条数": (final_df["平均薪资"] != "未知").sum(),
                }
            ]
        )
        summary.to_csv(OUTPUT_DIR / "cleaning_summary.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
