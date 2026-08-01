const bar_btn = document.getElementsByClassName("nav-item")
for (const btn of bar_btn){
    btn.onclick = function () {
        for (const bar of bar_btn){
            bar.classList = "nav-item"
        }
        btn.classList.add("nav-item--active")
    }
}