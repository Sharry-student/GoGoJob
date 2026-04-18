async function fillMapOptions() {
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
    fill("mapCategory", data.categories);
    fill("mapEdu", data.educations);
    fill("mapExp", data.experiences);
    fill("mapSize", data.company_sizes);
}

async function ensureChinaMapRegistered() {
    if (echarts.getMap("china_custom")) {
        return;
    }
    try {
        const resp = await fetch("https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json");
        const geoJson = await resp.json();
        echarts.registerMap("china_custom", geoJson);
    } catch (e) {
        throw new Error("中国地图资源加载失败");
    }
}

function resetMapPanels() {
    const barDom = document.getElementById("mapBarChart");
    const mapDom = document.getElementById("chinaMapChart");
    const bar = echarts.init(barDom);
    const map = echarts.init(mapDom);
    bar.clear();
    map.clear();
    bar.setOption({ graphic: [{ type: "text", left: "center", top: "middle", style: { text: "请先筛选并点击查询", fill: "#8793b0", fontSize: 18 } }] });
    map.setOption({ graphic: [{ type: "text", left: "center", top: "middle", style: { text: "请先筛选并点击查询", fill: "#8793b0", fontSize: 18 } }] });
    const tbody = document.querySelector("#mapTopTable tbody");
    tbody.innerHTML = `<tr><td colspan="2">请先筛选并点击查询</td></tr>`;
}

async function loadMap() {
    const params = {
        category: document.getElementById("mapCategory").value,
        education: document.getElementById("mapEdu").value,
        experience: document.getElementById("mapExp").value,
        company_size: document.getElementById("mapSize").value
    };
    const { data } = await axios.get("/api/map", { params });
    if (!data.map_data || data.map_data.length === 0) {
        const tbody = document.querySelector("#mapTopTable tbody");
        tbody.innerHTML = `<tr><td colspan="2">当前筛选条件下无数据</td></tr>`;
        const bar = echarts.init(document.getElementById("mapBarChart"));
        const map = echarts.init(document.getElementById("chinaMapChart"));
        bar.clear();
        map.clear();
        bar.setOption({ graphic: [{ type: "text", left: "center", top: "middle", style: { text: "当前筛选条件下无柱状图数据", fill: "#8793b0", fontSize: 16 } }] });
        map.setOption({ graphic: [{ type: "text", left: "center", top: "middle", style: { text: "当前筛选条件下无热力图数据", fill: "#8793b0", fontSize: 16 } }] });
        return;
    }
    const chart = echarts.init(document.getElementById("mapBarChart"));
chart.setOption({
    graphic: [],
    tooltip: { trigger: "axis" },

    grid: {
        left: '5%',
        right: '10%',
        bottom: '3%',
        top: '3%',
        containLabel: true
    },
    xAxis: {
        type: "value",
        axisLabel: { fontSize: 11 }
    },
    yAxis: {
        type: "category",
        data: data.map_data.map(x => x.name),
        axisLabel: {

            interval: 0,
            fontSize: 11
        }
    },
    series: [{
        type: "bar",
        data: data.map_data.map(x => x.value),

        barWidth: '60%',
        itemStyle: {

            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#4f7cff' },
                { offset: 1, color: '#91d5ff' }
            ]),
            borderRadius: [0, 4, 4, 0]
        }
    }]
});

    const mapChart = echarts.init(document.getElementById("chinaMapChart"));
    try {
        await ensureChinaMapRegistered();
        mapChart.setOption({
            graphic: [],
            tooltip: {
                trigger: "item",
                formatter: p => `${p.name}<br/>平均薪资：${p.value || 0} 元/月`
            },
            visualMap: {
                min: data.min_value || 0,
                max: data.max_value || 1,
                text: ["高", "低"],
                realtime: false,
                calculable: true,
                inRange: { color: ["#e0ffff", "#66ccff", "#2f67ff", "#213b9a"] },
                left: "left",
                bottom: "5%"
            },
            series: [
                {
                    name: "平均薪资",
                    type: "map",
                    map: "china_custom",
                    roam: true,
                    selectedMode: false,
                    emphasis: { label: { show: true } },
                    data: data.map_data
                }
            ]
        });
        mapChart.off("click");
        mapChart.on("click", async paramsClick => {
            if (!paramsClick || !paramsClick.name) {
                return;
            }
            await loadProvinceDetail(paramsClick.name, params);
        });
    } catch (e) {
        mapChart.clear();
        mapChart.setOption({ graphic: [{ type: "text", left: "center", top: "middle", style: { text: "地图加载失败，请检查网络后重试", fill: "#8793b0", fontSize: 16 } }] });
    }
    const tbody = document.querySelector("#mapTopTable tbody");
    tbody.innerHTML = "";
    data.top10.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.name}</td><td>${row.value} 元/月</td>`;
        tbody.appendChild(tr);
    });
}

async function loadProvinceDetail(mapProvinceName, currentParams) {
    const drawer = new bootstrap.Offcanvas(document.getElementById("provinceDrawer"));
    drawer.show();
    const cityBody = document.querySelector("#drawerCityTable tbody");
    const jobBody = document.querySelector("#drawerJobTable tbody");
    cityBody.innerHTML = `<tr><td colspan="3">加载中...</td></tr>`;
    jobBody.innerHTML = `<tr><td colspan="4">加载中...</td></tr>`;
    const provinceMap = {
        "北京": "北京市", "天津": "天津市", "上海": "上海市", "重庆": "重庆市",
        "内蒙古": "内蒙古自治区", "广西": "广西壮族自治区", "西藏": "西藏自治区", "宁夏": "宁夏回族自治区", "新疆": "新疆维吾尔自治区", "香港": "香港特别行政区", "澳门": "澳门特别行政区"
    };
    let province = provinceMap[mapProvinceName] || mapProvinceName;
    if (!/(省|市|自治区|特别行政区)$/.test(province)) {
        province = `${province}省`;
    }
    const { data } = await axios.get("/api/map/province-detail", { params: { province, ...currentParams } });
    cityBody.innerHTML = "";
    (data.cities || []).forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.city}</td><td>${row.job_count}</td><td>${row.avg_salary} 元/月</td>`;
        cityBody.appendChild(tr);
    });
    if ((data.cities || []).length === 0) {
        cityBody.innerHTML = `<tr><td colspan="3">无数据</td></tr>`;
    }
    jobBody.innerHTML = "";
    (data.jobs || []).forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${row.title}</td><td>${row.city}</td><td>${row.company_name}</td><td>${row.avg_salary} 元/月</td>`;
        jobBody.appendChild(tr);
    });
    if ((data.jobs || []).length === 0) {
        jobBody.innerHTML = `<tr><td colspan="4">无数据</td></tr>`;
    }
}

document.getElementById("btnMapSearch").addEventListener("click", loadMap);
document.getElementById("btnMapReset").addEventListener("click", () => {
    document.getElementById("mapCategory").value = "全部";
    document.getElementById("mapEdu").value = "不限";
    document.getElementById("mapExp").value = "不限";
    document.getElementById("mapSize").value = "不限";
    resetMapPanels();
});
fillMapOptions().then(loadMap);
