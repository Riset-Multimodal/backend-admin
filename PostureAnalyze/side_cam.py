import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Optional

mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5)

def _calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle if angle <= 180.0 else 360 - angle

def _calculate_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def analyze_side_view(image: np.ndarray) -> Optional[Dict]:
    h, w, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose_detector.process(image_rgb)

    if not results.pose_landmarks:
        return None

    plm = results.pose_landmarks.landmark
    p = {
        'shoulder': (int(plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * h)),
        'elbow': (int(plm[mp_pose.PoseLandmark.RIGHT_ELBOW].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_ELBOW].y * h)),
        'wrist': (int(plm[mp_pose.PoseLandmark.RIGHT_WRIST].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_WRIST].y * h)),
        'hip': (int(plm[mp_pose.PoseLandmark.RIGHT_HIP].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_HIP].y * h)),
        'knee': (int(plm[mp_pose.PoseLandmark.RIGHT_KNEE].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_KNEE].y * h)),
        'ankle': (int(plm[mp_pose.PoseLandmark.RIGHT_ANKLE].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h)),
        'ear': (int(plm[mp_pose.PoseLandmark.RIGHT_EAR].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_EAR].y * h)),
        'nose': (int(plm[mp_pose.PoseLandmark.NOSE].x * w), int(plm[mp_pose.PoseLandmark.NOSE].y * h)),
        'index_finger': (int(plm[mp_pose.PoseLandmark.RIGHT_INDEX].x * w), int(plm[mp_pose.PoseLandmark.RIGHT_INDEX].y * h)),
    }

    knee_angle = _calculate_angle(p['hip'], p['knee'], p['ankle'])
    elbow_angle = _calculate_angle(p['shoulder'], p['elbow'], p['wrist'])
    recline_angle = 180 - _calculate_angle(p['shoulder'], p['hip'], p['knee'])
    feet_on_floor = p['ankle'][1] > (h * 0.95)
    monitor_too_low = p['nose'][1] > p['shoulder'][1]
    monitor_too_high = p['ear'][0] < p['shoulder'][0] - 20
    wrist_extension_angle = _calculate_angle(p['elbow'], p['wrist'], p['index_finger'])
    wrists_extended = wrist_extension_angle < 165
    shrugged_shoulders = _calculate_distance(p['ear'], p['shoulder']) < (h * 0.1)
    work_surface_too_high = shrugged_shoulders or (p['elbow'][1] < p['hip'][1] * 0.9)

    forearm_support_contact = False
    if 75 < elbow_angle < 115:
        armrest_y_position = p['elbow'][1] + (h * 0.03) # Sedikit di bawah siku
        height_tolerance = h * 0.05
        if abs(p['wrist'][1] - armrest_y_position) < height_tolerance:
            forearm_support_contact = True

    reaching_to_overhead_items = p['wrist'][1] < p['ear'][1]

    return {
        "knee_angle": knee_angle,
        "elbow_angle": elbow_angle,
        "recline_angle": recline_angle,
        "feet_on_floor": feet_on_floor,
        "monitor_too_low": monitor_too_low,
        "monitor_too_high": monitor_too_high,
        "wrists_extended": wrists_extended,
        "work_surface_too_high": work_surface_too_high,
        "keyboard_too_high": work_surface_too_high,
        "forearm_support_contact": forearm_support_contact,
        "reaching_to_overhead_items": reaching_to_overhead_items,
    }


# knee angle
#  no foot contact on ground
#  insuffienct space
#  approximately 3 inches
#  to o long - less than 3" of spcae
#  too short - more than 3" of space
# adequete lumbar support
# no lumbar support Or Lumbar suppport not oisioned in small of back
# anggled too far back or angle too far fowrward (less than 95)
# no back support
# hard damage/surface
# Arm length distance (40-75 cm)/ screen at eye level
# Too low (below 30 degree)
# to high (nect extensyon)
# glare on screen
# palmrest in front of mouse
# wrist straight shiulder relaxed
# wrist extended/keyboard on postitive angle




# Memerlukan Pengukuran 3D/Jarak Fisik:

# insufficient space

# approximately 3 inches

# too long - less than 3" of space

# too short - more than 3" of space

# Arm length distance (40-75 cm)

# Alasan: Kamera tidak bisa mengetahui jarak atau ukuran asli dalam "inci" atau "cm" tanpa adanya objek referensi atau sensor kedalaman (depth sensor).

# Memerlukan Inspeksi Fisik:

# adequate lumbar support

# no lumbar support

# hard/damaged surface

# Alasan: Ini adalah kualitas atau fitur dari kursi itu sendiri yang harus diperiksa secara langsung.

# Memerlukan Deteksi Objek/Lingkungan Tingkat Lanjut:

# glare on screen (silau)

# palmrest in front of mouse

# Alasan: Ini memerlukan analisis kondisi pencahayaan atau kemampuan untuk mengenali objek spesifik seperti "palmrest," yang berada di luar kemampuan MediaPipe Pose.