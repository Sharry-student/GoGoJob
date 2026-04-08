async function loadJobDetail() {
    const { data } = await axios.get(`/api/job/${window.jobId}`);
    if (!data || !data.job) {
        return;
    }
    document.getElementById("dTitle").innerText = data.job.normalized_title || data.job.title;
    document.getElementById("dCount").innerText = data.job.peer_count;
    document.getElementById("dAvg").innerText = `${data.job.peer_avg_salary || 0}`;
    document.getElementById("dCur").innerText = `${data.job.avg_salary || 0}`;

    const trend = echarts.init(document.getElementById("trendChart"));
    trend.setOption({
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: data.trend.map(x => x.name) },
        yAxis: { type: "value" },
        series: [{ type: "line", smooth: true, data: data.trend.map(x => x.value) }]
    });

    const skill = echarts.init(document.getElementById("skillChart"));
    skill.setOption({
        tooltip: { trigger: "axis" },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: data.skills_top10.map(x => x.name) },
        series: [{ type: "bar", data: data.skills_top10.map(x => x.value) }]
    });

    const company = echarts.init(document.getElementById("companyChart"));
    company.setOption({
        tooltip: { trigger: "item" },
        legend: { top: "bottom" },
        series: [{ type: "pie", radius: ["35%", "70%"], data: data.company_distribution }]
    });

    const similarRes = await axios.get(`/api/job/${window.jobId}/similar`);
    const tbody = document.querySelector("#similarTable tbody");
    tbody.innerHTML = "";
    (similarRes.data.items || []).forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${item.title}</td><td>${item.normalized_title}</td><td>${item.province}-${item.city}</td><td>${item.company_name}</td><td>${item.avg_salary || "未知"}</td><td>${item.similarity}</td>`;
        tbody.appendChild(tr);
    });
    document.getElementById("exportSimilarBtn").href = `/api/job/${window.jobId}/similar/export`;
}

loadJobDetail();
