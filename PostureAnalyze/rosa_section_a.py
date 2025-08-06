import math
import numpy as np
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum


class PostureType(Enum):
    NEUTRAL = "neutral"
    TOO_HIGH = "too_high"
    TOO_LOW = "too_low"
    NO_CONTACT = "no_contact"
    HARD_SURFACE = "hard_surface"
    TOO_WIDE = "too_wide"


@dataclass
class ChairMeasurements:
    knee_angle: float  # sudut lutut (derajat)
    thigh_pressure: bool  # ngecek ada tekanan di bawah paha atau ngga
    feet_on_floor: bool  # kakinya napak ke lantai apa ngga
    foot_contact_percentage: float  # berapa persen telapak kaki yang napak

    gap_behind_knee: float  # jarak antara belakang lutut sama ujung kursi (inci)
    thigh_support_length: float  # panjang paha yang ditopang kursi (inci)

    elbow_angle: float  # sudut siku (derajat)
    shoulder_elevation: float  # bahunya keangkat atau turun (derajat dari posisi netral)
    forearm_support_contact: bool  # lengan bawahnya nyentuh sandaran apa ngga
    armrest_height_from_seat: float  # tinggi sandaran tangan dari dudukan (inci)

    armrests_too_wide: bool  # True jika terlalu lebar
    armrest_surface_hard: bool  # True jika permukaan keras/rusak
    armrest_adjustable: bool  # True jika bisa diatur

    lumbar_contact: bool  # bagian pinggangnya kesentuh sandaran apa ngga
    lumbar_curve_match: float  # seberapa pas sandaran sama lekuk pinggang (0-100%)
    recline_angle: float  # sudut sandaran (derajat dari posisi vertikal)
    back_contact_percentage: float  # berapa persen punggung yang nempel sandaran
    backrest_adjustable: bool
    work_surface_too_high: bool  # Untuk penalti +1

    height_adjustable: bool
    pan_depth_adjustable: bool
    armrest_adjustable: bool
    backrest_adjustable: bool

    knee_clearance: float  # sisa ruang buat lutut di bawah meja (inci)
    leg_room_width: float  # lebar ruang buat kaki


class AdvancedROSASectionA:

    def __init__(self):
        self.rosa_scoring_table = [
            [1, 2, 3, 4, 5, 6, 7, 8],
            [2, 2, 3, 4, 5, 6, 7, 8],
            [3, 3, 3, 4, 5, 7, 7, 8],
            [4, 4, 4, 4, 5, 7, 7, 8],
            [5, 5, 5, 5, 6, 7, 8, 9],
            [6, 6, 6, 6, 6, 7, 8, 9],
            [7, 7, 7, 7, 7, 8, 8, 9]
        ]

    def analyze_chair_height(self, measurements: ChairMeasurements) -> int:

        base_score = 1  # posisi netral

        if measurements.knee_angle > 95:
            base_score = 2
        elif measurements.knee_angle < 85:
            base_score = 2
        elif not measurements.feet_on_floor:
            base_score = 3

        additional_score = 0

        if measurements.knee_clearance < 3.0:
            additional_score += 1

        if not measurements.height_adjustable:
            additional_score += 1

        return base_score + additional_score

    def analyze_pan_depth(self, measurements: ChairMeasurements) -> int:
        base_score = 1  # posisi netral
        if measurements.gap_behind_knee < 2.0:
            # "Seat pan depth - too long" - kurang dari 2-3 inci
            base_score = 2
        elif measurements.gap_behind_knee > 4.0:
            # "Seat pan depth - too short" - lebih dari 2-3 inci
            base_score = 2
        additional_score = 0
        if not measurements.pan_depth_adjustable:
            additional_score += 1
        return base_score + additional_score

    def analyze_armrest(self, measurements: ChairMeasurements) -> int:
        base_score = 1
        if measurements.shoulder_elevation > 15 or measurements.elbow_angle > 110 or measurements.elbow_angle < 70:
            # Mencakup "Too High (Shoulders Shrugged)" atau "Low (Arms Unsupported)"
            base_score = 2
        additional_score = 0
        if measurements.armrests_too_wide:
            additional_score += 1
        if measurements.armrest_surface_hard:
            additional_score += 1
        return base_score + additional_score

    def analyze_backrest(self, measurements: ChairMeasurements) -> int:
        base_score = 1

        is_lumbar_unsupported = not measurements.lumbar_contact
        is_recline_off = measurements.recline_angle < 95 or measurements.recline_angle > 110
        is_leaning_forward = measurements.back_contact_percentage < 50

        if is_lumbar_unsupported or is_recline_off or is_leaning_forward:
            base_score = 2

        additional_score = 0
        if measurements.work_surface_too_high:
            additional_score += 1  # Penalti untuk meja kerja terlalu tinggi

        return base_score + additional_score

    def calculate_final_chair_score(self, measurements: ChairMeasurements) -> Dict[str, int]:

        height_score = self.analyze_chair_height(measurements)
        depth_score = self.analyze_pan_depth(measurements)
        armrest_score = self.analyze_armrest(measurements)
        backrest_score = self.analyze_backrest(measurements)

        seat_pan_score = height_score + depth_score
        arms_back_score = armrest_score + backrest_score

        row_index = min(len(self.rosa_scoring_table) - 1, max(0, seat_pan_score - 2))
        col_index = min(len(self.rosa_scoring_table[0]) - 1, max(0, arms_back_score - 2))

        chair_base_score = self.rosa_scoring_table[row_index][col_index]

        # Skor akhir (tanpa faktor durasi)
        final_score = chair_base_score

        # Pastikan skor dalam rentang 1-10
        final_score = max(1, min(final_score, 10))

        return {
            'height_score': height_score,
            'depth_score': depth_score,
            'armrest_score': armrest_score,
            'backrest_score': backrest_score,
            'seat_pan_axis': seat_pan_score,
            'arms_back_axis': arms_back_score,
            'chair_base_score': chair_base_score,
            'final_score': final_score
        }