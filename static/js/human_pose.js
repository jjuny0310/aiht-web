const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

LoadingWithMask();
var count = 0;
var correct_pose = false;
var soundDelay = 4000;

// 플래그 변수
var loadingFlag = true;
var poseSoundFlag = true;
var trainerEndFlag = true;
var upSoundFlag = true;
var exerciseEndFlag = true;

// 오디오 변수
var leftKneeSound = new Audio('../static/sound/squat/left_knee.mp3');
var rightKneeSound = new Audio('../static/sound/squat/right_knee.mp3');
var ankleSound = new Audio('../static/sound/squat/ankle.mp3');
var footSound = new Audio('../static/sound/squat/foot.mp3');
var nothingSound = new Audio('../static/sound/squat/nothing.mp3');

// 트레이너 비디오 종료 시 처리
function endVideo(){
    trainerEndFlag = false;
    leftKneeSound.pause();
    rightKneeSound.pause();
    ankleSound.pause();
    footSound.pause();
    nothingSound.pause();

    new Audio('../static/sound/end/trainer_end.mp3').play();
    setTimeout(function() { trainerEndFlag = true;}, 6000);
}

function poseOnResults(results) {
    // 캔버스 반응형
    canvasElement.style.width = "100%";

    // 관절선
    if(correct_pose){
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                     {color: '#ffffff', lineWidth: 2});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                    {color: '#BDBDBD', lineWidth: 1});
    }
    else{
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                     {color: '#ff0000', lineWidth: 2});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                    {color: '#BDBDBD', lineWidth: 1});
    }

    // AJAX 통신
    var input_video = $('#input_video');
    var trainer_video = $('#trainer_video');
    var canvas = $('#output_canvas')

    var input_width = input_video.css('width').replace("px", "");
    var input_height = input_video.css('height').replace("px", "");

    var canvas_width = canvas.css('width').replace("px", "");
    var canvas_height = canvas.css('height').replace("px", "");

    var trainer_width = trainer_video.css('width').replace("px", "");
    var trainer_height = trainer_video.css('height').replace("px", "");


    var dataList = {
        'pose_landmarks' : results.poseLandmarks,
        'input_width' : input_width, 'input_height' : input_height,
        'trainer_width' : trainer_width, 'trainer_height' : trainer_height,
        'canvas_width' : canvas_width, 'canvas_height' : canvas_height,
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
                        $('#trainer_video').get(0).play();
                        loadingFlag = false;
                    }
                // 종료 시
                if(data.num === count && exerciseEndFlag){
                    exerciseEndFlag = false;
                    setTimeout(function() { new Audio('../static/sound/end/exercise_end.mp3').play(); }, 1000);
                    setTimeout(function() { location.href = "/result"; }, 5000);
                }

            switch (data.fitness_mode){
                case "SQUAT":
                    // python 에서 전달받은 값
                    correct_pose = data.correct_pose;

                    // 사용자가 지정한 횟수까지 수행
                    if(count < data.num){
                         // 카운트 및 각도 체크 사운드
                        if(upSoundFlag && data.angle_check){
                            new Audio('../static/sound/squat/up.mp3').play();
                            upSoundFlag = false;
                        }
                        if(count !== data.count){
                            count = data.count
                            new Audio('../static/sound/count/' + count + '.mp3').play();
                            document.getElementById('count').innerHTML = "횟수 : " + data.count;
                            upSoundFlag = true;
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
                        else if(poseSoundFlag && data.state==="NOTHING"){
                                nothingSound.play();
                                poseSoundFlag = false;
                                setTimeout(function() { poseSoundFlag = true;}, soundDelay);
                        }   
                    }
                    break;
                case "PUSH_UP":
                    state = data.state;
                    document.getElementById('count').innerHTML = "횟수 : " + data.count;
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