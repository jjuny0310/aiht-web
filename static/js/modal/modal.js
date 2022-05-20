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


// 운동 선택 시
function changeExercise(){
    var selectExercise = document.getElementById('select_exercise');
    switch (selectExercise.options[selectExercise.selectedIndex].value){
        case "SQUAT":
            document.getElementById('caution').innerHTML = "'스쿼트'는 카메라를 바라보고 수행 합니다.";
            break;
        case "PUSH_UP":
            document.getElementById('caution').innerHTML = "'푸쉬업'은 몸의 측면이 보이게 하여 수행합니다.(좌우는 상관 없습니다.)";
            break;
    }
}