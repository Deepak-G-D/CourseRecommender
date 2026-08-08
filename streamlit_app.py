import streamlit as st

from model import Student
from catalog import load_courses, load_careers
from recommend import CourseRecommender
from llm import explain_learning_path
from validation import validate_explanation

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Course Recommender",
    page_icon="🎓",
    layout="centered"
)


# --------------------------------------------------
# Load recommendation engine
# --------------------------------------------------

@st.cache_resource
def get_engine():
    courses = load_courses()
    careers = load_careers()
    return CourseRecommender(courses, careers)


engine = get_engine()


# --------------------------------------------------
# UI
# --------------------------------------------------

st.title("Course Recommendation Agent")

st.write(
    "Tell us about your background, career goal, and current skills. "
    "The agent will create a personalized learning path."
)


background = st.text_area(
    "Student background",
    placeholder=(
        "Example: Mechanical Engineering graduate "
        "with some programming experience."
    ),
    height=120
)


goal = st.text_input(
    "Career goal",
    placeholder="Example: AI Engineer"
)


skills = st.text_input(
    "Current skills",
    placeholder="Example: python, sql, excel"
)


# --------------------------------------------------
# Recommendation
# --------------------------------------------------

if st.button("🚀 Generate Learning Path", type="primary"):

    # Basic validation
    if not background.strip():
        st.error("Please enter your background.")

    elif not goal.strip():
        st.error("Please enter your career goal.")

    elif not skills.strip():
        st.error("Please enter at least one current skill.")

    else:

        # Normalize skills
        current_skills = [
            skill.strip().lower()
            for skill in skills.split(",")
            if skill.strip()
        ]

        # Create student
        student = Student(
            background=background.strip(),
            goal=goal.strip(),
            skills=current_skills
        )

        try:
            # Find missing skills
            missing_skills = engine.find_missing_skills(student)

            # Step 2: Build prerequisite-aware roadmap

            roadmap = engine.generate_learning_path(
                missing_skills
            )

            # Handle unsupported career

            if not roadmap:

                st.warning(
                    f"We couldn't create a learning path for "
                    f"'{student.goal}'."
                )

                st.info(
                    "Try one of the careers currently supported "
                    "by the course catalog."
                )

            else:

                # Show learning path

                st.subheader("📚 Your Learning Path")

                for index, course in enumerate(
                    roadmap,
                    start=1
                ):

                    st.markdown(
                        f"### {index}. {course['title']}"
                    )

                    st.caption(
                        f"Difficulty: {course.get('difficulty', 'N/A')}"
                    )

                    prerequisites = course.get(
                        "prerequisites",
                        []
                    )

                    if prerequisites:

                        st.write(
                            "Prerequisites: "
                            + ", ".join(prerequisites)
                        )

                    st.divider()

                # Generate AI explanation

                with st.spinner(
                    "Generating personalized explanations..."
                ):

                    explanation = explain_learning_path(
                        student,
                        roadmap
                    )

                    validate_explanation(
                        explanation,
                        roadmap
                    )
                    st.subheader("Why This Path?")

                    st.write(explanation["summary"])

                    for item in explanation["recommendations"]:

                        st.markdown(
                            f"### {item['course_title']}"
                        )

                        st.write(item["reason"])

                        st.caption(
                            f"Why now: {item['why_now']}"
                        )

                        st.divider()

        except KeyError:

            st.error(
                f"Career '{goal}' is not currently supported "
                "by the recommendation engine."
            )

        except Exception as e:

            st.error(
                "Something went wrong while generating "
                "your recommendation."
            )

            st.exception(e)

