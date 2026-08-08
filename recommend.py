class CourseRecommender:
    def __init__(self, courses, careers):
        self.courses = courses
        self.careers = careers

        #create a mapping of skills to courses for quick lookup
        self.course_map = {
            skill: course
            for course in courses
            for skill in course["skills"]
        }

        self.career_map = {
            career["id"]: career
            for career in careers
        }

    def find_career(self, goal):

        goal = goal.strip().lower()

        for career in self.careers:

            if career["title"].lower() == goal:
                return career

        return None
    def find_missing_skills(self, student):

        career = self.find_career(student.goal)

        if not career:
            return None

        required_skills = career["skills"]

        return [
            skill
            for skill in required_skills
            if skill not in student.skills
        ]

    #recommend courses 
    def generate_learning_path(self, missing_skills):

        ordered = []

        visited = set()

        for skill in missing_skills:

            self.add_course(
                skill,
                visited,
                ordered
            )

        return ordered

    # if skill is already visited, return. 
    # Otherwise, add the skill to the visited set and retrieve the corresponding course from the course_map. 
    # If the course exists, recursively call add_course for each prerequisite of the course.
    # Finally, append the course to the ordered list. 
    def add_course(self, skill, visited, ordered):

        if skill in visited:
            return

        visited.add(skill) #visited set ensures that each skill is processed only once.

        course = self.course_map.get(skill)

        if not course:
            return

        for prereq in course["prerequisites"]:  
            self.add_course(prereq, visited, ordered)

        ordered.append(course)
            