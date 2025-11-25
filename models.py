from datetime import datetime

from sqlalchemy import Column, Integer, Float, Index
from sqlalchemy.ext.declarative import declarative_base
import enum

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

class Keylog(Base):
    __tablename__ = 'keylog'

    id = Column(Integer, primary_key=True)
    user_email = Column(String)
    created_at = Column(DateTime)
    type = Column(String)
    keystroke_count = Column(Integer)
    left_click_count = Column(Integer)
    right_click_count = Column(Integer)
    scroll_up = Column(Integer)
    scroll_down = Column(Integer)
    space_count = Column(Integer)
    error_rate = Column(Float)
    mean_dwell_time_ms = Column(Float)
    std_dev_dwell_time_ms = Column(Float)
    mean_flight_time_ms = Column(Float)
    std_dev_flight_time_ms = Column(Float)
    mean_digraph_time_ms = Column(Float)
    std_dev_digraph_time_ms = Column(Float)
    pause_count = Column(Integer)
    mean_pause_duration_ms = Column(Float)
    mean_burst_length = Column(Float)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


from sqlalchemy import Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Posture(Base):
    __tablename__ = 'posture'

    id = Column(Integer, primary_key=True)
    user_email = Column(String)
    timestamp = Column(DateTime)

    front_image_link = Column(String)
    side_image_link = Column(String)
    overhead_image_link = Column(String)

    # Chair state
    chair_state_armrest_adjustable = Column(Boolean)
    chair_state_armrest_height_from_seat = Column(Float)
    chair_state_armrest_surface_hard = Column(Boolean)
    chair_state_armrests_too_wide = Column(Boolean)
    chair_state_back_contact_percentage = Column(Float)
    chair_state_backrest_adjustable = Column(Boolean)
    chair_state_elbow_angle = Column(Float)
    chair_state_feet_on_floor = Column(Boolean)
    chair_state_foot_contact_percentage = Column(Float)
    chair_state_forearm_support_contact = Column(Boolean)
    chair_state_gap_behind_knee = Column(Float)   # ← di DB double precision, jadi Float
    chair_state_height_adjustable = Column(Boolean)
    chair_state_knee_angle = Column(Float)
    chair_state_knee_clearance = Column(Float)    # ← di DB double precision, jadi Float
    chair_state_leg_room_width = Column(Float)
    chair_state_lumbar_contact = Column(Boolean)
    chair_state_lumbar_curve_match = Column(Float) # ← di DB double precision, jadi Float
    chair_state_pan_depth_adjustable = Column(Boolean)
    chair_state_recline_angle = Column(Float)
    chair_state_shoulder_elevation = Column(Boolean)
    chair_state_thigh_pressure = Column(Boolean)
    chair_state_thigh_support_length = Column(Float)
    chair_state_work_surface_too_high = Column(Boolean)

    # Final scores
    final_scores_bc_combined_score = Column(Integer)
    final_scores_final_rosa_score = Column(Integer)
    final_scores_section_a_score = Column(Integer)
    final_scores_section_b_score = Column(Integer)
    final_scores_section_c_score = Column(Integer)

    # Monitor / Phone state
    monitor_phone_state_has_glare = Column(Boolean)
    monitor_phone_state_has_neck_twist = Column(Boolean)
    monitor_phone_state_monitor_consecutive_minutes = Column(Integer)
    monitor_phone_state_monitor_too_far = Column(Boolean)
    monitor_phone_state_monitor_too_high = Column(Boolean)
    monitor_phone_state_monitor_too_low = Column(Boolean)
    monitor_phone_state_no_doc_holder = Column(Boolean)
    monitor_phone_state_no_hands_free = Column(Boolean)
    monitor_phone_state_phone_consecutive_minutes = Column(Integer)
    monitor_phone_state_phone_too_far = Column(Boolean)
    monitor_phone_state_use_neck_shoulder_hold = Column(Boolean)

    # Mouse / Keyboard state
    mouse_keyboard_state_deviation_while_typing = Column(Boolean)
    mouse_keyboard_state_keyboard_consecutive_minutes = Column(Integer)
    mouse_keyboard_state_keyboard_duration_hours = Column(Integer)
    mouse_keyboard_state_keyboard_platform_non_adjustable = Column(Boolean)
    mouse_keyboard_state_keyboard_too_high = Column(Boolean)
    mouse_keyboard_state_mouse_consecutive_minutes = Column(Integer)
    mouse_keyboard_state_mouse_duration_hours = Column(Integer)
    mouse_keyboard_state_mouse_keyboard_on_different_surfaces = Column(Boolean)
    mouse_keyboard_state_palmrest_in_front_of_mouse = Column(Boolean)
    mouse_keyboard_state_pinch_grip_on_mouse = Column(Boolean)
    mouse_keyboard_state_reaching_to_mouse = Column(Boolean)
    mouse_keyboard_state_reaching_to_overhead_items = Column(Boolean)
    mouse_keyboard_state_wrists_extended = Column(Boolean)

    # Score A results
    score_a_results_armrest_score = Column(Integer)
    score_a_results_arms_back_axis = Column(Integer)
    score_a_results_backrest_score = Column(Integer)
    score_a_results_chair_base_score = Column(Integer)
    score_a_results_depth_score = Column(Integer)
    score_a_results_final_score = Column(Integer)
    score_a_results_height_score = Column(Integer)
    score_a_results_seat_pan_axis = Column(Integer)

    # Score B results
    score_b_results_final_b_score = Column(Integer)
    score_b_results_monitor_score = Column(Integer)
    score_b_results_phone_score = Column(Integer)

    # Score C results
    score_c_results_final_c_score = Column(Integer)
    score_c_results_keyboard_score = Column(Integer)
    score_c_results_mouse_score = Column(Integer)

    def as_dict(self):
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

