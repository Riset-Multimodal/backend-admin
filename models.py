from sqlalchemy import Column, Integer, Float
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

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
