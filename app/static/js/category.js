async function loadCategory() {
    const { data } = await axios.get("/api/dashboard", { params: { category: window.currentCategory } });
    document.getElementById("catTotalJobs").innerText = data.total_jobs;
    document.getElementById("catAvgSalary").innerText = `${data.avg_salary} 元/月`;
    const edu = echarts.init(document.getElementById("catEduChart"));
    const exp = echarts.init(document.getElementById("catExpChart"));
    const option = (title, rows) => ({
        tooltip: { trigger: "item" },
        legend: { top: "bottom" },
        series: [{ name: title, type: "pie", radius: ["35%", "70%"], data: rows }]
    });
    edu.setOption(option("学历", data.education));
    exp.setOption(option("经验", data.experience));
    const tbody = document.querySelector("#catJobTable tbody");
    tbody.innerHTML = "";
    (data.top_jobs || []).forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.title}</td><td>${row.city}</td><td>${row.company_name}</td><td>${row.avg_salary} 元/月</td><td>${row.education}</td><td>${row.experience}</td>`;
        tbody.appendChild(tr);
    });
    if ((data.top_jobs || []).length === 0) {
        tbody.innerHTML = `<tr><td colspan="6">暂无数据</td></tr>`;
    }
}

loadCategory();
