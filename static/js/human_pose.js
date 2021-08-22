const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

LoadingWithMask();
var state = "NOTHING";
var count = 0;
var correct_pose = false;

// 플래그 변수
var loadingFlag = true;

function poseOnResults(results) {
    canvasElement.style.width = "100%";
    // 관절선 그리기

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
                        loadingFlag = false;
                    }
                    // python 에서 전달받은 값
                    state = data.state;
                    correct_pose = data.correct_pose;

                    // 카운트
                    if(count !== data.count){
                        count = data.count
                        new Audio('../static/sound/count/' + count + '.mp3').play();
                        document.getElementById('count').innerHTML = "횟수 : " + data.count;
                    }

                    // console.log(data.correct_dict['correct_right_knee']);
                    // console.log(data.correct_dict['correct_left_knee']);
                    // console.log(data.correct_dict['correct_right_ankle']);
                    // console.log(data.correct_dict['correct_left_ankle']);
                    // console.log(data.correct_dict['correct_left_foot']);
                    // console.log(data.correct_dict['correct_right_foot']);
                    // console.log(correct_pose)












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