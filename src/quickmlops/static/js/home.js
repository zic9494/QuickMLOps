let Models = []

window.addEventListener("DOMContentLoaded", async (event)=>{
    init()
})

async function init(){
    await getModels()
    renderHomePage(0)
    renderHeader("首頁")
}

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

function renderHeader(title, modelSelect = true){
    
    const selectElement = document.getElementById("model-select")
    if (Models.length <= 1 || !modelSelect){
        selectElement.textContent = ""
    }else{
        headerSelect(selectElement) 
    }

    document.getElementById("header-title").textContent = title
}

function renderHomePage(targetModel){
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