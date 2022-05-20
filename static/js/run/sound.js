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