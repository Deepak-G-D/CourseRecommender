class CourseRecommender:

    def __init__(self, courses, careers):

        self.courses = courses
        self.careers = careers

        # Map every skill to the course that teaches it.
        #
        # Example:
        # "python" -> Python Programming course
        self.course_map = {
            skill: course
            for course in courses
            for skill in course["skills"]
        }

        # Map career ID to career object.
        self.career_map = {
            career["id"]: career
            for career in careers
        }

  
    # Career lookup
  
    def find_career(self, goal):

        normalized_goal = goal.strip().lower()

        for career in self.careers:

            if career["title"].strip().lower() == normalized_goal:
                return career

        return None

  
    # Find missing skills
  
    def find_missing_skills(self, student):

        career = self.find_career(student.goal)

        # None means the career is not supported.
        if career is None:
            return None

        required_skills = career["skills"]

        current_skills = {
            skill.strip().lower()
            for skill in student.skills
        }

        missing_skills = [
            skill
            for skill in required_skills
            if skill.lower() not in current_skills
        ]

        return missing_skills

  
    # Build prerequisite-aware learning path
  
    def generate_learning_path(self, missing_skills):

        ordered = []
        visited = set()
        unavailable = []

        if not missing_skills:
            return ordered, unavailable

        for skill in missing_skills:

            self._add_course(
                skill=skill,
                visited=visited,
                ordered=ordered,
                unavailable=unavailable
            )

        return ordered, unavailable

  
    # Recursive prerequisite resolver
  
    def _add_course(
        self,
        skill,
        visited,
        ordered,
        unavailable
    ):

        if skill in visited:
            return

        visited.add(skill)

        course = self.course_map.get(skill)

        if course is None:

            if skill not in unavailable:
                unavailable.append(skill)

            return

        for prerequisite_id in course.get(
            "prerequisites",
            []
        ):

            prerequisite_course = self._get_course_by_id(
                prerequisite_id
            )

            if prerequisite_course is None:

                if prerequisite_id not in unavailable:
                    unavailable.append(prerequisite_id)

                continue

            for prerequisite_skill in prerequisite_course["skills"]:

                self._add_course(
                    skill=prerequisite_skill,
                    visited=visited,
                    ordered=ordered,
                    unavailable=unavailable
                )

        ordered.append(course)
  
    # Course lookup by ID
  
    def _get_course_by_id(self, course_id):

        for course in self.courses:

            if course["id"] == course_id:
                return course

        return None