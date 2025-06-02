# 🔍 Automatic Crop

**Automatic Crop**은 SAMURAI 객체 추적 기술을 활용하여 K-pop 공연 영상에서 각 멤버를 자동으로 추적하고,<br/>
개인 직캠을 생성하는 지능형 영상처리 시스템입니다.<br/>

사용자가 마우스로 간단히 멤버를 선택하면, AI가 자동으로 전체 영상에서 해당 멤버를 추적하여 부드럽고 안정적인 개인 직캠을 생성합니다.

---

## 🎯 주요 기능

  - 마우스 드래그만으로 간단한 멤버 선택
  - 가우시안스무딩 알고리즘으로 떨림 없는 부드러운 움직임
  - 최대 6명의 멤버 동시 추적
  - 모든 멤버의 추적 박스 표시

---

## ⚙️ 기술 스택

### AI/ML

 - SAMURAI (SAM 2.1) - Meta AI 객체 추적 모델
 - Gaussian Smoothing - 경로 최적화
 - Computer Vision - OpenCV 기반 영상 처리

### Backend

 - Python 3.8+
 - NumPy - 수치 연산
 - SciPy - 계산

### Frontend/UI

 - OpenCV GUI - 시각적 선택 인터페이스
 - PIL (Pillow) - 한글 텍스트 렌더링

---

## 🔧 설치 및 실행

Python 3.8 이상 필요


### SAMURAI 프레임워크 설치

```bash
git clone https://github.com/yangchris11/samurai
cd samurai
# SAM 2.1 모델을 checkpoints/ 폴더에 다운로드
```

### AI-Powered-K-pop-Camera-System 클론 및 다운

```bash
git clone https://github.com/KBohyeon/AI-Powered-K-pop-Camera-System
```

### 의존성 설치

```bash
pip install opencv-python
pip install numpy
pip install pillow
pip install scipy
```

---

📊 프로젝트 구조

samuria/</br>
├── assets    </br>
├── checkpoints                
├── data               
├── lib                       
├── sam2             </br>
├── scripts    # 사무라이 객체 인식 스크립트</br>
├── multi_member_optimal_system.py    </br>
├── 영상.mp4</br>

다운로드한 multi_member_optimal_system.py와 사용할 영상.mp4가 samuria 파일에 들어있어야합니다.

---
## 🌄 실행 결과 보기
>[ (※ 멤버 전체 크롭 박스 영상 링크)](https://www.youtube.com/watch?v=3hWu7DHPN4Q)
>[ (※ 개인 크롭 영상 링크)](https://www.youtube.com/shorts/9QvCRJi_8eQ)
<table>
  <tr>
    <td align="center"><b>멤버 전체 크롭 박스</b></td>
  </tr>
  <tr>
    <td><img src="./images/전체.png" width="100%"></td>
  </tr>
    <tr>
    <td align="center"><b>개인 크롭</b></td>
  </tr>
  <tr>
    <td><img src="./images/해원 개인 크롭.png" width="50%"></td>
  </tr>
</table>

---

## 📌 향후 개선 방향

- 실시간 스트리밍 지원
- 현재 터미널내 실행 가능 -> GUI 인터페이스 개발
- 다양한 출력 비율 지원

---

## 📮 문의

**김보현**  
- 이메일: `qhgus9346@gmail.com`

