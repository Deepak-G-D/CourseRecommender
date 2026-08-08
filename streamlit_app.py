import streamlit as st
from model import Student
from catalog import load_courses, load_careers
from recommend import CourseRecommender
from llm import explain_learning_path
from validation import validate_explanation


# Page configuration
st.set_page_config(
    page_title="Course Recommendation Agent",
    page_icon="🎓",
    layout="wide"
)


# Load engine

@st.cache_resource
def get_engine():
    courses = load_courses()
    careers = load_careers()

    return CourseRecommender(courses, careers)


engine = get_engine()


# Session state

if "result" not in st.session_state:
    st.session_state.result = None

if "error" not in st.session_state:
    st.session_state.error = None


# Header

st.title("🎓 Course Recommendation Agent")

st.caption(
    "Build a personalized learning path based on your "
    "background, career goal, and current skills."
)

# Two-column layout

left, right = st.columns(
    [1, 1.5],
    gap="large"
)

# LEFT — Student profile

with left:

    st.subheader("👤 Your Profile")

    background = st.text_area(
        "Student background",
        placeholder=(
            "Example: Machine Learning graduate "
            "with a strong mathematics background."
        ),
        height=140
    )

    goal = st.text_input(
        "Career goal",
        placeholder="Example: AI Engineer"
    )

    skills = st.text_input(
        "Current skills",
        placeholder="Example: python, statistics, machine learning"
    )

    generate = st.button(
        "🚀 Generate Learning Path",
        type="primary",
        use_container_width=True
    )

# Generate recommendation

if generate:

    st.session_state.result = None
    st.session_state.error = None

     # Validate input
 
    if not background.strip():

        st.session_state.error = (
            "Please enter your background."
        )

    elif not goal.strip():

        st.session_state.error = (
            "Please enter your career goal."
        )

    elif not skills.strip():

        st.session_state.error = (
            "Please enter at least one current skill."
        )

    else:

        current_skills = [
            skill.strip().lower()
            for skill in skills.split(",")
            if skill.strip()
        ]

        student = Student(
            background=background.strip(),
            goal=goal.strip(),
            skills=current_skills
        )

        try:

            # Career lookup

            career = engine.find_career(
                student.goal
            )

            if career is None:

                st.session_state.error = (
                    f"Career '{student.goal}' is not "
                    "currently supported."
                )

            else:

                # Missing skills

                missing_skills = (
                    engine.find_missing_skills(
                        student
                    )
                )

                # Already qualified

                if not missing_skills:

                    st.session_state.result = {
                        "student": student,
                        "roadmap": [],
                        "unavailable": [],
                        "explanation": None,
                        "complete": True
                    }

                else:

                    # ------------------------------
                    # Generate roadmap
                    # ------------------------------

                    roadmap, unavailable = (
                        engine.generate_learning_path(
                            missing_skills
                        )
                    )

                    if not roadmap:

                        st.session_state.error = (
                            "We couldn't build a learning "
                            "path from the current catalogue."
                        )

                    else:

                        # --------------------------
                        # LLM explanation
                        # --------------------------

                        with st.spinner(
                            "Generating your personalized explanation..."
                        ):

                            explanation = (
                                explain_learning_path(
                                    student,
                                    roadmap
                                )
                            )

                            validate_explanation(
                                explanation,
                                roadmap
                            )

                        st.session_state.result = {
                            "student": student,
                            "roadmap": roadmap,
                            "unavailable": unavailable,
                            "explanation": explanation,
                            "complete": False
                        }

        except Exception as error:

            st.session_state.error = str(error)

# RIGHT — Results

with right:

    st.subheader("📚 Recommended Learning Path")

     # Error
 
    if st.session_state.error:

        st.warning(
            st.session_state.error
        )

        st.info("Supported careers:")

        for career in engine.careers:
            st.write(
                f"• {career['title']}"
            )

     # No result yet
 
    elif st.session_state.result is None:

        st.info(
            "Your personalized learning path "
            "will appear here."
        )

     # Result available
 
    else:

        result = st.session_state.result

      
        # Already qualified
       

        if result["complete"]:

            st.success(
                "🎉 You already have all the skills "
                "currently defined for this career."
            )

        # Learning path available

        else:

            roadmap = result["roadmap"]
            unavailable = result["unavailable"]
            explanation = result["explanation"]

            # Compact roadmap

            st.markdown("#### 🗺️ Learning Roadmap")

            course_columns = st.columns(len(roadmap))

            for index, (column, course) in enumerate(
                zip(course_columns, roadmap),
                start=1
            ):

                with column:

                    with st.container(border=True):

                        st.caption(f"STEP {index}")

                        st.markdown(
                            f"**{course['title']}**"
                        )

                        st.caption(
                            course.get(
                                "difficulty",
                                "Unknown"
                            )
                        )
            # Prerequisites

            prerequisite_lines = []

            for course in roadmap:

                prerequisites = course.get(
                    "prerequisites",
                    []
                )

                if prerequisites:

                    prerequisite_names = []

                    for prerequisite_id in prerequisites:

                        prerequisite_course = (
                            engine._get_course_by_id(
                                prerequisite_id
                            )
                        )

                        if prerequisite_course:

                            prerequisite_names.append(
                                prerequisite_course["title"]
                            )

                        else:

                            prerequisite_names.append(
                                prerequisite_id
                            )

                    prerequisite_lines.append(
                        f"**{course['title']}** ← "
                        + ", ".join(prerequisite_names)
                    )

            if prerequisite_lines:

                st.markdown(
                    "##### 🔗 Prerequisites"
                )

                for line in prerequisite_lines:

                    st.caption(line)

            # Unavailable skills

            if unavailable:

                st.warning(
                    "Some required skills are not "
                    "currently covered by the catalogue."
                )

                for skill in unavailable:

                    st.write(
                        f"⚠️ {skill}"
                    )

            # Explanation

            if explanation:

                st.markdown("---")

                st.subheader(
                    "💡 Why This Path?"
                )

                st.write(
                    explanation.get(
                        "summary",
                        ""
                    )
                )

                for item in explanation.get(
                    "recommendations",
                    []
                ):

                    st.markdown(
                        f"**{item['course_title']}**"
                    )

                    st.write(
                        item["reason"]
                    )

                    st.caption(
                        f"Why now: {item['why_now']}"
                    )