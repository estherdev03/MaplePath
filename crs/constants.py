from graph.state.profile import EducationLevel

AGE_POINTS_SINGLE = {
    17: 0,
    18: 99,
    19: 105,
    20: 110,
    21: 110,
    22: 110,
    23: 110,
    24: 110,
    25: 110,
    26: 110,
    27: 110,
    28: 110,
    29: 110,
    30: 105,
    31: 99,
    32: 94,
    33: 88,
    34: 83,
    35: 77,
    36: 72,
    37: 66,
    38: 61,
    39: 55,
    40: 50,
    41: 39,
    42: 28,
    43: 17,
    44: 6,
}

AGE_POINTS_MARRIED = {
    18: 90,
    19: 95,
    20: 100,
    21: 100,
    22: 100,
    23: 100,
    24: 100,
    25: 100,
    26: 100,
    27: 100,
    28: 100,
    29: 100,
    30: 95,
    31: 90,
    32: 85,
    33: 80,
    34: 75,
    35: 70,
    36: 65,
    37: 60,
    38: 55,
    39: 50,
    40: 45,
    41: 35,
    42: 25,
    43: 15,
    44: 5,
}

EDUCATION_POINTS_SINGLE = {
    EducationLevel.SECONDARY: 30,
    EducationLevel.ONE_YEAR: 90,
    EducationLevel.TWO_YEAR: 98,
    EducationLevel.BACHELOR: 120,
    EducationLevel.TWO_OR_MORE: 128,
    EducationLevel.MASTERS: 135,
    EducationLevel.PHD: 150,
}

EDUCATION_POINTS_MARRIED = {
    EducationLevel.SECONDARY: 28,
    EducationLevel.ONE_YEAR: 84,
    EducationLevel.TWO_YEAR: 91,
    EducationLevel.BACHELOR: 112,
    EducationLevel.TWO_OR_MORE: 119,
    EducationLevel.MASTERS: 126,
    EducationLevel.PHD: 140,
}

FIRST_LANGUAGE_SINGLE = {
    4: 6,
    5: 6,
    6: 9,
    7: 17,
    8: 23,
    9: 31,
    10: 34,
}

FIRST_LANGUAGE_MARRIED = {
    4: 6,
    5: 6,
    6: 8,
    7: 16,
    8: 22,
    9: 29,
    10: 32,
}

SECOND_LANGUAGE = {
    5: 1,
    6: 1,
    7: 3,
    8: 3,
    9: 6,
    10: 6,
}

CANADIAN_EXPERIENCE_SINGLE = {
    1: 40,
    2: 53,
    3: 64,
    4: 72,
    5: 80,
}

CANADIAN_EXPERIENCE_MARRIED = {
    1: 35,
    2: 46,
    3: 56,
    4: 63,
    5: 70,
}

SPOUSE_EDUCATION = {
    EducationLevel.SECONDARY: 2,
    EducationLevel.ONE_YEAR: 6,
    EducationLevel.TWO_YEAR: 7,
    EducationLevel.BACHELOR: 8,
    EducationLevel.TWO_OR_MORE: 9,
    EducationLevel.MASTERS: 10,
    EducationLevel.PHD: 10,
}

SPOUSE_LANGUAGE_POINTS = {
    4: 0,
    5: 1,
    6: 1,
    7: 3,
    8: 3,
    9: 5,
    10: 5,
}

SPOUSE_CANADIAN_EXPERIENCE = {
    0: 0,
    1: 5,
    2: 7,
    3: 8,
    4: 9,
    5: 10,  # 5 years or more
}

# =============== skill transferability =======================
EDUCATION_LANGUAGE = {
    EducationLevel.SECONDARY: (0, 0),
    EducationLevel.ONE_YEAR: (13, 25),
    EducationLevel.TWO_YEAR: (13, 25),
    EducationLevel.BACHELOR: (13, 25),
    EducationLevel.TWO_OR_MORE: (25, 50),
    EducationLevel.MASTERS: (25, 50),
    EducationLevel.PHD: (25, 50),
}

EDUCATION_CAN_EXP = {
    EducationLevel.SECONDARY: (0, 0),
    EducationLevel.ONE_YEAR: (13, 25),
    EducationLevel.TWO_YEAR: (13, 25),
    EducationLevel.BACHELOR: (13, 25),
    EducationLevel.TWO_OR_MORE: (25, 50),
    EducationLevel.MASTERS: (25, 50),
    EducationLevel.PHD: (25, 50),
}

FOREIGN_EXP_LANGUAGE = {
    0: (0, 0),
    1: (13, 25),
    2: (13, 25),
    3: (25, 50),
}

FOREIGN_CAN_EXP = {
    0: (0, 0),
    1: (13, 25),
    2: (13, 25),
    3: (25, 50),
}
