#validates LLM explanation against the generated roadmap
def validate_explanation(explanation, roadmap):

    expected_ids = [
        course["id"]
        for course in roadmap
    ]

    returned_ids = [
        item["course_id"]
        for item in explanation["recommendations"]
    ]

    if expected_ids != returned_ids:

        raise ValueError(
            "LLM explanation does not match the generated roadmap."
        )

    return True