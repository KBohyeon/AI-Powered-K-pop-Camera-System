import subprocess
import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from scipy import interpolate
from scipy.ndimage import gaussian_filter1d

def put_korean_text(img, text, position, font_size=30, color=(255, 255, 255)):
    #한글 텍스트를 이미지에 추가
    try:
        img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        
        try:
            font = ImageFont.truetype("malgun.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        color_rgb = (color[2], color[1], color[0])  # BGR → RGB
        bbox = draw.textbbox(position, text, font=font) # 바운딩 박스 계산
        draw.rectangle(bbox, fill=(0, 0, 0, 180)) # 반투명 배경 추가
        draw.text(position, text, font=font, fill=color_rgb) 
        
        img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        return img_cv
    except Exception as e:
        print(f"한글 텍스트 추가 실패: {e}")
        cv2.putText(img, text.encode('ascii', 'ignore').decode('ascii'), 
                position, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        return img

def select_multiple_members(video_path):
    """6명까지 순서대로 드래그 선택 (이름 직접 입력)"""
    print("최소 1명 부터 최대 6명의 멤버를 순서대로 선택하세요")
    print("사용법:")
    print("   1. 터미널에서 슬롯 번호 입력 (1~6)")
    print("   2. 멤버 이름 입력")
    print("   3. 해당 멤버를 마우스로 드래그(전신을 드래그 하셔야 합니다.)")
    print("   4. Enter로 확인, 다음 멤버 선택")
    print("   5. 'q' 입력시 선택 완료(실행)")
    
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("비디오 읽기 실패")
        return {}
    
    print(f"Video size: {frame.shape[1]}x{frame.shape[0]}")
    
    # 색상 정보 (6개 슬롯)
    slot_colors = [
        (0, 0, 255),      # 빨간색
        (0, 165, 255),    # 주황색
        (0, 255, 255),    # 노란색
        (0, 255, 0),      # 초록색
        (255, 0, 0),      # 파란색
        (255, 0, 255),    # 보라색
    ]
    
    color_names = ["빨간색", "주황색", "노란색", "초록색", "파란색", "보라색"]
    
    selected_members = {}
    used_slots = set()
    display_frame = frame.copy()
    
    print("\n사용 가능한 색상 슬롯:")
    for i, color_name in enumerate(color_names):
        print(f"   {i+1}. {color_name}")
    
    while len(selected_members) < 6:
        print(f"\n현재 선택된 멤버: {len(selected_members)}/6명")
        # 사용된거 표기
        used_slots_display = [slot + 1 for slot in sorted(used_slots)] if used_slots else []
        print(f"사용된 슬롯: {used_slots_display if used_slots_display else '없음'}")
        
        # 슬롯 번호 입력
        while True:  # 슬롯 선택 루프
            try:
                user_input = input(f"색상 슬롯 번호 입력 (1-6) 또는 'q'로 완료: ").strip()
                
                if user_input.lower() == 'q':
                    return selected_members  # 함수 종료
                    
                slot_idx = int(user_input) - 1
                
                if slot_idx < 0 or slot_idx >= 6:
                    print("❌ 1~6 사이의 숫자를 입력하세요")
                    continue
                    
                if slot_idx in used_slots:
                    # 기존 멤버 정보 찾기
                    existing_member = None
                    for name, info in selected_members.items():
                        if info['slot_index'] == slot_idx:
                            existing_member = name
                            break
                    
                    print(f"❌ {slot_idx + 1}번 슬롯({color_names[slot_idx]})은 이미 사용 중입니다.")
                    if existing_member:
                        print(f"   현재 할당된 멤버: {existing_member}")
                    
                    retry = input("기존 선택을 덮어쓰시겠습니까?(Y/N): ").strip().upper()
                    if retry == 'Y':
                        # 기존 멤버 제거
                        if existing_member:
                            del selected_members[existing_member]
                            used_slots.remove(slot_idx)
                            print(f"✅ {existing_member} 선택이 제거되었습니다.")
                            
                            # display_frame을 다시 그리기 (제거된 박스 반영)
                            display_frame = frame.copy()
                            for remaining_name, remaining_info in selected_members.items():
                                x, y, w, h = remaining_info['bbox']
                                remaining_color = remaining_info['color']
                                cv2.rectangle(display_frame, (x, y), (x+w, y+h), remaining_color, 3)
                                display_frame = put_korean_text(display_frame, remaining_name, (x, y-35), 
                                                                font_size=24, color=remaining_color)
                        
                        break  # 같은 슬롯으로 새로 선택 진행
                    elif retry == 'N':
                        slot_idx = None  # 슬롯 선택 건너뛰기 표시
                        break  # 슬롯 선택 루프 탈출
                    else:
                        print("Y 또는 N을 입력하세요")
                        continue
                else:
                    break  # 유효한 슬롯 선택됨
                    
            except ValueError:
                print("❌ 숫자를 입력하세요")
                continue
            except KeyboardInterrupt:
                print("\n❌ 선택이 취소되었습니다")
                return {}
        
        # N을 선택해서 슬롯 선택을 건너뛴 경우
        if slot_idx is None:
            continue
        
        # 멤버 이름 입력
        try:
            member_name = input(f"{color_names[slot_idx]} 슬롯에 할당할 멤버 이름: ").strip()
            
            if not member_name:
                print("❌ 멤버 이름을 입력하세요")
                continue
                
            if member_name in selected_members:
                print(f"❌ '{member_name}'은 이미 선택되었습니다")
                continue
                
        except KeyboardInterrupt:
            print("\n❌ 선택이 취소되었습니다")
            return {}
        
        # 색상 정보
        color = slot_colors[slot_idx]
        color_name = color_names[slot_idx]
        
        print(f"\n {member_name} ({color_name} 슬롯)을 마우스로 드래그하여 선택하세요...")
        
        # 20% 축소로 창 표시하고 위치 조정
        new_width = int(frame.shape[1] * 0.8)  # 80% 크기 (20% 축소)
        new_height = int(frame.shape[0] * 0.8)
        display_small = cv2.resize(display_frame, (new_width, new_height))
        
        # 한글 깨짐 방지를 위해 영어로 창 제목 설정
        window_name = f"Member Selection_Slot"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, new_width, new_height)
        cv2.moveWindow(window_name, 100, 50)  # 화면 위쪽으로 이동
        
        # 원본 크기 기준으로 ROI 선택 (화면은 작게 표시하지만 좌표는 원본 기준)
        bbox = cv2.selectROI(window_name, display_frame, False, False)
        cv2.destroyAllWindows()
        
        if bbox[2] > 0 and bbox[3] > 0:
            selected_members[member_name] = {
                'bbox': bbox,
                'color': color,
                'color_name': color_name,
                'slot_index': slot_idx
            }
            
            used_slots.add(slot_idx)
            
            # 선택된 박스를 display_frame에 그리기
            x, y, w, h = bbox
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 3)
            
            # 멤버 이름 추가
            display_frame = put_korean_text(display_frame, member_name, (x, y-35), 
                                        font_size=24, color=color)
            
            print(f"✅ {member_name} ({color_name}) 선택됨: {bbox}")
        else:
            print(f"❌ {member_name} 선택이 취소되었습니다")
    
    print(f"\n📊 최종 선택: {len(selected_members)}명")
    for name, info in selected_members.items():
        print(f"   {name}: {info['color_name']} 슬롯 {info['bbox']}")
    
    return selected_members

