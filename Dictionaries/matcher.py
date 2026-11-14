import random

ADJECTIVES = ["Neon", "Radiant", "Bright", "Swift", "Solar", "Electric", ]
ANIMALS = ["Fox", "Husky", "Owl", "Antelope", "Cat", "Hawk", "Pitbull" ]
class User:
    def __init__(self, user_id, real_name, bio, interests, mode="group"):
        self.user_id = user_id
        self.real_name = real_name
        self.bio = bio
        self.interests = set(interests)
        self.mode = mode

        #random name picker
        self.alias = f"{random.choice(ADJECTIVES)} {random.choice(ANIMALS)}"

def jaccard_similarity(set1, set2):
    #Returns a compatability score between 0.0 (no overlap) and 1.0 (full overlap)
    if not set1 or not set2:
        return 0.0

    #shared intrests divided by total combined unique intrests
    intersection = set1.intersection(set2)
    union = len(set1.union(set2))
    return intersection / union

def form_match_room(waiting_pool, target_user, similarity_threshold=0.15):
