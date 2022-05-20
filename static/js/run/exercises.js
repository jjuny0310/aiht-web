// 웹캠 바
const webcamBar = document.getElementById('webcam_bar');

// 카운트 변수
var count = 0;

// 관절 선 색상 결정(바른자세 : 흰색, 틀린자세 : 빨간색)
var correctPose = true;

// 로딩 후 준비 시간
const readyTime = 10000;

// 사운드 딜레이
const soundDelay = 4000;

// 플래그 변수
var loadingFlag = true;
var readyFlag = false;
var poseSoundFlag = true;
var trainerEndFlag = true;
var downSoundFlag = true;
var exerciseEndFlag = true;
var runStop = false;


// 스쿼트 피드백
function squatRun(data){
    correctPose = data.correct_pose;
    exerciseType = "스쿼트"

    // 사용자가 지정한 횟수까지 수행
    if(readyFlag && count < data.goal_number){
         // DOWN 체크 사운드
        if(downSoundFlag && data.count_check){
            downSound.play();
            downSoundFlag = false;
        }
        // 카운트 사운드(UP 체크)
        if(count !== data.count){
            count = data.count
            new Audio('../static/sound/count/' + count + '.wav').play();
            document.getElementById('count').innerHTML = "현재 횟수 : " + count;
            countIncreaseCheck = true;
            downSoundFlag = true;

        }

        // 자세교정 안내 음성
        if(poseSoundFlag && trainerEndFlag && data.state==="UP" && data.visibility){
            if(data.result['ankle_state'] === "narrow"){
                ankleWideSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
            }
            else if(data.result['ankle_state'] === "wide"){
                ankleNarrowSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
            }
            else if(data.result['foot_state'] === "narrow"){
                footWideSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay+2000);
            }
            else if(data.result['foot_state'] === "wide"){
                footNarrowSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay+2000);
            }
        }
        else if(poseSoundFlag && trainerEndFlag && data.state==="NOTHING" && data.visibility){
                squatNothingSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
        }
    }
}


// 푸쉬업 피드백
function pushupRun(data){
    correctPose = data.correct_pose;
    exerciseType = "푸쉬업"

    // 사용자가 지정한 횟수까지 수행
    if(readyFlag && count < data.goal_number) {
         // DOWN 체크 사운드
        if (downSoundFlag && data.count_check) {
            downSound.play();
            downSoundFlag = false;
        }
        // 카운트 사운드(UP 체크)
        if (count !== data.count) {
            count = data.count
            new Audio('../static/sound/count/' + count + '.wav').play();
            document.getElementById('count').innerHTML = "현재 횟수 : " + count;
            downSoundFlag = true;
        }
        // 자세교정 안내 음성
        if(poseSoundFlag && trainerEndFlag && data.state==="UP" && data.visibility){
            if(!data.result['hand_state']){
                handSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
            }
            else if(!data.result['hip_state']){
                hipSound.play();
                poseSoundFlag = false;
                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
            }
        }
        else if(poseSoundFlag && trainerEndFlag && data.state==="NOTHING" && data.visibility){
            pushupNothingSound.play();
            poseSoundFlag = false;
            setTimeout(function() { poseSoundFlag = true;}, soundDelay);
        }
    }
}


// 로딩 완료 시 초기 설정
function initSetting(){
    closeLoadingWithMask();
    loadingSound.pause();
    loadingSound.currentTime = 0;
    loadingFlag = false;
    webcamBar.style.display = "block";

    // 준비시간
    readySound.play();
    setTimeout(function() {
        startSound.play();

        setTimeout(function() {
        startTime = new Date().getTime() / 1000;
        $('#trainer_video').get(0).play();
        readyFlag = true;}, 1000);
        }, readyTime);
}


// 종료 시
function runEnd(data){
    allSoundStop();
    exerciseEndFlag = false;
    runStop = false;

    endTime = new Date().getTime() / 1000;
    var exerciseTime = parseInt(endTime-startTime);
    exerciseTime = parseInt(exerciseTime / 60) + "분 " + (exerciseTime % 60) + "초";

    setTimeout(function() { exerciseEndSound.play(); }, 500);
    setTimeout(function() {
        location.href = "/result?date=" + monthDate + "&exercise="+exerciseType + "&result_num=" + (count+" / "+data.goal_number)
                        + "&exercise_time=" + exerciseTime; }, 5000);
}


// 종료(중지) 버튼 클릭 시 처리
function stopButtonClick(){
    if(readyFlag === false){
        alert("아직 종료할 수 없습니다.");
    }
    else if(count <= 0){
        alert("운동 횟수가 1회 이상일 때만 종료가 가능합니다.")
    }
    else if(exerciseEndFlag)
    {
        answer = confirm("운동을 종료할까요?");
        if (answer) {
            runStop = true;
        }
    }
}