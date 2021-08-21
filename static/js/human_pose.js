const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

LoadingWithMask();
var state = "NOTHING";
var count = 0;
var audio = new Audio('../static/sound/count/1.mp3');
var countSoundFlag = false;

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
        success: function (data){
            switch (data.fitness_mode){
                case "SQUAT":
                    // 로딩
                    closeLoadingWithMask();
                    $('#trainer_video').get(0).play();

                    state = data.state;

                    // 갯수 카운트
                    document.getElementById('count').innerHTML = "횟수 : " + data.count;

                    // 카운트 사운드 출력
                    if(countSoundFlag){
                        switch (count){
                            case 1:
                            audio.play();
                            countSoundFlag = false
                            break;
                        }
                    }

                case "PUSH_UP":
                    // 로딩
                    closeLoadingWithMask();
                    $('#trainer_video').get(0).play();

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