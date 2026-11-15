# 🦊 FoxHunt — Marist Student Meetups

**Chat anonymously by shared interests, break the ice, and meet up safely on campus.**

FoxHunt is a real-time, interest-based social matching platform built for Marist students. Instead of endless swiping or awkward cold-approaches, FoxHunt uses **Jaccard similarity** to pair students into anonymous "Fox Packs" (Group chats up to 5) or 1-on-1 rooms based on shared hobbies. Students chat under temporary aliases (like *Red Fox 🦊* or *Arctic Fox ❄️*) with custom Marist icebreakers until the countdown timer hits zero—at which point the pack can unmask their real identities or lock in an instant meetup at a verified safe campus spot.

---

##  Key Features

* ** Jaccard Similarity Matching Engine:** Automatically calculates set intersection over union ($J(A, B) = \frac{\vert{}A \cap B\vert{}}{\vert{}A \cup B\vert{}}$) across preset and user-generated custom interest tags to pair students with the highest compatibility.
* **Dynamic Group "Packs" & 1-on-1 Modes:** Supports both 1-on-1 matches and dynamic group rooms (up to 5 students). Active group rooms stay open to late-joining students who share the pack's core interests.
* **Anonymous Alias Roster:** Protects student privacy during the initial conversation by assigning unique fox-themed aliases and prevented duplicate names within the same room.
* * Context-Aware Marist Icebreakers:** Automatically injects campus-specific conversation starters tailored to the group's top shared interest (e.g., Saxbys orders at Hancock, McCann gym splits, or Hudson River walks).
* ** Synchronized Countdown & Unmasking:** Features configurable chat timers (45s demo mode, 5m mixer, 15m hangout). When time expires, students can trigger a synchronized live reveal of names and social handles across all connected screens.
* ** Safe Campus Meetup Integration:** Suggests curated, high-traffic Marist campus locations (Hancock Center, Murray Student Center, McCann, Byrne House) with an embedded interactive OpenStreetMap view.

---

## Tech Stack

* **Backend:** Python, Flask, Flask-SocketIO (WebSockets)
* **Matching Algorithm:** Custom Python Jaccard Similarity & Set Intersection Engine (`Dictionaries/matcher.py`)
* **Frontend:** HTML5, Vanilla JavaScript, Socket.IO Client, Tailwind CSS
* **Maps:** OpenStreetMap Embedded API

---

##  Project Structure

```text
FoxHunt/
├── app.py                   # Flask server & Socket.IO real-time event handlers
├── Dictionaries/
│   └── matcher.py           # User class & Jaccard similarity matching algorithm
├── templates/
│   └── index.html           # Responsive UI & WebSocket client controller
└── README.md                # Project documentation

Used gamini argon 4 for front end dev along with some backend dev and issues with things like websockets and more. 
