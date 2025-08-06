import cv2
import numpy as np
import pandas as pd
import logging
import time
from pathlib import Path
from dataclasses import asdict
from typing import Dict, Any, Optional
import pprint

from PostureAnalyze.front_cam import analyze_front_view
from PostureAnalyze.side_cam import analyze_side_view
from PostureAnalyze.overhead_cam import analyze_overhead_view
from PostureAnalyze.rosa_section_a import AdvancedROSASectionA, ChairMeasurements
from PostureAnalyze.rosa_section_b import ROSASectionB, SectionBMeasurements
from PostureAnalyze.rosa_section_c import ROSASectionC, SectionCMeasurements
from PostureAnalyze.rosa_final_score import ROSAFinalScorer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

section_a_model = AdvancedROSASectionA()
section_b_model = ROSASectionB()
section_c_model = ROSASectionC()
rosa_scorer = ROSAFinalScorer()


def convert_numpy_types(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
        return int(obj)
    if isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.bool_)):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_numpy_types(i) for i in obj]
    return obj


def save_to_csv(log_row: Dict, filename: str = "analysis_log.csv"):
    output_dir = Path("rosa_function_output")
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    log_row_cleaned = convert_numpy_types(log_row)

    df_new_row = pd.DataFrame([log_row_cleaned])
    header = not filepath.exists()
    df_new_row.to_csv(filepath, mode='a', header=header, index=False)
    logger.info(f"Log entry has been added to {filepath}")


