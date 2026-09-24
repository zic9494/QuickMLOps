let Models = []
const evaluatoionReslut = new Map()

window.addEventListener("DOMContentLoaded", async (event)=>{
    init()
})

async function init(){
    await getModels()
    await renderHomePage(0)
    renderHeader("首頁")
}


function setStatValue(element, value) {
    const text = String(value ?? "-");
    const match = text.match(/^([+-]?\d+(?:\.\d+)?)e([+-]?\d+)$/i);

    if (!match) {
        element.textContent = Number(text).toFixed(2);
        return;
    }

    const exponent = document.createElement("sup");
    exponent.textContent = String(Number(match[2]));

    element.replaceChildren(`${Number(match[1]).toFixed(2)} x 10`, exponent);
}

// fetch
async function getModels(){
    const response = await fetch(
        "/_quickmlops/models",
        {
            method: "GET"
        }
    )

    if (!response.ok){
        throw new Error("Fetch model list error")
    }
    const reslut = (await response.json())['detail']
    Models = reslut
}

async function getModelEvaluation(model_id){
    if (evaluatoionReslut.has(model_id)){
        return evaluatoionReslut.get(model_id)
    }

    const response = await fetch(
        `/model/${model_id}/evaluation`,
        {
            method: "GET"
        }
    )
    if (response.status == 404){
        evaluatoionReslut.set(model_id, null)
        return null
    }

    if (!response.ok){
        throw new Error("Fetch model list error")
    }

    const reslut = (await response.json())["evaluation"]
    evaluatoionReslut.set(model_id, reslut)

    return reslut
}

// render
function renderHeader(title, modelSelect = true){
    
    const selectElement = document.getElementById("model-select")
    if (Models.length <= 1 || !modelSelect){
        selectElement.textContent = ""
    }else{
        headerSelect(selectElement) 
    }

    document.getElementById("header-title").textContent = title
}

async function renderHomePage(targetModel){
    let renderModel
    for (const Model of Models){
        if (Model["model_id"] == targetModel){
            renderModel = Model
            break
        }
    }
    document.getElementById("model-title").textContent = renderModel["model_name"] || "Unnamed" + ` (ID: ${targetModel})`
    document.getElementById("model-type").textContent = renderModel["task_type"]
        .split("_")
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")

    const version_badges = document.getElementsByClassName("version-badge")
    for (badge of version_badges){
        badge.textContent ="v"+ renderModel["model_version"]
    }

    const data = await getModelEvaluation(targetModel)
    renderEvaluation(renderModel["task_type"] ,data)
}

function renderEvaluation(task_type, data){
    const renderers = {
        classification: renderClassification,
        regression: renderRegression,
        clustering: renderClustering,
    }

    clearEvaluation()

    // if (!data) {
    //     renderEvaluationEmpty()
    //     return
    // }

    const render = renderers[task_type]
    if (!render){
        // renderEvaluationUnsupported
        return 
    }

    render(data)
}

function clearEvaluation(){
    const stat_container = document.getElementById("model-stats")
    stat_container.replaceChildren()

    const dashboard_container = document.getElementById("dashboard")
    dashboard_container.replaceChildren()
}

function renderStats(data, controls = null){
    const container = document.getElementById("model-stats")
    container.classList.toggle("model-stats--classification", Boolean(controls))

    const elements = Object.entries(data).map(([key, value])=>{
        const stat = document.createElement("div");
        stat.className = "stat";

        const title = document.createElement("span");
        title.textContent = key;

        const number = document.createElement("strong");
        setStatValue(number, value);

        stat.append(title, number);
        return stat;
    })

    container.replaceChildren(
        ...(controls ? [controls] : []),
        ...elements
    )
}

function renderClassification(data){
    const {
        "Confusion Matrix": confusionMatrix,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1Score,
    } = data

    const labels = confusionMatrix["labels"]
    

    function showClass(index){
        renderStats({
            Accuracy: accuracy,
            Precision: precision.values[index],
            Recall: recall.values[index],
            "F1-Score": f1Score.values[index],
        }, selector)
    }

    const selector = renderClassificationControls(labels, showClass)
    showClass(0)
    renderConfusionMatrix(confusionMatrix)
    
}

function renderRegression(data){
    renderStats(data)
}

function renderClustering(data){
    renderStats(data)
}

