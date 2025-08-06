import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Optional, List

mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5)


def analyze_overhead_view(image: np.ndarray) -> Optional[Dict]:
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(image_rgb)

    if not results.multi_hand_landmarks:
        return None

    all_hands_data = []
    for hand_landmarks in results.multi_hand_landmarks:
        landmarks_list = [{'x': lm.x, 'y': lm.y} for lm in hand_landmarks.landmark]
        all_hands_data.append(landmarks_list)

    # Asumsi: tangan kanan adalah untuk mouse, tangan kiri untuk keyboard
    # Logika ini bisa disempurnakan jika ada cara membedakan tangan

    pinch_grip_on_mouse = False
    deviation_while_typing = False

    # Analisis Pinch Grip (biasanya pada satu tangan)
    for hand in all_hands_data:
        thumb_tip = hand[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = hand[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        distance = np.sqrt((thumb_tip['x'] - index_tip['x']) ** 2 + (thumb_tip['y'] - index_tip['y']) ** 2)
        if distance < 0.05:  # Heuristik untuk pinch grip
            pinch_grip_on_mouse = True
            break  # Cukup deteksi sekali

    # Analisis Deviasi Pergelangan Tangan (biasanya saat mengetik)
    for hand in all_hands_data:
        wrist = hand[mp_hands.HandLandmark.WRIST]
        mcp_middle = hand[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
        # Vektor dari pergelangan tangan ke tengah telapak
        wrist_to_mcp_x = mcp_middle['x'] - wrist['x']
        # Jika deviasinya signifikan ke samping
        if abs(wrist_to_mcp_x) > 0.04:  # Heuristik untuk deviasi
            deviation_while_typing = True
            break  # Cukup deteksi sekali

    # Analisis Permukaan Berbeda
    mouse_keyboard_on_different_surfaces = False
    if len(all_hands_data) == 2:
        wrist1_y = all_hands_data[0][mp_hands.HandLandmark.WRIST]['y']
        wrist2_y = all_hands_data[1][mp_hands.HandLandmark.WRIST]['y']
        # Jika perbedaan ketinggian (sumbu y) signifikan
        if abs(wrist1_y - wrist2_y) > 0.1:  # Heuristik utk perbedaan ketinggian
            mouse_keyboard_on_different_surfaces = True

    # Mengembalikan kamus yang bersih dan sesuai
    return {
        "pinch_grip_on_mouse": pinch_grip_on_mouse,
        "deviation_while_typing": deviation_while_typing,
        "mouse_keyboard_on_different_surfaces": mouse_keyboard_on_different_surfaces
    }