async function fillPredictOptions() {
    const { data } = await axios.get("/api/options");
    const fill = (id, arr) => {
        const el = document.getElementById(id);
        arr.forEach(v => {
            const op = document.createElement("option");
            op.value = v;
            op.innerText = v;
            el.appendChild(op);
        });
    };
    fill("pTitle", data.titles || []);
    fill("pProvince", data.provinces);
    fill("pEdu", data.educations);
    fill("pExp", data.experiences);
    fill("pSize", data.company_sizes);
    const provinceCityMap = data.province_city_map || {};
    const provinceEl = document.getElementById("pProvince");
    const cityEl = document.getElementById("pCity");
    provinceEl.addEventListener("change", () => {
        const province = provinceEl.value;
        cityEl.innerHTML = '<option value="">请选择城市</option>';
        (provinceCityMap[province] || []).forEach(v => {
            const op = document.createElement("option");
            op.value = v;
            op.innerText = v;
            cityEl.appendChild(op);
        });
    });
}

async function loadModelMetrics() {
    const { data } = await axios.get("/api/predict/model-metrics");
    document.getElementById("modelName").innerText = data.model_name || "-";
    document.getElementById("modelMae").innerText = data.mae !== null && data.mae !== undefined ? `${data.mae}` : "-";
    document.getElementById("modelTrainSize").innerText = `${data.train_sample_size || 0}`;
}

document.getElementById("btnPredict").addEventListener("click", async () => {
    const requiredIds = ["pTitle", "pProvince", "pCity", "pEdu", "pExp", "pSize"];
    const missing = requiredIds.filter(id => !document.getElementById(id).value);
    if (missing.length > 0) {
        alert("请先填写完整筛选条件后再预测");
        return;
    }
    const payload = {
        title: document.getElementById("pTitle").value,
        province: document.getElementById("pProvince").value,
        city: document.getElementById("pCity").value,
        education: document.getElementById("pEdu").value,
        experience: document.getElementById("pExp").value,
        company_size: document.getElementById("pSize").value
    };
    const { data } = await axios.post("/api/predict", payload).catch(err => ({ data: err.response?.data || {} }));
    if (data.error) {
        alert(data.error);
        return;
    }
    document.getElementById("predMin").innerText = `${data.min_salary} 元`;
    document.getElementById("predAvg").innerText = `${data.avg_salary} 元`;
    document.getElementById("predMax").innerText = `${data.max_salary} 元`;
    document.getElementById("predConf").innerText = `${data.confidence}%`;
    document.getElementById("predSampleCount").innerText = `${data.sample_count || 0}`;
    document.getElementById("modelName").innerText = data.model_name || "-";
    document.getElementById("modelMae").innerText = data.mae !== null && data.mae !== undefined ? `${data.mae}` : "-";
    document.getElementById("modelTrainSize").innerText = `${data.train_sample_size || 0}`;
});

fillPredictOptions().then(loadModelMetrics);
