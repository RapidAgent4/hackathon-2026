import random

ADJECTIVES = ["Neon", "Radiant", "Bright", "Swift", "Solar", "Electric", ]
ANIMALS = ["Fox", "Husky", "Owl", "Antelope", "Cat", "Hawk", "Pitbull" ]
class User:
    def __init__(self, user_id, real_name, bio, interests):
        self.user_id = user_id
        self.real_name = real_name
        self.bio = bio
        self.interests = set(interests)