def analyze_ergonomics_from_files(
        file_front: bytes,
        file_side: bytes,
        file_overhead: bytes,
        save_log: bool = False
) -> Optional[Dict]:
    try:
        print("--- DEBUG: Menjalankan versi kode TERBARU. Jika Anda melihat pesan ini, file sudah benar. ---")
        img_front = cv2.imdecode(np.frombuffer(file_front, np.uint8), cv2.IMREAD_COLOR)
        img_side = cv2.imdecode(np.frombuffer(file_side, np.uint8), cv2.IMREAD_COLOR)
        img_overhead = cv2.imdecode(np.frombuffer(file_overhead, np.uint8), cv2.IMREAD_COLOR)

        if img_front is None or img_side is None or img_overhead is None:
            logger.error("Gagal men-decode satu atau lebih file gambar dari data bytes.")
            return None

        front_data = analyze_front_view(img_front)
        side_data = analyze_side_view(img_side)
        overhead_data = analyze_overhead_view(img_overhead)

        # if not front_data or not side_data:
        #     logger.error("Pose could not be detected from front or side view.")
        #     return None

        metrics = {**(side_data or {}), **(front_data or {}), **(overhead_data or {})}

        chair_m = ChairMeasurements(
            knee_angle=metrics.get('knee_angle', 90.0),
            feet_on_floor=metrics.get('feet_on_floor', False),
            recline_angle=metrics.get('recline_angle', 100.0),
            elbow_angle=metrics.get('elbow_angle', 90.0),
            work_surface_too_high=metrics.get('work_surface_too_high', False),
            armrests_too_wide=metrics.get('armrests_too_wide', False),
            forearm_support_contact=metrics.get('forearm_support_contact', False),
            shoulder_elevation=metrics.get('has_shoulder_elevation', False),
            thigh_pressure=False,
            foot_contact_percentage=90.0 if metrics.get('feet_on_floor') else 0.0,
            gap_behind_knee=3.0,
            thigh_support_length=16.0,
            armrest_height_from_seat=8.5,
            armrest_surface_hard=False,
            armrest_adjustable=True,
            lumbar_contact=not (metrics.get('recline_angle', 100.0) < 95),
            lumbar_curve_match=85.0,
            back_contact_percentage=90.0 if metrics.get('lumbar_contact', False) else 10.0,
            backrest_adjustable=True,
            height_adjustable=True,
            pan_depth_adjustable=True,
            leg_room_width=24.0,
            knee_clearance=5.0
        )

        sec_b_m = SectionBMeasurements(
            monitor_too_low=metrics.get('monitor_too_low', False),
            monitor_too_high=metrics.get('monitor_too_high', False),
            use_neck_shoulder_hold=metrics.get('use_neck_shoulder_hold', False),
            has_neck_twist=metrics.get('has_neck_twist', False),
            no_hands_free=metrics.get('use_neck_shoulder_hold', False),
            monitor_too_far=False,
            has_glare=metrics.get('has_glare', False),
            no_doc_holder=True,
            monitor_consecutive_minutes=0,
            phone_too_far=False,
            phone_consecutive_minutes=0
        )

        sec_c_m = SectionCMeasurements(
            reaching_to_mouse=metrics.get('reaching_to_mouse', False),
            pinch_grip_on_mouse=metrics.get('pinch_grip_on_mouse', False),
            wrists_extended=metrics.get('wrists_extended', False),
            deviation_while_typing=metrics.get('deviation_while_typing', False),
            keyboard_too_high=metrics.get('keyboard_too_high', False),
            mouse_keyboard_on_different_surfaces=metrics.get('mouse_keyboard_on_different_surfaces', False),
            reaching_to_overhead_items=metrics.get('reaching_to_overhead_items', False),
            palmrest_in_front_of_mouse=False,
            mouse_duration_hours=0,
            mouse_consecutive_minutes=0,
            keyboard_platform_non_adjustable=False,
            keyboard_duration_hours=0,
            keyboard_consecutive_minutes=0
        )

        score_a = section_a_model.calculate_final_chair_score(chair_m)
        score_b = section_b_model.calculate_final_b_score(sec_b_m)
        score_c = section_c_model.calculate_final_c_score(sec_c_m)
        final_scores = rosa_scorer.get_final_rosa_score(
            score_a['final_score'], score_b['final_b_score'], score_c['final_c_score']
        )

        structured_result = {
            "chair_state": asdict(chair_m),
            "monitor_phone_state": asdict(sec_b_m),
            "mouse_keyboard_state": asdict(sec_c_m),
            "score_a_results": score_a,
            "score_b_results": score_b,
            "score_c_results": score_c,
            "final_scores": final_scores
        }

        flat_final_result = {}
        for key, value in structured_result.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    flat_final_result[f"{key}_{sub_key}"] = sub_value
            else:
                flat_final_result[key] = value

        if save_log:
            save_to_csv(flat_final_result)

        return convert_numpy_types(flat_final_result)

    except Exception as e:
        logger.error(f"An unexpected error occurred during analysis: {e}", exc_info=True)
        return None


if __name__ == '__main__':
    try:
        path_front = 'front_2.jpeg'
        path_side = 'side_2.jpeg'
        path_overhead = 'overhead_2.jpeg'

        with open(path_front, 'rb') as f:
            file_data_front = f.read()

        with open(path_side, 'rb') as f:
            file_data_side = f.read()

        with open(path_overhead, 'rb') as f:
            file_data_overhead = f.read()

        print("Menganalisis file gambar...")
        start_analysis_time = time.time()

        results = analyze_ergonomics_from_files(
            file_data_front,
            file_data_side,
            file_data_overhead,
            save_log=True
        )

        analysis_duration = time.time() - start_analysis_time
        print(f"Analisis selesai dalam {analysis_duration:.2f} detik.")

        if results:
            print("\n--- HASIL ANALISIS ROSA (FLAT) ---")
            pprint.pprint(results)
            print("----------------------------------\n")
            final_score = results.get("final_scores_final_rosa_score")
            print(f"Skor Final ROSA: {final_score}")
        else:
            print("\nAnalisis gagal. Silakan periksa log error di atas.")

    except FileNotFoundError:
        print(
            f"Error: Pastikan file 'sample_front.jpg', 'sample_side.jpg', dan 'sample_overhead.jpg' ada di folder yang sama.")
    except Exception as e:
        print(f"Terjadi error yang tidak terduga: {e}")