def create_bbox_file(bbox, filename):
    # 바운딩박스 파일 생성
    x, y, w, h = bbox
    with open(filename, 'w') as f:
        f.write(f"{x},{y},{w},{h}")

def run_single_tracking(video_path, bbox_file, model_path, output_path): 
    # SAMURAI 추적 실행
    cmd = [
        "python", "scripts/demo.py",
        "--video_path", video_path,
        "--txt_path", bbox_file,
        "--model_path", model_path,
        "--video_output_path", output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return True
    else:
        print(f"❌ 추적 실패: {result.stderr}")
        return False

def extract_center_coords(tracked_video, original_video):
    # 전체 경로 추출
    original_cap = cv2.VideoCapture(original_video)
    tracked_cap = cv2.VideoCapture(tracked_video)
    
    center_coords = []
    frame_count = 0
    valid_detections = 0
    
    while True:
        ret_orig, orig_frame = original_cap.read()
        ret_track, track_frame = tracked_cap.read()
        
        if not ret_orig or not ret_track:
            break
        
        frame_count += 1
        
        if track_frame.shape[:2] != orig_frame.shape[:2]:
            track_frame = cv2.resize(track_frame, (orig_frame.shape[1], orig_frame.shape[0]))
        
        diff = cv2.absdiff(track_frame, orig_frame)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 500:
                x, y, w, h = cv2.boundingRect(largest)
                body_start_y = y + int(h * 0.15)  
                body_end_y = y + int(h * 0.75)    
                body_center_y = (body_start_y + body_end_y) // 2
                body_center_x = x + w // 2
                
                center_coords.append((body_center_x, body_center_y))
                valid_detections += 1
            else:
                center_coords.append(None)
        else:
            center_coords.append(None)
    
    original_cap.release()
    tracked_cap.release()
    
    return center_coords

def interpolate_missing_positions(center_coords):
    #누락된 위치 보간
    valid_indices = []
    valid_x = []
    valid_y = []
    
    for i, coord in enumerate(center_coords):
        if coord is not None:
            valid_indices.append(i)
            valid_x.append(coord[0])
            valid_y.append(coord[1])
    
    if len(valid_indices) < 2:
        return center_coords
    
    all_indices = np.arange(len(center_coords))
    interp_x = np.interp(all_indices, valid_indices, valid_x)
    interp_y = np.interp(all_indices, valid_indices, valid_y)
    
    interpolated_coords = [(int(x), int(y)) for x, y in zip(interp_x, interp_y)]
    return interpolated_coords

def calculate_optimal_camera_path(center_coords, crop_width=400, crop_height=750):
    #최적 카메라 경로 계산
    interpolated_coords = interpolate_missing_positions(center_coords)
    
    x_coords = np.array([coord[0] for coord in interpolated_coords])
    y_coords = np.array([coord[1] for coord in interpolated_coords])
    
    smoothing_sigma = 8.0
    
    try:
        smooth_x = gaussian_filter1d(x_coords, sigma=smoothing_sigma)
        smooth_y = gaussian_filter1d(y_coords, sigma=smoothing_sigma)
    except:
        smooth_x = x_coords
        smooth_y = y_coords
    
    TOP_MARGIN = 100 #상단 여백(머리)
    BOTTOM_MARGIN = 120 #하단 여백(발)
    
    camera_x = smooth_x
    camera_y = smooth_y + BOTTOM_MARGIN - TOP_MARGIN 
    
    optimal_path = [(int(x), int(y)) for x, y in zip(camera_x, camera_y)] # 정수 좌표로 변환
    return optimal_path 

def create_optimal_cropped_video(original_video, optimal_camera_path, output_path, member_name, crop_width=400, crop_height=750):
    #개인 크롭 영상 생성
    print(f"{member_name} 최적화된 크롭 영상 생성 중")
    
    cap = cv2.VideoCapture(original_video) 
    fps = cap.get(cv2.CAP_PROP_FPS)
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (crop_width, crop_height))
    
    frame_idx = 0
    
    while True:
        ret, frame = cap.read() 
        if not ret:
            break
        
        if frame_idx < len(optimal_camera_path): 
            cam_x, cam_y = optimal_camera_path[frame_idx]
            
            start_x = max(0, cam_x - crop_width // 2)
            start_y = max(0, cam_y - crop_height // 2)
            
            if start_x + crop_width > orig_width:
                start_x = orig_width - crop_width
            if start_y + crop_height > orig_height:
                start_y = orig_height - crop_height
            
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            
            end_x = start_x + crop_width
            end_y = start_y + crop_height
            
            cropped_frame = frame[start_y:end_y, start_x:end_x]
            
            if cropped_frame.shape[:2] != (crop_height, crop_width):
                padded_frame = np.zeros((crop_height, crop_width, 3), dtype=np.uint8)
                h, w = cropped_frame.shape[:2]
                padded_frame[:h, :w] = cropped_frame
                cropped_frame = padded_frame
                
        else:
            cropped_frame = np.zeros((crop_height, crop_width, 3), dtype=np.uint8)
        
        out.write(cropped_frame)
        frame_idx += 1
        
        if frame_idx % 60 == 0:
            print(f"{member_name}: {frame_idx} frames processed...")
    
    cap.release()
    out.release()
    print(f"✅ {member_name} 크롭 영상 완료: {output_path}")

def create_full_view_with_crop_boxes(original_video, all_camera_paths, member_info, output_path, crop_width=400, crop_height=750): 
    #전체 영상에 각 멤버의 크롭 박스 표시
    print(f"전체 영상에 크롭 박스 표시 생성 중...")
    
    cap = cv2.VideoCapture(original_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
    out = cv2.VideoWriter(output_path, fourcc, fps, (orig_width, orig_height)) 
    
    frame_idx = 0 # 프레임 인덱스 초기화
    
    print(f"전체 박스 영상 생성")
    print(f"   원본 크기 유지: {orig_width}x{orig_height}")
    print(f"   각 멤버별 크롭 박스 실시간 표시")
    print(f"   멤버별 고유 색상 박스")
    print(f"   카메라가 실제로 크롭하는 영역 시각화")
    print(f"   선택된 멤버: {', '.join(member_info.keys())}")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        result_frame = frame.copy()
        
        # 각 멤버의 크롭 박스 그리기
        for member_name, info in member_info.items():
            if member_name in all_camera_paths:
                camera_path = all_camera_paths[member_name]
                
                if frame_idx < len(camera_path):
                    cam_x, cam_y = camera_path[frame_idx]
                    color = info['color']
                    
                    # 크롭 박스 계산
                    box_x = max(0, cam_x - crop_width // 2)
                    box_y = max(0, cam_y - crop_height // 2)
                    
                    if box_x + crop_width > orig_width:
                        box_x = orig_width - crop_width
                    if box_y + crop_height > orig_height:
                        box_y = orig_height - crop_height
                    
                    box_x = max(0, box_x)
                    box_y = max(0, box_y)
                    
                    # 크롭 박스 그리기
                    cv2.rectangle(result_frame, 
                                (box_x, box_y), 
                                (box_x + crop_width, box_y + crop_height), 
                                color, 4)
                    
                    # 멤버 이름 라벨 추가 (어떤 언어든 가능)
                    result_frame = put_korean_text(result_frame, member_name, 
                                                (box_x, box_y - 50), font_size=28, color=color)
                    
                    # 박스 내부에 반투명 색상 오버레이 (선택사항)
                    overlay = result_frame.copy()
                    cv2.rectangle(overlay, (box_x, box_y), (box_x + crop_width, box_y + crop_height), 
                                color, -1)
                    result_frame = cv2.addWeighted(result_frame, 0.95, overlay, 0.05, 0)
        
        out.write(result_frame)
        frame_idx += 1
        
        if frame_idx % 60 == 0:
            progress = (frame_idx / frame_count) * 100
            print(f"   {frame_idx}/{frame_count} frames ({progress:.1f}%)...")
    
    cap.release()
    out.release()
    print(f"✅ 전체 박스 영상 완료: {output_path}")

def select_video_file():
    #비디오 파일 선택
    print("비디오 파일 선택")
    print("=" * 50)
    
    # 현재 디렉토리의 비디오 파일 찾기
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    video_files = []
    
    try:
        for file in os.listdir('.'):
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_files.append(file)
    except:
        pass
    
    if video_files:
        print("현재 폴더의 비디오 파일:")
        for i, file in enumerate(video_files, 1):
            file_size = os.path.getsize(file) / (1024*1024)  # MB
            print(f"   {i}. {file} ({file_size:.1f} MB)")
        
        print(f"   {len(video_files) + 1}. 직접 파일 경로 입력")
        print("   q. 종료")
        
        while True: # 파일 선택 루프 
            try:
                choice = input(f"\n파일 선택 (1-{len(video_files) + 1}) 또는 'q': ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                choice_num = int(choice)
                # 선택된 번호가 유효한지 확인
                if 1 <= choice_num <= len(video_files):
                    selected_file = video_files[choice_num - 1]
                    print(f"선택된 파일: {selected_file}")
                    return selected_file
                
                elif choice_num == len(video_files) + 1:
                    # 직접 경로 입력
                    break
                
                else:
                    print(f"❌ 1~{len(video_files) + 1} 사이의 숫자를 입력하세요")
                    
            except ValueError:
                print("❌ 숫자를 입력하세요")
            except KeyboardInterrupt:
                print("\n❌ 취소되었습니다")
                return None
    
    # 직접 파일 경로 입력
    while True:
        try:
            file_path = input("\n비디오 파일 경로를 입력하세요: ").strip()
            
            if not file_path:
                print("❌ 파일 경로를 입력하세요")
                continue
            
            # 따옴표 제거 (드래그&드롭시 자동 추가되는 경우)
            file_path = file_path.strip('"').strip("'")
            
            if not os.path.exists(file_path):
                print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
                continue
            
            # 비디오 파일인지 확인
            if not any(file_path.lower().endswith(ext) for ext in video_extensions):
                print(f"❌ 지원되지 않는 파일 형식입니다")
                print(f"   지원 형식: {', '.join(video_extensions)}")
                continue
            
            # 파일 크기 확인
            file_size = os.path.getsize(file_path) / (1024*1024)  # MB
            print(f"✅ 선택된 파일: {file_path}")
            print(f"파일 크기: {file_size:.1f} MB")
            
            return file_path
            
        except KeyboardInterrupt:
            print("\n❌ 취소되었습니다")
            return None
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

def main():
    try:
        from scipy import interpolate
        from scipy.ndimage import gaussian_filter1d
        print("✅ SciPy 라이브러리 확인됨")
    except ImportError:
        print("❌ SciPy가 설치되지 않음. 설치 필요: pip install scipy")
        return
    
    print("멀티 아이돌 최적 카메라 시스템")
    print("=" * 80)
    
    # 비디오 파일 선택
    video_path = select_video_file()
    if not video_path:
        print("❌ 비디오 파일이 선택되지 않았습니다")
        return
    
    # 비디오 정보 확인
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ 비디오 파일을 열 수 없습니다: {video_path}")
        return
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    cap.release()
    
    # 설정
    model_path = "checkpoints/sam2.1_hiera_base_plus.pt"
    
    FIXED_CROP_WIDTH = 400 # 고정 크롭 너비
    FIXED_CROP_HEIGHT = 750 # 고정 크롭 높이
    
    print(f"해상도: {width}x{height}")
    print(f"영상 길이: {duration:.1f}초 ({frame_count} frames, {fps:.1f} fps)")
    print(f"Model: {model_path}")
    print(f"Crop Size: {FIXED_CROP_WIDTH}x{FIXED_CROP_HEIGHT}")
    print("출력:")
    print(" 1. 전체 영상 + 각 멤버 크롭 박스 표시")
    print(" 2. 각 멤버별 개인 최적화 크롭 영상")
    print("=" * 80)
    
    # Step 1: 멤버 선택 (이름 입력)
    print(f"\nStep 1: 멤버 선택 (이름 입력)")
    selected_members = select_multiple_members(video_path)
    
    if len(selected_members) == 0:
        print("❌ 선택된 멤버가 없습니다")
        return
    
    print(f"\n선택된 멤버: {len(selected_members)}명")
    
    # Step 2: 각 멤버별 추적 및 경로 계산
    all_camera_paths = {}
    temp_files = []
    
    for member_name, info in selected_members.items():
        print(f"\n🎬 {member_name} ({info['color_name']}) 처리 중...")
        
        # 바운딩박스 파일 생성
        bbox_file = f"{member_name}_bbox.txt"
        create_bbox_file(info['bbox'], bbox_file)
        temp_files.append(bbox_file)
        
        # 추적 실행
        tracked_file = f"{member_name}_tracked.mp4"
        print(f"SAMURAI 추적 중")
        
        if run_single_tracking(video_path, bbox_file, model_path, tracked_file):
            temp_files.append(tracked_file)
            
            # 경로 추출
            print(f"경로 추출 중")
            center_coords = extract_center_coords(tracked_file, video_path)
            
            # 최적 카메라 경로 계산
            print(f"최적 경로 계산 중")
            optimal_path = calculate_optimal_camera_path(center_coords, FIXED_CROP_WIDTH, FIXED_CROP_HEIGHT)
            all_camera_paths[member_name] = optimal_path
            
            # 개인 크롭 영상 생성
            crop_output = f"{member_name}_optimal_crop.mp4"
            create_optimal_cropped_video(video_path, optimal_path, crop_output, member_name, 
                                        FIXED_CROP_WIDTH, FIXED_CROP_HEIGHT)
        else:
            print(f"   ❌ {member_name} 추적 실패")
    
    # Step 3: 전체 영상에 크롭 박스 표시
    if len(all_camera_paths) > 0:
        print(f"\n전체 영상에 크롭 박스 표시 생성 중")
        create_full_view_with_crop_boxes(video_path, all_camera_paths, selected_members, 
                                        "Full_View_With_Crop_Boxes.mp4", 
                                        FIXED_CROP_WIDTH, FIXED_CROP_HEIGHT)
    
    # 임시 파일 정리
    print(f"\n임시 파일 정리 중")
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("\n" + "=" * 80)
    print("멀티 아이돌 카메라 시스템 완료!")
    print("생성된 영상:")
    print("Full_View_With_Crop_Boxes.mp4 (전체 + 크롭 박스)")
    for member_name in selected_members.keys():
        print(f"{member_name}_optimal_crop.mp4 (개인 크롭)")
    print("=" * 80)

if __name__ == "__main__":
    main()