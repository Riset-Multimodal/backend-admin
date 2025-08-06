import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Optional

mp_pose = mp.solutions.pose
mp_hands = mp.solutions.hands
pose_detector = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5)
hands_detector = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5)


def _calculate_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def _get_body_proportions(landmarks, w, h):
    plm = landmarks
    shoulder_l = (plm[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w, plm[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)
    shoulder_r = (plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w, plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)
    hip_l = (plm[mp_pose.PoseLandmark.LEFT_HIP].x * w, plm[mp_pose.PoseLandmark.LEFT_HIP].y * h)
    hip_r = (plm[mp_pose.PoseLandmark.RIGHT_HIP].x * w, plm[mp_pose.PoseLandmark.RIGHT_HIP].y * h)
    shoulder_width = _calculate_distance(shoulder_l, shoulder_r)
    torso_height = (_calculate_distance(shoulder_l, hip_l) + _calculate_distance(shoulder_r, hip_r)) / 2
    return {'shoulder_width': shoulder_width, 'torso_height': torso_height}


def _detect_glare_in_roi(image: np.ndarray, roi: tuple) -> bool:
    """Mendeteksi area sangat terang di dalam Region of Interest (ROI)."""
    (x, y, w, h) = roi

    # <<< PERBAIKAN: Pastikan semua nilai adalah integer sebelum digunakan untuk slicing >>>
    x, y, w, h = int(x), int(y), int(w), int(h)

    # Pastikan ROI tidak keluar dari batas gambar
    x, y = max(0, x), max(0, y)
    img_roi = image[y:y + h, x:x + w]

    if img_roi.size == 0:
        return False

    gray_roi = cv2.cvtColor(img_roi, cv2.COLOR_BGR2GRAY)

    # Cari piksel yang sangat terang (mendekati putih murni)
    _, thresh = cv2.threshold(gray_roi, 245, 255, cv2.THRESH_BINARY)

    # Hitung persentase piksel terang di ROI
    bright_pixels = cv2.countNonZero(thresh)
    total_pixels = img_roi.shape[0] * img_roi.shape[1]

    if total_pixels == 0:
        return False

    bright_ratio = bright_pixels / total_pixels

    # Jika ada area terang yang signifikan (tidak terlalu kecil, tidak terlalu besar)
    if 0.005 < bright_ratio < 0.2:
        return True

    return False


# ... (sisa kode di front_cam.py tidak perlu diubah)

def analyze_front_view(image: np.ndarray) -> Optional[Dict]:
    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pose_results = pose_detector.process(image_rgb)
    hands_results = hands_detector.process(image_rgb)

    if not pose_results.pose_landmarks:
        return None

    plm = pose_results.pose_landmarks.landmark
    props = _get_body_proportions(plm, w, h)

    elbow_l = (plm[mp_pose.PoseLandmark.LEFT_ELBOW].x * w, plm[mp_pose.PoseLandmark.LEFT_ELBOW].y * h)
    elbow_r = (plm[mp_pose.PoseLandmark.RIGHT_ELBOW].x * w, plm[mp_pose.PoseLandmark.RIGHT_ELBOW].y * h)
    elbow_distance = _calculate_distance(elbow_l, elbow_r)
    armrests_too_wide = elbow_distance > (props['shoulder_width'] * 1.5)

    wrist_r_pt = (plm[mp_pose.PoseLandmark.RIGHT_WRIST].x * w, plm[mp_pose.PoseLandmark.RIGHT_WRIST].y * h)
    shoulder_r_pt = (plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w, plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)
    reaching_to_mouse = wrist_r_pt[0] > (shoulder_r_pt[0] + props['shoulder_width'] * 0.5)

    neck_shoulder_hold = False
    if hands_results.multi_hand_landmarks:
        head_y = (plm[mp_pose.PoseLandmark.NOSE].y * h)
        for hand_landmarks in hands_results.multi_hand_landmarks:
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * h
            if wrist_y < head_y:
                neck_shoulder_hold = True
                break

    nose_pt = (plm[mp_pose.PoseLandmark.NOSE].x * w, plm[mp_pose.PoseLandmark.NOSE].y * h)
    shoulder_l_pt = (plm[mp_pose.PoseLandmark.LEFT_SHOULDER].x * w, plm[mp_pose.PoseLandmark.LEFT_SHOULDER].y * h)
    shoulder_r_pt = (plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w, plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)
    shoulder_mid_x = (shoulder_l_pt[0] + shoulder_r_pt[0]) / 2

    twist_threshold = props['shoulder_width'] * 0.15
    has_neck_twist = abs(nose_pt[0] - shoulder_mid_x) > twist_threshold

    wrist_l_pt = (plm[mp_pose.PoseLandmark.LEFT_WRIST].x * w, plm[mp_pose.PoseLandmark.LEFT_WRIST].y * h)
    nose_y = nose_pt[1]
    reaching_to_overhead_items = (wrist_l_pt[1] < nose_y) or (wrist_r_pt[1] < nose_y)

    roi_x = shoulder_r_pt[0]
    roi_y = 0  # Mulai dari atas gambar
    roi_w = int(props['shoulder_width'] * 2)
    roi_h = int(h * 0.75)  # Hingga 75% tinggi gambar
    glare_roi = (roi_x, roi_y, roi_w, roi_h)
    has_glare = _detect_glare_in_roi(image.copy(), glare_roi)

    dy = shoulder_l_pt[1] - shoulder_r_pt[1]  # Perbedaan tinggi vertikal
    dx = shoulder_l_pt[0] - shoulder_r_pt[0]  # Perbedaan horizontal
    # Hindari pembagian dengan nol jika bahu sejajar vertikal (tidak mungkin secara praktis)
    if dx == 0:
        dx = 1e-6
    # Hitung sudut dalam derajat
    shoulder_elevation_angle = abs(np.degrees(np.arctan2(dy, dx)))
    # Kita anggap ada elevasi signifikan jika kemiringan lebih dari 3 derajat
    has_shoulder_elevation = shoulder_elevation_angle > 3.0

    return {
        "armrests_too_wide": armrests_too_wide,
        "reaching_to_mouse": reaching_to_mouse,
        "use_neck_shoulder_hold": neck_shoulder_hold,
        "has_neck_twist": has_neck_twist,
        "reaching_to_overhead_items": reaching_to_overhead_items,
        "has_glare": has_glare,
        "has_shoulder_elevation": has_shoulder_elevation
    }
# elbow supported in line with shoulder
# too high shoulders/low
# too wide armrests
# work surface too high
# Too far of reach mouse,
# nect and shoukder hold
# headset/one hand on phone
# mouse in line with shoulder
# Reaching to mouse
# MOuse/keybaord on different surface
# pinch grip on mouse
# keyboard too high


# Not Feasible (Tidak Bisa Dideteksi dari Depan):

# Mouse/keyboard on different surface: Ini memerlukan informasi kedalaman (depth) yang tidak kita miliki dari gambar 2D. Jadi, ini akan selalu dikembalikan sebagai False.


