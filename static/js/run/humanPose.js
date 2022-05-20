const videoElement = document.getElementsByClassName('input_video')[0];
const canvasElement = document.getElementsByClassName('output_canvas')[0];
const canvasCtx = canvasElement.getContext('2d');

// 로딩 실행
LoadingWithMask();


function poseOnResults(results) {
    // 웹캠 설정
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

    if(correctPose){
         drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#ffffff', lineWidth: 2});
    }
    else{
        drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS,
                 {color: '#ff0000', lineWidth: 2});

    }
    drawLandmarks(canvasCtx, results.poseLandmarks,
                {color: '#BDBDBD', lineWidth: 1});

    // Ajax 전달할 Json 데이터
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
            // 로딩 완료 시 초기 설정
            if(loadingFlag) {
                initSetting();
            }
            // 종료 시
            if((data.goal_number === count && exerciseEndFlag) || runStop){
                runEnd(data);
            }
            // 자세 교정 및 카운터 피드백
            switch (data.exercise_type){
                case "SQUAT":
                    squatRun(data)
                    break;
                case "PUSH_UP":
                    pushupRun(data)
                    break;
            }
        }, error: function (request, status, error){
            alert("code:"+request.status+"\n"+"message:"+request.responseText+"\n"+"error:"+error);
        }
    })
  canvasCtx.restore();
}


const pose = new Pose({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
}});


// MediaPipe Pose 옵션 설정
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