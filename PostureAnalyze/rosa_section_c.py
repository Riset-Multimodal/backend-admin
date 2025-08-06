from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SectionCMeasurements:
    reaching_to_mouse: bool
    pinch_grip_on_mouse: bool
    palmrest_in_front_of_mouse: bool
    mouse_keyboard_on_different_surfaces: bool
    mouse_duration_hours: float
    mouse_consecutive_minutes: float

    wrists_extended: bool
    deviation_while_typing: bool
    keyboard_too_high: bool
    reaching_to_overhead_items: bool
    keyboard_platform_non_adjustable: bool
    keyboard_duration_hours: float
    keyboard_consecutive_minutes: float


class ROSASectionC:

    def __init__(self):

        self.section_c_table = [
            [1, 1, 2, 3, 4, 5, 6, 7],
            [1, 1, 2, 3, 4, 5, 6, 7],
            [1, 2, 2, 3, 4, 5, 6, 7],
            [2, 3, 3, 4, 5, 6, 7, 8],
            [3, 4, 4, 5, 5, 6, 7, 8],
            [4, 5, 5, 6, 6, 7, 8, 9],
            [5, 6, 6, 7, 7, 8, 8, 9],
            [6, 7, 7, 8, 8, 9, 9, 9],
        ]

    def analyze_mouse(self, m: SectionCMeasurements) -> int:
        base_score = 2 if m.reaching_to_mouse else 1

        # Akumulasi semua skor penalti tambahan
        additional_score = 0
        if m.pinch_grip_on_mouse:
            additional_score += 1
        if m.palmrest_in_front_of_mouse:
            additional_score += 1
        if m.mouse_keyboard_on_different_surfaces:
            additional_score += 2

        posture_score = base_score + additional_score
        # duration_score = self._get_duration_score(m.mouse_duration_hours, m.mouse_consecutive_minutes)

        return posture_score

        # File: rosa_section_c.py

    def analyze_keyboard(self, m: SectionCMeasurements) -> int:
        base_score = 2 if m.wrists_extended else 1

        additional_score = 0
        if m.deviation_while_typing:
            additional_score += 1
        if m.keyboard_too_high:
            additional_score += 1
        if m.reaching_to_overhead_items:
            additional_score += 1
        if m.keyboard_platform_non_adjustable:
            additional_score += 1

        posture_score = base_score + additional_score

        return posture_score

    def calculate_final_c_score(self, measurements: SectionCMeasurements) -> Dict[str, int]:
        mouse_score = self.analyze_mouse(measurements)
        keyboard_score = self.analyze_keyboard(measurements)

        row_idx = max(0, min(mouse_score, 7))
        col_idx = max(0, min(keyboard_score, 7))

        final_score = self.section_c_table[row_idx][col_idx]

        return {
            "mouse_score": mouse_score,
            "keyboard_score": keyboard_score,
            "final_c_score": final_score
        }