let Models = []

window.addEventListener("DOMContentLoaded", async (event)=>{
    init()
})

async function init(){
    await getModels()
    renderHomePage(0)
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

function renderHomePage(targetModel){
    let renderModel
    for (const Model of Models){
        if (Model["model_id"] == targetModel){
            renderModel = Model
            break
        }
    }


}