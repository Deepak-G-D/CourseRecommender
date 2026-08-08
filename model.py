from dataclasses import dataclass 

@dataclass
class Student:
    background: str
    goal: str
    skills: list[str]
