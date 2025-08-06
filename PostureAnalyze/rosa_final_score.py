from typing import Dict

class ROSAFinalScorer:

    def __init__(self):
        self.final_score_table = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [2, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [3, 3, 3, 4, 5, 6, 7, 8, 9, 10],
            [4, 4, 4, 4, 5, 6, 7, 8, 9, 10],
            [5, 5, 5, 5, 5, 6, 7, 8, 9, 10],
            [6, 6, 6, 6, 6, 6, 7, 8, 9, 10],
            [7, 7, 7, 7, 7, 7, 7, 8, 9, 10],
            [8, 8, 8, 8, 8, 8, 8, 8, 9, 10],
            [9, 9, 9, 9, 9, 9, 9, 9, 9, 10],
            [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        ]

    def get_final_rosa_score(self, section_a_score: int, section_b_score: int, section_c_score: int) -> Dict[str, int]:
        b_c_combination_table = [
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [2, 2, 3, 4, 5, 6, 7, 8, 9],
            [3, 3, 3, 4, 5, 6, 7, 8, 9],
            [4, 4, 4, 4, 5, 6, 7, 8, 9],
            [5, 5, 5, 5, 5, 6, 7, 8, 9],
            [6, 6, 6, 6, 6, 6, 7, 8, 9],
            [7, 7, 7, 7, 7, 7, 7, 8, 9],
            [8, 8, 8, 8, 8, 8, 8, 8, 9],
            [9, 9, 9, 9, 9, 9, 9, 9, 9]
        ]

        row_b = max(0, min(section_b_score - 1, 8))
        col_c = max(0, min(section_c_score - 1, 8))
        combined_bc_score = b_c_combination_table[row_b][col_c]

        row_a = max(0, min(section_a_score - 1, 9))
        col_bc = max(0, min(combined_bc_score - 1, 9))
        final_score = self.final_score_table[row_a][col_bc]

        return {
            "section_a_score": section_a_score,
            "section_b_score": section_b_score,
            "section_c_score": section_c_score,
            "bc_combined_score": combined_bc_score,
            "final_rosa_score": final_score
        }