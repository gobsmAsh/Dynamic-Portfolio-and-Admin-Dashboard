
from dataclasses import dataclass, field
from typing import List, Optional


# =========================
# 1. PROFILE MODEL
# =========================
@dataclass
class Profile:
    name: str
    title: str
    bio: str
    email: str
    location: str = ""
    github: str = ""
    linkedin: str = ""
    website: str = ""

    def to_dict(self):
        return {
            "name": self.name,
            "title": self.title,
            "bio": self.bio,
            "email": self.email,
            "location": self.location,
            "github": self.github,
            "linkedin": self.linkedin,
            "website": self.website,
        }


# =========================
# 2. SKILL MODEL
# =========================

@dataclass
class Skill:
    id: int
    name: str
    category: str = "General"
    proficiency: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "proficiency": self.proficiency
        }


# =========================
# 3. PROJECT MODEL
# =========================

@dataclass
class Project:
    id: int
    title: str
    description: str
    technologies: List[str] = field(default_factory=list)
    github_url: str = ""
    demo_url: str = ""
    image_url: str = ""
    year: Optional[int] = None
    featured: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "technologies": self.technologies,
            "github_url": self.github_url,
            "demo_url": self.demo_url,
            "image_url": self.image_url,
            "year": self.year,
            "featured": self.featured
        }


# =========================
# 4. ACHIEVEMENT MODEL
# =========================

@dataclass
class Achievement:
    id: int
    title: str
    description: str
    issuer: str = ""
    date: str = ""
    credential_url: str = ""
    image_url: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "issuer": self.issuer,
            "date": self.date,
            "credential_url": self.credential_url,
            "image_url": self.image_url
        }

import json
import os

DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "data.json"
)


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def get_next_id(items):
    if not items:
        return 1

    return max(item["id"] for item in items) + 1
