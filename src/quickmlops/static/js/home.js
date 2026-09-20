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
        element.textContent = text;
        return;
    }

    const exponent = document.createElement("sup");
    exponent.textContent = String(Number(match[2]));

    element.replaceChildren(`${match[1]} × 10`, exponent);
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
    const container = document.getElementById("model-stats")
    container.removeChild()
}

function renderStats(data){
    const container = document.getElementById("model-stats")

    const elements = data.map(([key, value])=>{
        const stat = document.createElement("div");
        stat.className = "stat";

        const title = document.createElement("span");
        title.textContent = key;

        const number = document.createElement("strong");
        number.textContent = value ?? "-";

        stat.append(title, number);
        return stat;
    })

    container.replaceChildren(...elements)
}

function renderClassification(data){
    renderStats(data)
}

function renderRegression(data){
    renderStats(data)
}

function renderClustering(data){
    renderStats(data)
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
