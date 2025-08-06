from dataclasses import dataclass
from typing import Dict, List

@dataclass
class SectionBMeasurements:

    monitor_too_high: bool
    monitor_too_low: bool
    monitor_too_far: bool
    has_neck_twist: bool
    has_glare: bool
    no_doc_holder: bool
    monitor_consecutive_minutes: float

    phone_too_far: bool
    use_neck_shoulder_hold: bool
    no_hands_free: bool
    phone_consecutive_minutes: float


class ROSASectionB:

    def __init__(self):

        self.section_b_table = [

            [1, 1, 1, 2, 3, 4, 5, 6],  # <-- BARIS INI TELAH DIPERBAIKI
            [1, 1, 2, 2, 3, 4, 5, 6],
            [1, 2, 2, 3, 3, 4, 6, 7],
            [2, 2, 3, 3, 4, 5, 6, 8],
            [3, 3, 4, 4, 5, 6, 7, 8],
            [4, 4, 5, 5, 6, 7, 8, 9],
            [5, 5, 6, 7, 8, 8, 9, 9],
        ]


    def analyze_monitor(self, m: SectionBMeasurements) -> int:
        if m.monitor_too_high:
            base_score = 3
        elif m.monitor_too_low:
            base_score = 2
        else:
            base_score = 1

        additional_score = 0
        if m.monitor_too_far:
            additional_score += 1
        if m.has_neck_twist:
            additional_score += 1
        if m.has_glare:
            additional_score += 1
        if m.no_doc_holder:
            additional_score += 1

        posture_score = base_score + additional_score


        return posture_score
    def analyze_telephone(self, m: SectionBMeasurements) -> int:
        if m.phone_too_far:
            base_score = 2
        else:
            base_score = 1

        additional_score = 0
        if m.use_neck_shoulder_hold:
            additional_score += 2 # Penalti +2
        if m.no_hands_free:
            additional_score += 1

        posture_score = base_score + additional_score


        return posture_score

    def calculate_final_b_score(self, measurements: SectionBMeasurements) -> Dict[str, int]:
        monitor_score = self.analyze_monitor(measurements)
        phone_score = self.analyze_telephone(measurements)

        row_idx = max(0, min(phone_score, 6))
        col_idx = max(0, min(monitor_score, 7))

        final_score = self.section_b_table[row_idx][col_idx]

        return {
            "monitor_score": monitor_score,
            "phone_score": phone_score,
            "final_b_score": final_score
        }