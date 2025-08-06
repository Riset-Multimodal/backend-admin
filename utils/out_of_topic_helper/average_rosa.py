import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from statistics import mean
from models import Posture

# Koneksi database
DB_URL = "postgresql://postgres:123@proxy.bccdev.id:11015/riset_db"
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)

# Urutan kolom sesuai request
FEATURE_ORDER = [
    "chair_state_knee_angle", "chair_state_thigh_pressure", "chair_state_feet_on_floor",
    "chair_state_foot_contact_percentage", "chair_state_gap_behind_knee", "chair_state_thigh_support_length",
    "chair_state_elbow_angle", "chair_state_shoulder_elevation", "chair_state_forearm_support_contact",
    "chair_state_armrest_height_from_seat", "chair_state_armrests_too_wide", "chair_state_armrest_surface_hard",
    "chair_state_armrest_adjustable", "chair_state_lumbar_contact", "chair_state_lumbar_curve_match",
    "chair_state_recline_angle", "chair_state_back_contact_percentage", "chair_state_backrest_adjustable",
    "chair_state_work_surface_too_high", "chair_state_height_adjustable", "chair_state_pan_depth_adjustable",
    "chair_state_knee_clearance", "chair_state_leg_room_width", "monitor_phone_state_monitor_too_high",
    "monitor_phone_state_monitor_too_low", "monitor_phone_state_monitor_too_far", "monitor_phone_state_has_neck_twist",
    "monitor_phone_state_has_glare", "monitor_phone_state_no_doc_holder", "monitor_phone_state_monitor_consecutive_minutes",
    "monitor_phone_state_phone_too_far", "monitor_phone_state_use_neck_shoulder_hold", "monitor_phone_state_no_hands_free",
    "monitor_phone_state_phone_consecutive_minutes", "mouse_keyboard_state_reaching_to_mouse",
    "mouse_keyboard_state_pinch_grip_on_mouse", "mouse_keyboard_state_palmrest_in_front_of_mouse",
    "mouse_keyboard_state_mouse_keyboard_on_different_surfaces", "mouse_keyboard_state_mouse_duration_hours",
    "mouse_keyboard_state_mouse_consecutive_minutes", "mouse_keyboard_state_wrists_extended",
    "mouse_keyboard_state_deviation_while_typing", "mouse_keyboard_state_keyboard_too_high",
    "mouse_keyboard_state_reaching_to_overhead_items", "mouse_keyboard_state_keyboard_platform_non_adjustable",
    "mouse_keyboard_state_keyboard_duration_hours", "mouse_keyboard_state_keyboard_consecutive_minutes",
    "score_a_results_height_score", "score_a_results_depth_score", "score_a_results_armrest_score",
    "score_a_results_backrest_score", "score_a_results_seat_pan_axis", "score_a_results_arms_back_axis",
    "score_a_results_chair_base_score", "score_a_results_final_score", "score_b_results_monitor_score",
    "score_b_results_phone_score", "score_b_results_final_b_score", "score_c_results_mouse_score",
    "score_c_results_keyboard_score", "score_c_results_final_c_score", "final_scores_section_a_score",
    "final_scores_section_b_score", "final_scores_section_c_score", "final_scores_bc_combined_score",
    "final_scores_final_rosa_score"
]

def average_posture_per_email(output_file="posture_avg.jsonl"):
    session = Session()
    try:
        all_data = session.query(Posture).all()

        # Group by user_email
        grouped = {}
        for p in all_data:
            email = p.user_email
            if email not in grouped:
                grouped[email] = []
            grouped[email].append(p)

        # Compute averages
        with open(output_file, "w", encoding="utf-8") as f:
            for email, records in grouped.items():
                avg_row = {"user_id": email}  # rename user_email → user_id

                for col in FEATURE_ORDER:
                    col_type = Posture.__table__.columns[col].type.python_type
                    values = [getattr(r, col) for r in records if getattr(r, col) is not None]

                    if not values:
                        avg_row[col] = None
                        continue

                    if col_type is bool:
                        # Persentase True
                        avg_row[col] = sum(1 for v in values if v) / len(values)
                    else:
                        # Rata-rata numerik
                        avg_row[col] = mean(values)

                f.write(json.dumps(avg_row, ensure_ascii=False) + "\n")

        print(f"✅ File tersimpan di {output_file}")

    finally:
        session.close()

if __name__ == "__main__":
    average_posture_per_email("posture_avg.jsonl")
