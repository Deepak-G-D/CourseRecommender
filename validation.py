def validate_explanation(explanation, roadmap):

    expected_ids = [
        course["id"]
        for course in roadmap
    ]

    recommendations = explanation.get(
        "recommendations",
        []
    )

    returned_ids = [
        item.get("course_id")
        for item in recommendations
    ]

    if expected_ids != returned_ids:

        raise ValueError(
            "LLM explanation does not match "
            "the generated learning path."
        )

    return True