function renderConfusionMatrix(matrix){
    const container = document.querySelector(".dashboard-grid")
    if (!container) return

    const card = document.createElement("section")
    card.className = "card confusion-matrix-card"

    const header = document.createElement("header")
    header.className = "card__header"
    const title = document.createElement("h3")
    title.textContent = "混淆矩陣"
    const description = document.createElement("p")
    description.textContent = "列為實際類別，欄為預測類別；顏色越深代表筆數越多。"
    header.append(title, description)
    card.appendChild(header)

    const labels = matrix?.labels
    const values = matrix?.values
    if (!Array.isArray(labels) || !labels.length ||
        !Array.isArray(values) || values.length !== labels.length ||
        values.some(row => !Array.isArray(row) || row.length !== labels.length)) {
        const empty = document.createElement("p")
        empty.className = "confusion-matrix-empty"
        empty.textContent = "沒有可顯示的混淆矩陣資料。"
        card.appendChild(empty)
        container.replaceChildren(card)
        return
    }

    const max = values.reduce((largest, row) =>
        row.reduce((current, value) => Math.max(current, Number(value) || 0), largest), 0)
    const scroll = document.createElement("div")
    scroll.className = "confusion-matrix-scroll"
    const table = document.createElement("table")
    table.className = "confusion-matrix"
    const caption = document.createElement("caption")
    caption.textContent = "混淆矩陣：列為實際類別，欄為預測類別"
    table.appendChild(caption)

    const thead = document.createElement("thead")
    const heading = document.createElement("tr")
    const corner = document.createElement("th")
    corner.scope = "col"
    corner.textContent = "實際 ＼ 預測"
    heading.appendChild(corner)
    labels.forEach(label => {
        const cell = document.createElement("th")
        cell.scope = "col"
        cell.textContent = String(label)
        heading.appendChild(cell)
    })
    thead.appendChild(heading)
    table.appendChild(thead)

    const tbody = document.createElement("tbody")
    values.forEach((row, rowIndex) => {
        const tr = document.createElement("tr")
        const labelCell = document.createElement("th")
        labelCell.scope = "row"
        labelCell.textContent = String(labels[rowIndex])
        tr.appendChild(labelCell)
        row.forEach((rawValue, columnIndex) => {
            const cell = document.createElement("td")
            const value = Number(rawValue)
            const count = Number.isFinite(value) && value >= 0 ? value : 0
            const strength = max ? count / max : 0
            cell.textContent = count.toLocaleString()
            cell.style.backgroundColor = `rgba(79, 70, 229, ${0.06 + strength * 0.8})`
            cell.style.color = strength > 0.55 ? "#fff" : "#172033"
            cell.setAttribute("aria-label", `實際 ${labels[rowIndex]}，預測 ${labels[columnIndex]}：${count} 筆`)
            tr.appendChild(cell)
        })
        tbody.appendChild(tr)
    })
    table.appendChild(tbody)
    scroll.appendChild(table)
    card.appendChild(scroll)
    container.replaceChildren(card)
}

function renderClassificationControls(label, onChange){
    const controls = document.createElement("div")
    controls.className = "classification-controls"

    const fieldLabel = document.createElement("label")
    fieldLabel.className = "classification-controls__label"
    fieldLabel.textContent = "選擇類別"

    const selector = createClassSelector(label)
    selector.className = "classification-controls__select"
    selector.id = "classification-class-select"
    fieldLabel.htmlFor = selector.id

    selector.addEventListener("change", ()=>{
        onChange(selector.selectedIndex)
    })

    controls.append(fieldLabel, selector)
    return controls
}

function createClassSelector(labels){
    const container = document.createElement("select")
    
    labels.forEach(label => {
        const option = document.createElement("option")

        option.value = label
        option.textContent = label

        container.appendChild(option)
    });

    return container
}

function headerSelect(container){
    const select  = document.createElement("select")
    select.setAttribute("aria-label", "選擇模型")

    for (const model of Models) {
        const option = document.createElement("option")
        let model_name = model.model_name || "Unnamed"
        option.value = model.model_id
        option.textContent = `${model_name} (ID: ${model["model_id"]})`

        select.appendChild(option)
    }

    select.addEventListener("change", (event) =>{
        renderHomePage(Number(event.target.value))
    })

    container.replaceChildren(select)
}
