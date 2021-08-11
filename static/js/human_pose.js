const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

function poseOnResults(results) {

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
  drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#ffffff', lineWidth: 4});
  drawLandmarks(canvasCtx, results.poseLandmarks,
                {color: '#BDBDBD', lineWidth: 2});


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

    // canvasCtx.font = "30px Arial";
    // canvasCtx.fillText("안녕하세요", 10, 50)

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
  width: 400,
  height: 400
});
camera.start();