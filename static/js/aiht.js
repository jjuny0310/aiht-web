const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

function poseOnResults(results) {

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(
      results.image, 0, 0, canvasElement.width, canvasElement.height);
  drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#00ff00', lineWidth: 4});
  drawLandmarks(canvasCtx, results.poseLandmarks,
                {color: '#ff0000', lineWidth: 2});

  // Ajax
    var keypoints = JSON.stringify(results.poseLandmarks);

    $.ajax({
        type: 'POST',
        url: '/ajax',
        data: keypoints,
        dataType : 'JSON',
        contentType: "application/json",
        success: function (data){
            console.log(data)
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
  width: 400,
  height: 400
});
camera.start();