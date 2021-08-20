// 모달 창
const modal = document.getElementById("modal")
const btnModal = document.getElementById("btn-modal")
btnModal.addEventListener("click", e => {
    modal.style.display = "flex"
})

const closeBtn = modal.querySelector(".close-area")
closeBtn.addEventListener("click", e => {
    modal.style.display = "none"
})

modal.addEventListener("click", e => {
const evTarget = e.target
if(evTarget.classList.contains("modal-overlay")) {
    modal.style.display = "none"
}
})

window.addEventListener("keyup", e => {
if(modal.style.display === "flex" && e.key === "Escape") {
    modal.style.display = "none"
}
})