class User(Base):
    __tablename__ = 'users'

    user_email = Column(String, primary_key=True)
    faculty = Column(String)
    name = Column(String)
    created_at = Column(DateTime)

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class TlxFactor(enum.Enum):
    mental = "mental"
    physical = "physical"
    temporal = "temporal"
    performance = "performance"
    effort = "effort"
    frustration = "frustration"

# biar Alembic yang mengelola create/drop type
TlxFactorEnum = PGEnum(TlxFactor, name="tlx_factor", create_type=False)

class TlxResponse(Base):
    __tablename__ = "tlx_response"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_email: Mapped[str] = mapped_column(
        String,                                           # ← tipe DULU
        ForeignKey("users.user_email", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # pasangan
    pair_q1:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q2:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q3:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q4:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q5:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q6:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q7:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q8:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q9:  Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q10: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q11: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q12: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q13: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q14: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)
    pair_q15: Mapped[TlxFactor] = mapped_column(TlxFactorEnum, nullable=False)

    # likert 1..10 (ingat: SmallInteger + constraint)
    likert_mental:          Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_physical:        Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_temporal:        Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_performance_raw: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_effort:          Mapped[int] = mapped_column(SmallInteger, nullable=False)
    likert_frustration:     Mapped[int] = mapped_column(SmallInteger, nullable=False)

    __table_args__ = (
        CheckConstraint("likert_mental BETWEEN 1 AND 100", name="ck_likert_mental"),
        CheckConstraint("likert_physical BETWEEN 1 AND 100", name="ck_likert_physical"),
        CheckConstraint("likert_temporal BETWEEN 1 AND 100", name="ck_likert_temporal"),
        CheckConstraint("likert_performance_raw BETWEEN 1 AND 100", name="ck_likert_performance_raw"),
        CheckConstraint("likert_effort BETWEEN 1 AND 100", name="ck_likert_effort"),
        CheckConstraint("likert_frustration BETWEEN 1 AND 100", name="ck_likert_frustration"),
        # kalau sudah pakai index=True di kolom, HAPUS index manual ini agar tidak dobel
        # Index("idx_tlx_response_user_email", "user_email"),
    )

    @property
    def likert_performance(self) -> int:
        return 11 - int(self.likert_performance_raw)

class NordicBodymapResponse(Base):
    """
    1 row = 1 kali pengisian Nordic Body Map.
    Kolom nbm_0..nbm_26 = tingkat keluhan (1..4) sesuai urutan di FE:
      0  leher atas
      1  leher bawah
      2  bahu kiri
      3  bahu kanan
      4  lengan atas kiri
      5  punggung
      6  lengan atas kanan
      7  pinggang
      8  bokong
      9  pantat
      10 siku kiri
      11 siku kanan
      12 lengan bawah kiri
      13 lengan bawah kanan
      14 pergelangan tangan kiri
      15 pergelangan tangan kanan
      16 tangan kiri
      17 tangan kanan
      18 paha kiri
      19 paha kanan
      20 lutut kiri
      21 lutut kanan
      22 betis kiri
      23 betis kanan
      24 pergelangan kaki kiri
      25 pergelangan kaki kanan
      26 kaki kiri
    (Jika kamu butuh “kaki kanan” terpisah, tambah nbm_27; tabel di gambar berhenti di 26.)
    """

    __tablename__ = "nordic_bodymap_response"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    from sqlalchemy import String, ForeignKey

    user_email: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.user_email", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # 27 area (skala 1..4)
    nbm_0:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # leher atas
    nbm_1:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # leher bawah
    nbm_2:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # bahu kiri
    nbm_3:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # bahu kanan
    nbm_4:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan atas kiri
    nbm_5:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # punggung
    nbm_6:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan atas kanan
    nbm_7:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pinggang
    nbm_8:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # bokong
    nbm_9:  Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pantat
    nbm_10: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # siku kiri
    nbm_11: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # siku kanan
    nbm_12: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan bawah kiri
    nbm_13: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lengan bawah kanan
    nbm_14: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan tangan kiri
    nbm_15: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan tangan kanan
    nbm_16: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # tangan kiri
    nbm_17: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # tangan kanan
    nbm_18: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # paha kiri
    nbm_19: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # paha kanan
    nbm_20: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lutut kiri
    nbm_21: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # lutut kanan
    nbm_22: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # betis kiri
    nbm_23: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # betis kanan
    nbm_24: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan kaki kiri
    nbm_25: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # pergelangan kaki kanan
    nbm_26: Mapped[int] = mapped_column(SmallInteger, nullable=False)  # kaki kiri

    __table_args__ = (
        # validasi skala 1..4 untuk semua kolom
        CheckConstraint("nbm_0  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_1  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_2  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_3  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_4  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_5  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_6  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_7  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_8  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_9  BETWEEN 1 AND 4"),
        CheckConstraint("nbm_10 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_11 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_12 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_13 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_14 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_15 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_16 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_17 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_18 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_19 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_20 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_21 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_22 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_23 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_24 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_25 BETWEEN 1 AND 4"),
        CheckConstraint("nbm_26 BETWEEN 1 AND 4"),
        Index("idx_nbm_response_user_email", "user_email"),
    )

    # helper opsional
    @property
    def total_score(self) -> int:
        return sum(
            getattr(self, f"nbm_{i}", 0) for i in range(0, 26)
        )
