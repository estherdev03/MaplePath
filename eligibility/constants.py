# constants.py

from enum import Enum

from graph.state.profile import EducationLevel

FSW_PASS_SCORE = 67


# Education (Max 25)
EDUCATION_POINTS = {
    EducationLevel.SECONDARY: 5,
    EducationLevel.ONE_YEAR: 15,
    EducationLevel.TWO_YEAR: 19,
    EducationLevel.BACHELOR: 21,
    EducationLevel.TWO_OR_MORE: 22,
    EducationLevel.MASTERS: 23,
    EducationLevel.PHD: 25,
}


# First Official Language
# Max 24 (6 per ability)
FIRST_LANGUAGE_POINTS = {
    10: 6,
    9: 6,
    8: 5,
    7: 4,
}


# Second Official Language
# Max 4
SECOND_LANGUAGE_MIN_CLB = 5
SECOND_LANGUAGE_POINTS = 4


# Skilled Work Experience
WORK_EXPERIENCE_POINTS = {
    1: 9,
    2: 11,
    3: 11,
    4: 13,
    5: 13,
    6: 15,  # 6+
}


# Age
AGE_POINTS = {
    18: 12,
    19: 12,
    20: 12,
    21: 12,
    22: 12,
    23: 12,
    24: 12,
    25: 12,
    26: 12,
    27: 12,
    28: 12,
    29: 12,
    30: 12,
    31: 12,
    32: 12,
    33: 12,
    34: 12,
    35: 12,
    36: 11,
    37: 10,
    38: 9,
    39: 8,
    40: 7,
    41: 6,
    42: 5,
    43: 4,
    44: 3,
    45: 2,
    46: 1,
}
# >=47 => 0


# Arranged Employment
ARRANGED_EMPLOYMENT_POINTS = 10


# Adaptability
ADAPTABILITY_MAX = 10
