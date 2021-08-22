const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

LoadingWithMask();
var state = "NOTHING";
var count = 0;
// var audio = new Audio('../static/sound/count/1.mp3');

// 플래그 변수
var loadingFlag = true;
var countChangeFlag = true;

function poseOnResults(results) {
    canvasElement.style.width = "100%";
    // 관절선 그리기

    if(state==="NOTHING"){
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                     {color: '#ff0000', lineWidth: 2});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                    {color: '#BDBDBD', lineWidth: 1});
    }
    else{
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                     {color: '#ffffff', lineWidth: 2});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                    {color: '#BDBDBD', lineWidth: 1});
    }

    // Ajax
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
            switch (data.fitness_mode){
                case "SQUAT":
                    // 로딩 완료 시 초기세팅
                    if(loadingFlag) {
                        closeLoadingWithMask();
                        $('#trainer_video').get(0).play();
                        count = data.count;
                        loadingFlag = false;
                    }
                    // python 에서 전달받은 값
                    state = data.state;

                    // 카운트 사운드 출력
                    if(count !== data.count){
                        switch (data.count){
                            case 1:
                                new Audio('../static/sound/count/1.mp3').play();
                                count = data.count
                                break;
                            case 2:
                                new Audio('../static/sound/count/2.mp3').play();
                                count = data.count
                                break;
                            case 3:
                                new Audio('../static/sound/count/3.mp3').play();
                                count = data.count
                                break;
                            case 4:
                                new Audio('../static/sound/count/4.mp3').play();
                                count = data.count
                                break;
                            case 5:
                                new Audio('../static/sound/count/5.mp3').play();
                                count = data.count
                                break;
                            case 6:
                                new Audio('../static/sound/count/6.mp3').play();
                                count = data.count
                                break;
                            case 7:
                                new Audio('../static/sound/count/7.mp3').play();
                                count = data.count
                                break;
                            case 8:
                                new Audio('../static/sound/count/8.mp3').play();
                                count = data.count
                                break;
                            case 9:
                                new Audio('../static/sound/count/9.mp3').play();
                                count = data.count
                                break;
                            case 10:
                                new Audio('../static/sound/count/10.mp3').play();
                                count = data.count
                                break;
                            case 11:
                                new Audio('../static/sound/count/11.mp3').play();
                                count = data.count
                                break;
                            case 12:
                                new Audio('../static/sound/count/12.mp3').play();
                                count = data.count
                                break;
                            case 13:
                                new Audio('../static/sound/count/13.mp3').play();
                                count = data.count
                                break;
                            case 14:
                                new Audio('../static/sound/count/14.mp3').play();
                                count = data.count
                                break;
                            case 15:
                                new Audio('../static/sound/count/15.mp3').play();
                                count = data.count
                                break;
                            case 16:
                                new Audio('../static/sound/count/16.mp3').play();
                                count = data.count
                                break;
                            case 17:
                                new Audio('../static/sound/count/17.mp3').play();
                                count = data.count
                                break;
                            case 18:
                                new Audio('../static/sound/count/18.mp3').play();
                                count = data.count
                                break;
                            case 19:
                                new Audio('../static/sound/count/19.mp3').play();
                                count = data.count
                                break;
                            case 20:
                                new Audio('../static/sound/count/20.mp3').play();
                                count = data.count
                                break;
                            case 21:
                                new Audio('../static/sound/count/21.mp3').play();
                                count = data.count
                                break;
                            case 22:
                                new Audio('../static/sound/count/22.mp3').play();
                                count = data.count
                                break;
                            case 23:
                                new Audio('../static/sound/count/23.mp3').play();
                                count = data.count
                                break;
                            case 24:
                                new Audio('../static/sound/count/24.mp3').play();
                                count = data.count
                                break;
                            case 25:
                                new Audio('../static/sound/count/25.mp3').play();
                                count = data.count
                                break;
                            case 26:
                                new Audio('../static/sound/count/26.mp3').play();
                                count = data.count
                                break;
                            case 27:
                                new Audio('../static/sound/count/27.mp3').play();
                                count = data.count
                                break;
                            case 28:
                                new Audio('../static/sound/count/28.mp3').play();
                                count = data.count
                                break;
                            case 29:
                                new Audio('../static/sound/count/29.mp3').play();
                                count = data.count
                                break;
                            case 30:
                                new Audio('../static/sound/count/30.mp3').play();
                                count = data.count
                                break;
                        }
                    }

                    // 갯수 카운트
                    document.getElementById('count').innerHTML = "횟수 : " + data.count;
                    break;

                case "PUSH_UP":
                    // 로딩 완료 시
                    if(loadingFlag){
                        closeLoadingWithMask();
                        $('#trainer_video').get(0).play();
                        loadingFlag = false;
                    }

                    state = data.state;
                    document.getElementById('count').innerHTML = "횟수 : " + data.count;
                    break;

            }
        },
        error: function (request, status, error){
            // alert(error);
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