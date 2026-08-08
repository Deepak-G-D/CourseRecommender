import pytest
from catalog import load_courses, load_careers
from model import Student
from recommend import CourseRecommender


@pytest.fixture
def engine():
    courses = load_courses()
    careers = load_careers()

    return CourseRecommender(
        courses,
        careers
    )


def test_find_existing_career(engine):

    career = engine.find_career(
        "AI Engineer"
    )

    assert career is not None
    assert career["id"] == "ai_engineer"


def test_unknown_career_returns_none(engine):

    career = engine.find_career(
        "ML Engineer"
    )

    assert career is None


def test_find_missing_skills(engine):

    student = Student(
        background="ML graduate",
        goal="AI Engineer",
        skills=[
            "python",
            "statistics"
        ]
    )

    missing = engine.find_missing_skills(
        student
    )

    assert missing == [
        "machine learning",
        "deep learning"
    ]


def test_no_missing_skills(engine):

    student = Student(
        background="ML graduate",
        goal="AI Engineer",
        skills=[
            "python",
            "statistics",
            "machine learning",
            "deep learning"
        ]
    )

    missing = engine.find_missing_skills(
        student
    )

    assert missing == []


def test_prerequisites_are_ordered(engine):

    missing_skills = [
        "deep learning"
    ]

    roadmap, unavailable = (
        engine.generate_learning_path(
            missing_skills
        )
    )

    course_ids = [
        course["id"]
        for course in roadmap
    ]

    assert course_ids == [
        "python",
        "statistics",
        "machine_learning",
        "deep_learning"
    ]

    assert unavailable == []


def test_skill_normalization(engine):

    student = Student(
        background="ML graduate",
        goal="AI Engineer",
        skills=[
            " Python ",
            "STATISTICS"
        ]
    )

    missing = engine.find_missing_skills(
        student
    )

    assert missing == [
        "machine learning",
        "deep learning"
    ]