#!/usr/bin/env python3
"""
Lab 7 - Test inputs for inference validation
Student: Madhav Murali | Roll No: 2022BCS0050
"""

# ── Valid Input ──────────────────────────────────────────────
# A representative red wine sample from the dataset
VALID_INPUT = {
    "fixed_acidity": 7.4,
    "volatile_acidity": 0.7,
    "citric_acid": 0.0,
    "residual_sugar": 1.9,
    "chlorides": 0.076,
    "free_sulfur_dioxide": 11.0,
    "total_sulfur_dioxide": 34.0,
    "density": 0.9978,
    "pH": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4
}

# ── Invalid Input ────────────────────────────────────────────
# Malformed: wrong types + missing required fields → should return HTTP 422
INVALID_INPUT = {
    "fixed_acidity": "not_a_number",
    "volatile_acidity": "bad"
    # All other required fields are missing
}

if __name__ == "__main__":
    import json
    print("=== 2022BCS0050 - Madhav Murali - Lab 7 Test Inputs ===")
    print("\n[VALID INPUT]")
    print(json.dumps(VALID_INPUT, indent=2))
    print("\n[INVALID INPUT]")
    print(json.dumps(INVALID_INPUT, indent=2))
