const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

var state = "NOTHING";
var count = 0;
function poseOnResults(results) {
    // Draw
    if(state==="NOTHING"){
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                     {color: '#ff0000', lineWidth: 3});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                    {color: '#BDBDBD', lineWidth: 1});
    }
    else{
        canvasCtx.save();
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                     {color: '#ffffff', lineWidth: 3});
        drawLandmarks(canvasCtx, results.poseLandmarks,
                    {color: '#BDBDBD', lineWidth: 1});
    }

    // Ajax
    var input_video = $('#input_video');
    var trainer_video = $('#trainer_video');

    var input_width = input_video.css('width').replace("px", "");
    var input_height = input_video.css('height').replace("px", "");

    var trainer_width = trainer_video.css('width').replace("px", "");
    var trainer_height = trainer_video.css('height').replace("px", "");

    var dataList = {
        'pose_landmarks' : results.poseLandmarks, 'input_width' : input_width, 'input_height' : input_height,
        'trainer_width' : trainer_width, 'trainer_height' : trainer_height
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
                    state = data.state
                    document.getElementById('count').innerHTML = "횟수 : " + data.count
                    console.log(data);

                    break;
                case "PUSH_UP":
                    console.log(data);
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