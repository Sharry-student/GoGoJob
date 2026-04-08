function pieOption(title, data) {
    return {
        tooltip: { trigger: "item" },
        legend: { top: "bottom" },
        series: [{ name: title, type: "pie", radius: ["35%", "70%"], data }]
    };
}

function gradientBar(colorStart, colorEnd) {
    return {
        type: "linear",
        x: 0,
        y: 0,
        x2: 1,
        y2: 0,
        colorStops: [
            { offset: 0, color: colorStart },
            { offset: 1, color: colorEnd }
        ]
    };
}

async function loadDashboard(category = "全部") {
    const { data } = await axios.get("/api/dashboard", { params: { category } });
    document.getElementById("totalJobs").innerText = data.total_jobs;
    document.getElementById("avgSalary").innerText = `${data.avg_salary} 元/月`;

    const edu = echarts.init(document.getElementById("eduChart"));
    const exp = echarts.init(document.getElementById("expChart"));
    const size = echarts.init(document.getElementById("sizeChart"));
    const cityCount = echarts.init(document.getElementById("cityCountChart"));
    const citySalary = echarts.init(document.getElementById("citySalaryChart"));
    const eduOption = pieOption("学历", data.education);
    eduOption.series[0].itemStyle = { borderRadius: 6, borderColor: "#fff", borderWidth: 2 };
    eduOption.series[0].color = ["#4f7cff", "#69b1ff", "#91d5ff", "#adc6ff", "#d6e4ff", "#2f54eb", "#5c7cff", "#85a5ff"];
    const expOption = pieOption("经验", data.experience);
    expOption.series[0].itemStyle = { borderRadius: 6, borderColor: "#fff", borderWidth: 2 };
    expOption.series[0].color = ["#13c2c2", "#36cfc9", "#5cdbd3", "#87e8de", "#b5f5ec", "#08979c", "#006d75", "#95de64"];
    edu.setOption(eduOption);
    exp.setOption(expOption);
    size.setOption({
        tooltip: { trigger: "axis" },
        xAxis: { type: "category", data: data.company_size.map(x => x.name) },
        yAxis: { type: "value" },
        series: [{ type: "bar", data: data.company_size.map(x => x.value), itemStyle: { color: gradientBar("#7c4dff", "#40a9ff"), borderRadius: [6, 6, 0, 0] } }]
    });
    cityCount.setOption({
        tooltip: { trigger: "axis" },
        xAxis: { type: "value" },
        yAxis: { type: "category", data: data.top_cities.map(x => x.name) },
        series: [{ type: "bar", data: data.top_cities.map(x => x.value), itemStyle: { color: gradientBar("#2f54eb", "#597ef7"), borderRadius: [0, 6, 6, 0] } }]
    });
    const salaryVals = data.top_city_salary.map(x => x.value);
    const minVal = salaryVals.length ? Math.min(...salaryVals) : 0;
    const maxVal = salaryVals.length ? Math.max(...salaryVals) : 0;
    const axisMin = minVal > 0 ? Math.floor(minVal * 0.85) : 0;
    const axisMax = maxVal > 0 ? Math.ceil(maxVal * 1.05) : 100;
    citySalary.setOption({
        tooltip: { trigger: "axis" },
        xAxis: { type: "value", min: axisMin, max: axisMax },
        yAxis: { type: "category", data: data.top_city_salary.map(x => x.name) },
        series: [{ type: "bar", data: data.top_city_salary.map(x => x.value), itemStyle: { color: gradientBar("#f5222d", "#fa8c16"), borderRadius: [0, 6, 6, 0] } }]
    });
}

loadDashboard();
