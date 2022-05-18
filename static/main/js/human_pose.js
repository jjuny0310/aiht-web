const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

var count = 0;
var countText = document.getElementById('count_text');
var webcamBar = document.getElementById('webcam_bar');
var correct_pose = true;
var soundDelay = 4000;
var readyTime = 10000;

LoadingWithMask();

// 플래그 변수
var loadingFlag = true;
var readyFlag = false;
var poseSoundFlag = true;
var trainerEndFlag = true;
var downSoundFlag = true;
var exerciseEndFlag = true;
var runStop = false;

// 1. 스쿼트 자세교정 오디오 변수
var ankleNarrowSound = new Audio('../static/sound/squat/ankle_narrow.wav');
var ankleWideSound = new Audio('../static/sound/squat/ankle_wide.wav');
var footNarrowSound = new Audio('../static/sound/squat/foot_narrow.wav');
var footWideSound = new Audio('../static/sound/squat/foot_wide.wav');
var squatNothingSound = new Audio('../static/sound/squat/nothing.wav');

// 2. 푸쉬업 자세교정 오디오 변수
var hipSound = new Audio('../static/sound/push_up/hip.wav');
var handSound = new Audio('../static/sound/push_up/hand.wav');
var pushupNothingSound = new Audio('../static/sound/push_up/nothing.wav');

// 3. 시작 오디오 변수
var startSound = new Audio('../static/sound/start/exercise_start.wav');
var readySound = new Audio('../static/sound/start/ready.wav');

// 4. 종료 오디오 변수
var trainerEndSound = new Audio('../static/sound/end/trainer_end.wav');
var exerciseEndSound = new Audio('../static/sound/end/exercise_end.wav');

// 5. 카운트 오디오 변수
var downSound = new Audio('../static/sound/count/down.wav');

// 6. 로딩 오디오 변수
var loadingSound = new Audio('../static/loading/sound/loading_sound.wav');
loadingSound.play();

// 결과 페이지 변수
var now = new Date();
var monthDate = (now.getMonth()+1) + "월 " + now.getDate() + "일";
var startTime = 0;
var endTime = 0;
var exerciseType = "";

// 종료 버튼 클릭 시 처리
function stop(){
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

// 모든 사운드 중지
function allSoundStop(){
    ankleNarrowSound.pause();
    ankleWideSound.pause();
    footNarrowSound.pause();
    footWideSound.pause();
    squatNothingSound.pause();

    hipSound.pause();
    handSound.pause();
    pushupNothingSound.pause();

    startSound.pause();
    readySound.pause();

    trainerEndSound.pause();
    exerciseEndSound.pause();

    downSound.pause();

    ankleNarrowSound.currentTime = 0;
    ankleWideSound.currentTime = 0;
    footNarrowSound.currentTime = 0;
    footWideSound.currentTime = 0;
    squatNothingSound.currentTime = 0;

    hipSound.currentTime = 0;
    handSound.currentTime = 0;
    pushupNothingSound.currentTime = 0;

    startSound.currentTime = 0;
    readySound.currentTime = 0;

    trainerEndSound.currentTime = 0;
    exerciseEndSound.currentTime = 0;

    downSound.currentTime = 0;
}

// 트레이너 비디오 종료 시 처리
function endVideo(){
    trainerEndFlag = false;
    ankleNarrowSound.pause();
    ankleWideSound.pause();
    footNarrowSound.pause();
    footWideSound.pause();
    squatNothingSound.pause();

    hipSound.pause();
    handSound.pause();
    pushupNothingSound.pause();

    trainerEndSound.play();

    ankleNarrowSound.currentTime = 0;
    ankleWideSound.currentTime = 0;
    footNarrowSound.currentTime = 0;
    footWideSound.currentTime = 0;
    squatNothingSound.currentTime = 0;

    hipSound.currentTime = 0;
    handSound.currentTime = 0;
    pushupNothingSound.currentTime = 0;

    trainerEndSound.play();
    setTimeout(function() { trainerEndFlag = true;}, 6000);
}
function poseOnResults(results) {
    // 캔버스 조정
    canvasElement.style.position = "absolute";
    canvasElement.style.left = "0";
    canvasElement.style.top = "0";
    canvasElement.style.width = "100%";
    canvasElement.style.height = "100%";
    canvasElement.style.objectFit = "contain";
    canvasElement.style.transform = "rotateY(180deg)";

    // 관절선
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

    console.log(correct_pose)
    if(correct_pose){
         drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#ffffff', lineWidth: 2});
    }
    else{
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#ff0000', lineWidth: 2});

    }
    drawLandmarks(canvasCtx, results.poseLandmarks,
                {color: '#BDBDBD', lineWidth: 1});

    // 전달할 Json 데이터
    var dataList = {
        'pose_landmarks' : results.poseLandmarks,
        'ready_flag' : readyFlag,
    }

    // Ajax 통신(Python <-> Javascript)
    $.ajax({
        type: 'POST',
        url: '/exercise_analysis',
        data: JSON.stringify(dataList),
        dataType : 'JSON',
        contentType: "application/json",
        async: false,
        success: function (data){
            // 로딩 완료 시 초기세팅
            if(loadingFlag) {
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
            if((data.goal_number === count && exerciseEndFlag) || runStop){
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

            switch (data.exercise_type){
                case "SQUAT":
                    // python 에서 전달받은 데이터
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
                    break;
                case "PUSH_UP":
                    // python 에서 전달받은 값
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
                    break;
            }
        },
        error: function (request, status, error){
        }
    })
  canvasCtx.restore();
}

const pose = new Pose({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
}});
pose.setOptions({
  modelComplexity: 1,
  selfieMode: false,
  smoothLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});
pose.onResults(poseOnResults);

const camera = new Camera(videoElement, {
  onFrame: async () => {
    await pose.send({image: videoElement});
  },
  width: 480,
  height: 480
});
camera.start();