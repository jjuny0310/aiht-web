var docV = document.documentElement;
var isFull = false;

$('#fullscreen_btn').click(function (){
    isFull = !isFull;
    if(isFull){
        openFullScreenMode();
    }
    else{
        closeFullScreenMode();
    }
});

// 전체화면 설정
function openFullScreenMode() {
    if (docV.requestFullscreen)
        docV.requestFullscreen();
    else if (docV.webkitRequestFullscreen) // Chrome, Safari (webkit)
        docV.webkitRequestFullscreen();
    else if (docV.mozRequestFullScreen) // Firefox
        docV.mozRequestFullScreen();
    else if (docV.msRequestFullscreen) // IE or Edge
        docV.msRequestFullscreen();
}

// 전체화면 해제
function closeFullScreenMode() {
    if (document.exitFullscreen)
        document.exitFullscreen();
    else if (document.webkitExitFullscreen) // Chrome, Safari (webkit)
        document.webkitExitFullscreen();
    else if (document.mozCancelFullScreen) // Firefox
        document.mozCancelFullScreen();
    else if (document.msExitFullscreen) // IE or Edge
        document.msExitFullscreen();
}