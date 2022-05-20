var count = 0;
var webcamBar = document.getElementById('webcam_bar');
var correct_pose = true;
var soundDelay = 4000;
var readyTime = 10000;

// 플래그 변수
var loadingFlag = true;
var readyFlag = false;
var poseSoundFlag = true;
var trainerEndFlag = true;
var downSoundFlag = true;
var exerciseEndFlag = true;
var runStop = false;

LoadingWithMask();

// 스쿼트 처리
function squatRun(){
    correct_pose = data.correct_pose;
    exerciseType = "스쿼트"

    // 사용자가 지정한 횟수까지 수행
    if(readyFlag && count < data.goal_number){
         // 카운트 및 각도 체크 사운드
        if(downSoundFlag && data.count_check){
            downSound.play();
            downSoundFlag = false;
        }
        if(count !== data.count){
            count = data.count
            new Audio('../static/sound/count/' + count + '.wav').play();
            document.getElementById('count').innerHTML = "현재 횟수 : " + count;
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

// 푸쉬업 처리
function pushupRun(){
    correct_pose = data.correct_pose;
    exerciseType = "푸쉬업"

    // 사용자가 지정한 횟수까지 수행
    if(readyFlag && count < data.goal_number) {
        // 카운트 및 각도 체크 사운드
        if (downSoundFlag && data.count_check) {
            downSound.play();
            downSoundFlag = false;
        }
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

// 로딩 완료 시 초기세팅
function initSetting(){
    closeLoadingWithMask();
    loadingSound.pause();
    loadingSound.currentTime = 0;
    loadingFlag = false;
    webcamBar.style.display = "block";

    // 준비시간(10초)
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
function runEnd(){
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