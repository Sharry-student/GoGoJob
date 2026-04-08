async function fillMatchOptions() {
    const { data } = await axios.get("/api/options");
    const title = document.getElementById("mTitle");
    (data.titles || []).forEach(v => {
        const op = document.createElement("option");
        op.value = v;
        op.innerText = v;
        title.appendChild(op);
    });
    const province = document.getElementById("mProvince");
    (data.provinces || []).forEach(v => {
        const op = document.createElement("option");
        op.value = v;
        op.innerText = v;
        province.appendChild(op);
    });
    const city = document.getElementById("mCity");
    const provinceCityMap = data.province_city_map || {};
    province.addEventListener("change", () => {
        const p = province.value;
        city.innerHTML = '<option value="">期望城市</option>';
        (provinceCityMap[p] || []).forEach(v => {
            const op = document.createElement("option");
            op.value = v;
            op.innerText = v;
            city.appendChild(op);
        });
    });
    const fill = (id, arr) => {
        const el = document.getElementById(id);
        (arr || []).forEach(v => {
            const op = document.createElement("option");
            op.value = v;
            op.innerText = v;
            el.appendChild(op);
        });
    };
    fill("mEdu", data.educations);
    fill("mExp", data.experiences);
    fill("mSize", data.company_sizes);
    fill("mMin", data.salary_options);
    fill("mMax", data.salary_options);
}

function renderAnalysis(item) {
    const b = item.score_breakdown || { title_score: 0, location_score: 0, salary_score: 0, skill_score: 0 };
    document.getElementById("anaTitle").innerText = `${b.title_score}%`;
    document.getElementById("anaLoc").innerText = `${b.location_score}%`;
    document.getElementById("anaSalary").innerText = `${b.salary_score}%`;
    document.getElementById("barTitle").style.width = `${b.title_score}%`;
    document.getElementById("barLoc").style.width = `${b.location_score}%`;
    document.getElementById("barSalary").style.width = `${b.salary_score}%`;
    document.getElementById("anaTotal").innerText = item.score || 0;
}

document.getElementById("btnMatch").addEventListener("click", async () => {
    const requiredIds = ["mTitle", "mProvince", "mCity", "mMin", "mMax", "mEdu", "mExp", "mSize"];
    const missing = requiredIds.filter(id => !document.getElementById(id).value);
    if (missing.length > 0) {
        alert("请先填写完整筛选条件后再匹配");
        return;
    }
    const payload = {
        expected_title: document.getElementById("mTitle").value,
        province: document.getElementById("mProvince").value,
        city: document.getElementById("mCity").value,
        expected_min_salary: document.getElementById("mMin").value,
        expected_max_salary: document.getElementById("mMax").value,
        education: document.getElementById("mEdu").value,
        experience: document.getElementById("mExp").value,
        company_size: document.getElementById("mSize").value
    };
    const { data } = await axios.post("/api/match", payload).catch(err => ({ data: err.response?.data || {} }));
    if (data.error) {
        alert(data.error);
        return;
    }
    const container = document.getElementById("matchList");
    document.getElementById("matchSampleCount").innerText = `${data.sample_count || 0}`;
    container.innerHTML = "";
    if (!data.items || data.items.length === 0) {
        container.innerHTML = `<div class="alert alert-warning mb-0">未匹配到岗位，请调整条件后重试</div>`;
        renderAnalysis({ score: 0, matched_skills: 0, total_skills: 0, score_breakdown: { title_score: 0, location_score: 0, salary_score: 0, skill_score: 0 } });
        return;
    }
    data.items.forEach((item, idx) => {
        const card = document.createElement("div");
        card.className = "border rounded p-2 mb-2 bg-light";
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-bold">${item.title}</div>
                    <div class="small text-muted">${item.normalized_title} | ${item.city} | ${item.company_name}</div>
                    <div class="small text-muted">学历:${item.education} 经验:${item.experience} 薪资:${item.avg_salary || "未知"}</div>
                </div>
                <div class="text-end">
                    <div class="fw-bold text-primary">${item.score}</div>
                    <div class="small">匹配分</div>
                </div>
            </div>
            <div class="mt-2 d-flex gap-2">
                <a class="btn btn-sm btn-outline-primary" href="/job/${item.id}" target="_blank">详情</a>
                <button class="btn btn-sm btn-outline-success" data-idx="${idx}">分析</button>
            </div>
        `;
        container.appendChild(card);
    });

    const btns = container.querySelectorAll("button[data-idx]");
    btns.forEach(btn => {
        btn.addEventListener("click", () => {
            const item = data.items[Number(btn.dataset.idx)];
            renderAnalysis(item);
        });
    });

    renderAnalysis(data.items[0]);
});

fillMatchOptions();
