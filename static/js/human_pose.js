const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

LoadingWithMask();
var count = 0;
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

// 1. 스쿼트 자세교정 오디오 변수
var leftKneeSound = new Audio('../static/sound/squat/left_knee.wav');
var rightKneeSound = new Audio('../static/sound/squat/right_knee.wav');
var ankleSound = new Audio('../static/sound/squat/ankle.wav');
var footSound = new Audio('../static/sound/squat/foot.wav');
var squatNothingSound = new Audio('../static/sound/squat/nothing.wav');

// 2. 푸쉬업 자세교정 오디오 변수
var hipSound = new Audio('../static/sound/push_up/hip.wav');
var handSound = new Audio('../static/sound/push_up/hand.wav');
var pushupNothingSound = new Audio('../static/sound/push_up/nothing.wav');

// 3. 시작 오디오 변수
var startSound = new Audio('../static/sound/start/exercise_start.wav')
var readySound = new Audio('../static/sound/start/ready.wav')

// 4. 종료 오디오 변수
var trainerEndSound = new Audio('../static/sound/end/trainer_end.wav')
var exerciseEndSound = new Audio('../static/sound/end/exercise_end.wav')

// 5. 카운트 오디오 변수
var downSound = new Audio('../static/sound/count/down.wav')

// 결과 페이지 변수
var now = new Date();
var monthDate = (now.getMonth()+1) + "월 " + now.getDate() + "일";
var startTime = 0;
var endTime = 0;
var exerciseType = ""

// 트레이너 비디오 종료 시 처리
function endVideo(){
    trainerEndFlag = false;

    leftKneeSound.pause();
    rightKneeSound.pause();
    ankleSound.pause();
    footSound.pause();
    squatNothingSound.pause();

    hipSound.pause();
    handSound.pause();
    pushupNothingSound.pause();

    trainerEndSound.play();
    setTimeout(function() { trainerEndFlag = true;}, 6000);
}

function poseOnResults(results) {
    // 캔버스 반응형
    canvasElement.style.width = "100%";

    // 관절선
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

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

    // AJAX 통신
    // var input_video = $('#input_video');
    // var trainer_video = $('#trainer_video');
    // var canvas = $('#output_canvas')
    //
    // var input_width = input_video.css('width').replace("px", "");
    // var input_height = input_video.css('height').replace("px", "");
    //
    // var canvas_width = canvas.css('width').replace("px", "");
    // var canvas_height = canvas.css('height').replace("px", "");
    //
    // var trainer_width = trainer_video.css('width').replace("px", "");
    // var trainer_height = trainer_video.css('height').replace("px", "");


    var dataList = {
        'pose_landmarks' : results.poseLandmarks,
        // 'input_width' : input_width, 'input_height' : input_height,
        // 'trainer_width' : trainer_width, 'trainer_height' : trainer_height,
        // 'canvas_width' : canvas_width, 'canvas_height' : canvas_height,
        'ready_flag' : readyFlag,
    }

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
                        loadingFlag = false;

                        readySound.play();
                        setTimeout(function() {
                            startSound.play();}, readyTime);

                        setTimeout(function() {
                            startTime = new Date().getTime() / 1000;
                            $('#trainer_video').get(0).play();
                            readyFlag = true;}, readyTime + 1000);
                    }
                // 종료 시
                if(data.num === count && exerciseEndFlag){
                    endTime = new Date().getTime() / 1000;
                    var exerciseTime = parseInt(endTime-startTime);
                    exerciseTime = parseInt(exerciseTime / 60) + "분 " + (exerciseTime % 60) + "초";

                    exerciseEndFlag = false;
                    setTimeout(function() { exerciseEndSound.play(); }, 500);
                    setTimeout(function() {
                        location.href = "/result?date=" + monthDate + "&exercise="+exerciseType + "&result_num=" + (count+"/"+data.num)
                                        + "&exercise_time=" + exerciseTime; }, 5000);
                }

            switch (data.fitness_mode){
                case "SQUAT":
                    // python 에서 전달받은 값
                    correct_pose = data.correct_pose;
                    exerciseType = "스쿼트"

                    // 사용자가 지정한 횟수까지 수행
                    if(readyFlag && count < data.num){
                         // 카운트 및 각도 체크 사운드
                        if(downSoundFlag && data.angle_check){
                            downSound.play();
                            downSoundFlag = false;
                        }
                        if(count !== data.count){
                            count = data.count
                            new Audio('../static/sound/count/' + count + '.wav').play();
                            document.getElementById('count').innerHTML = "현재 횟수 : " + count;
                            downSoundFlag = true;
                        }
                        
                        // 자세교정 지시음
                        if(poseSoundFlag && trainerEndFlag && data.state==="UP" && data.visibility){
                            if(!data.correct_dict['correct_left_knee']){
                                leftKneeSound.play();
                                poseSoundFlag = false;
                                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
                            }
                            else if(!data.correct_dict['correct_right_knee']){
                                rightKneeSound.play();
                                poseSoundFlag = false;
                                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
                            }
                            else if(!data.correct_dict['correct_left_ankle'] || !data.correct_dict['correct_right_ankle']){
                                ankleSound.play();
                                poseSoundFlag = false;
                                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
                            }
                            else if(!data.correct_dict['correct_left_foot'] || !data.correct_dict['correct_right_foot']){
                                footSound.play();
                                poseSoundFlag = false;
                                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
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
                    if(readyFlag && count < data.num) {
                        // 카운트 및 각도 체크 사운드
                        if (downSoundFlag && data.angle_check) {
                            downSound.play();
                            downSoundFlag = false;
                        }
                        if (count !== data.count) {
                            count = data.count
                            new Audio('../static/sound/count/' + count + '.wav').play();
                            document.getElementById('count').innerHTML = "현재 횟수 : " + count;
                            downSoundFlag = true;
                        }
                        // 자세교정 지시음
                        if(poseSoundFlag && trainerEndFlag && data.state==="UP" && data.visibility){
                            if(!data.correct_dict['correct_hand']){
                                handSound.play();
                                poseSoundFlag = false;
                                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
                            }
                            else if(!data.correct_dict['correct_hip']){
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