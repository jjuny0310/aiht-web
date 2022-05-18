# 이 프로그램은?
> 운동을 효율적으로 수행할 수 있도록 도와주는 웹 기반 홈 트레이닝 시스템.

AIHT는 AI Home Training의 약자로, AI 기술을 적용하여 홈 트레이닝을 도와주는 서비스를 의미합니다. 주변을 보면 운동에 관심이 높아지고 있었고, 코로나가 지속되어 헬스장이 닫히기도 하는 일이 있었습니다. 이에 따라 운동을 도와주는 비대면 서비스가 있으면 좋겠다 라는 생각으로 이번 프로젝트를 진행하게 되었습니다. Human Pose Estimation 기술을 적용하여 운동 자세를 피드백 해주고, 개수를 세어주는 기능 등이 있습니다.

## 개발 환경
- Python3.7, Flask, Tensorflow Keras
- HTML/CSS, JS, JQuery
- Nginx, Gunicorn
- MediaPipe Pose API
- MySQL
- Docker

## 미리보기
##### <메인 화면 1>
![image](https://user-images.githubusercontent.com/59381113/168851013-dfc1b799-71cc-4a2b-b907-fd239a41a7f4.png)<br>

##### <메인 화면 2>
![image](https://user-images.githubusercontent.com/59381113/168852718-0304e13e-ec4c-48d4-8134-975d00cf3d07.png)<br>
---
##### <회원가입 화면>
![image](https://user-images.githubusercontent.com/59381113/168852878-6de7c87a-05be-44ee-9e37-d8ae94bd167e.png)<br>
---
##### <로그인 화면>
![image](https://user-images.githubusercontent.com/59381113/168852787-15149abe-527d-4a4a-b776-69cf393a1329.png)<br>
---
##### <로딩 화면>
![image](https://user-images.githubusercontent.com/59381113/168852920-7d8bd18b-c39e-45c3-bda5-18fb708061f2.png)<br>
---
##### <스쿼트(올바른 포즈) 예시>
![image](https://user-images.githubusercontent.com/59381113/168853040-ed9fba3f-0dff-4c10-9c0c-961850f22ac1.png)<br>
---
##### <스쿼트(잘못된 포즈) 예시>
![image](https://user-images.githubusercontent.com/59381113/168853116-7204d55e-17b3-4675-ade3-a98c5c5338bb.png)<br>
---
##### <푸쉬업(R, 올바른 포즈) 예시>
![image](https://user-images.githubusercontent.com/59381113/168853174-a77bd4db-0e31-422b-82e5-01f6a9c3a898.png)<br>
---
##### <푸쉬업(L, 올바른 포즈) 예시>
![image](https://user-images.githubusercontent.com/59381113/168853239-7d275c84-0779-4313-89c0-49e1c4523630.png)<br>
---
##### <푸쉬업(잘못된 포즈) 예시>
![image](https://user-images.githubusercontent.com/59381113/168853317-806f7ccf-0022-470c-8d40-455756cf9ae1.png)<br>
---
##### <운동 결과 예시>
![image](https://user-images.githubusercontent.com/59381113/168853368-59453eb4-3daf-4661-b3d3-0335f1032c20.png)<br>
---
##### <과거 운동 내역 예시>
![image](https://user-images.githubusercontent.com/59381113/168853437-6484a4d7-ee6a-4d1d-96b5-64f9805b6db2.png)<br>
