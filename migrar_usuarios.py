import json
import os

# Caminhos dos arquivos
DATA_DIR = "data"
USERS_ORIG = os.path.join(DATA_DIR, "users.json")
USERS_NEW = os.path.join(DATA_DIR, "users.json")
FRIENDS = os.path.join(DATA_DIR, "friends.json")
CONQUISTAS = os.path.join(DATA_DIR, "conquistas.json")
SCORE = os.path.join(DATA_DIR, "score.json")


STUDY_HISTORY = os.path.join(DATA_DIR, "study_history.json")
FAVORITES = os.path.join(DATA_DIR, "favorites.json")
ACTIVITY = os.path.join(DATA_DIR, "activity.json")

def main():
    with open(USERS_ORIG, "r", encoding="utf-8") as f:
        users = json.load(f)

    users_new = {}
    friends = {}
    conquistas = {}
    score = {}
    study_history = {}
    favorites = {}
    activity = {}

    for uid, u in users.items():
        # users.json (essencial)
        users_new[uid] = {
            "id": u.get("id", uid),
            "nome": u.get("nome"),
            "email": u.get("email"),
            "senha": u.get("senha"),
            "avatar": u.get("avatar", ""),
            "data_nascimento": u.get("data_nascimento", ""),
            "frase_pessoal": u.get("frase_pessoal", ""),
            "tema": u.get("tema", "dark"),
            "data_criacao": u.get("data_criacao"),
            "is_admin": u.get("is_admin", False)
        }
        # friends.json
        if u.get("friends"):
            friends[uid] = {"friends": u["friends"]}
        # conquistas.json
        conquistas[uid] = {
            "badges": u.get("badges", []),
            "conquistas": u.get("conquistas", [])
        }
        # score.json
        score[uid] = {
            "points": u.get("points", 0),
            "points_gained": u.get("stats", {}).get("points_gained", 0),
            "fast_answers": u.get("stats", {}).get("fast_answers", 0),
            "quizzes_finished": u.get("stats", {}).get("quizzes_finished", 0),
            "messages_sent": u.get("stats", {}).get("messages_sent", 0),
            "cards_created": u.get("stats", {}).get("cards_created", 0),
            "late_night_visits": u.get("stats", {}).get("late_night_visits", 0),
            "deck_review_counts": u.get("stats", {}).get("deck_review_counts", {}),
            "deck_errors": u.get("stats", {}).get("deck_errors", {}),
            "error_patterns": u.get("stats", {}).get("error_patterns", {})
        }
        # study_history.json
        if u.get("stats", {}).get("study_history"):
            study_history[uid] = u["stats"]["study_history"]
        # favorites.json
        if u.get("favorites"):
            favorites[uid] = u["favorites"]
        # activity.json
        activity[uid] = {
            "last_seen": u.get("last_seen", 0),
            "prev_seen": u.get("prev_seen", 0),
            "ultimo_uso_ia": u.get("ultimo_uso_ia", 0)
        }

    # Salva arquivos
    with open(USERS_NEW, "w", encoding="utf-8") as f:
        json.dump(users_new, f, ensure_ascii=False, indent=2)
    with open(FRIENDS, "w", encoding="utf-8") as f:
        json.dump(friends, f, ensure_ascii=False, indent=2)
    with open(CONQUISTAS, "w", encoding="utf-8") as f:
        json.dump(conquistas, f, ensure_ascii=False, indent=2)
    with open(SCORE, "w", encoding="utf-8") as f:
        json.dump(score, f, ensure_ascii=False, indent=2)
    with open(STUDY_HISTORY, "w", encoding="utf-8") as f:
        json.dump(study_history, f, ensure_ascii=False, indent=2)
    with open(FAVORITES, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)
    with open(ACTIVITY, "w", encoding="utf-8") as f:
        json.dump(activity, f, ensure_ascii=False, indent=2)

    print("Migração concluída! Arquivos gerados em ./data/")

if __name__ == "__main__":
    main()
