import random
import time

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
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union

def form_match_room(waiting_pool, target_user, similarity_threshold=0.15):
    #1. determine room size
    max_capacity = 5 if target_user.mode == "group" else 2

    #score everyone in the waiting pool who chose the same mode
    scored_canadates =[]
    for candidate in waiting_pool:
        if candidate.user_id != target_user.user_id and candidate.mode  == target_user.mode:
            score = jaccard_similarity(target_user.interests, candidate.interests)
            if score >= similarity_threshold:
                scored_canadates.append((score, candidate))

    #3. Sort canidates from highest simiarl
    scored_canadates.sort(key=lambda pair: pair[0], reverse=True)
    #4. Pick the top matches up to max_capacity (target_user + up to 4 other)
    best_matches = [pair[1] for pair in  scored_canadates[:max_capacity -1]]
    matched_users = [target_user] + best_matches

    # 5. If we have at least 2 people, build and return the room dictionary!
    if len(matched_users) >= 2:
        # Deal unique adjectives and animals with ZERO repeats in this room!
        unique_adjs = random.sample(ADJECTIVES, len(matched_users))
        unique_animals = random.sample(ANIMALS, len(matched_users))
        for i, member in enumerate(matched_users):
            member.alias = f"{unique_adjs[i]} {unique_animals[i]}"

        # Find interests shared by the new user and the top matches
        shared = set()
        for member in best_matches:
            shared.update(target_user.interests.intersection(member.interests))

        return{
            "room_id": f"room_{int(time.time() * 1000)}",
            "mode": target_user.mode,
            "members": matched_users,
            "common_interests": list(shared),
            "duration_seconds": 45,  # 45 seconds for easy hackathon testing/demo!
            "reveal_votes": set()  # Stores user_ids of people who click "Reveal"
        }
if __name__ == "__main__":
    # Create a fake waiting pool of 5 people
    pool = [
        User("id_1", "Alice", "CS Major", ["Coding", "Coffee", "Gaming"], mode="group"),
        User("id_2", "Bob", "Design Major", ["Coffee", "Music", "Art"], mode="group"),
        User("id_3", "Charlie", "Math Major", ["Coding", "Gaming", "Fitness"], mode="group"),
        User("id_4", "Dana", "Bio Major", ["Hiking", "Cooking"], mode="group"),  # No overlap!
        User("id_5", "Eli", "Music Major", ["Gaming", "Music"], mode="1on1"),    # Different mode!
    ]

    # Create a new incoming user looking for a group
    new_person = User("id_6", "Jacob", "Cybersecurity", ["Coding", "Coffee", "Gaming"], mode="group")

    room = form_match_room(pool, new_person)

    if room:
        print(f"✅ Match Found! Room ID: {room['room_id']} (Mode: {room['mode']})")
        print(f"🎯 Shared Interests: {room['common_interests']}")
        print("🎭 Anonymous Members in Room:")
        for m in room["members"]:
            print(f"   - {m.alias} (Secretly: {m.real_name})")
    else:
        print("⏳ No match found yet.")
