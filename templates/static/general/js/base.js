let sidebar = document.querySelector(".sidebar");
let closeBtn = document.querySelector("#btn");
let searchBtn = document.querySelector(".bx-search");

// Protege contra elementos ausentes (evita Uncaught TypeError quando o DOM não contém os seletores)
if (closeBtn) {
    closeBtn.addEventListener("click", ()=>{
        if (sidebar) sidebar.classList.toggle("open");
        menuBtnChange();
    });
}

if (searchBtn) {
    searchBtn.addEventListener("click", ()=>{ 
        if (sidebar) sidebar.classList.toggle("open");
        menuBtnChange();
    });
}

function menuBtnChange() {
if(sidebar.classList.contains("open")){
    closeBtn.classList.replace("bx-menu", "bx-menu-alt-right");
}else {
    closeBtn.classList.replace("bx-menu-alt-right","bx-menu");
}
}