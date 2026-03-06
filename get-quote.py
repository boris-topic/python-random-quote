import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

DATA_FILE = Path(__file__).with_name("activities.json")
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


def load_activities() -> list[dict[str, Any]]:
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_activities(activities: list[dict[str, Any]]) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(activities, file, ensure_ascii=False, indent=2)


def find_activity(activities: list[dict[str, Any]], activity_id: int) -> dict[str, Any]:
    for activity in activities:
        if activity["id"] == activity_id:
            return activity
    raise ValueError(f"Ingen aktivitet med id {activity_id} hittades.")


def now_string() -> str:
    return datetime.now().strftime(TIME_FORMAT)


def to_datetime(value: str) -> datetime:
    return datetime.strptime(value, TIME_FORMAT)


def get_elapsed_seconds(activity: dict[str, Any]) -> int:
    elapsed = int(activity["total_seconds"])
    if activity["running_since"]:
        elapsed += int((datetime.now() - to_datetime(activity["running_since"])).total_seconds())
    return max(elapsed, 0)


def format_duration(total_seconds: int) -> str:
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def next_id(activities: list[dict[str, Any]]) -> int:
    if not activities:
        return 1
    return max(item["id"] for item in activities) + 1


def add_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity = {
        "id": next_id(activities),
        "title": args.title,
        "completed": False,
        "total_seconds": 0,
        "running_since": None,
        "created_at": now_string(),
    }
    activities.append(activity)
    save_activities(activities)
    print(f"Skapade aktivitet #{activity['id']}: {activity['title']}")


def list_activities(_: argparse.Namespace) -> None:
    activities = load_activities()
    if not activities:
        print("Checklistan är tom. Lägg till en aktivitet med: python get-quote.py add \"Namn\"")
        return

    print("\nAktiviteter:")
    for activity in activities:
        running = "⏱️" if activity["running_since"] else " "
        done = "✅" if activity["completed"] else "⬜"
        duration = format_duration(get_elapsed_seconds(activity))
        print(f"{done} {running} #{activity['id']:>2} | {duration} | {activity['title']}")


def start_timer(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity = find_activity(activities, args.id)

    if activity["running_since"]:
        print("Tidtagningen är redan igång för denna aktivitet.")
        return

    activity["running_since"] = now_string()
    save_activities(activities)
    print(f"Startade tidtagning för aktivitet #{activity['id']}: {activity['title']}")


def stop_timer(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity = find_activity(activities, args.id)

    if not activity["running_since"]:
        print("Tidtagningen är inte igång för denna aktivitet.")
        return

    elapsed = int((datetime.now() - to_datetime(activity["running_since"])).total_seconds())
    activity["total_seconds"] = int(activity["total_seconds"]) + max(elapsed, 0)
    activity["running_since"] = None
    save_activities(activities)

    print(
        f"Stoppade tidtagning för aktivitet #{activity['id']}. "
        f"Total tid: {format_duration(activity['total_seconds'])}"
    )


def complete_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity = find_activity(activities, args.id)
    activity["completed"] = True
    save_activities(activities)
    print(f"Markerade aktivitet #{activity['id']} som klar.")


def reopen_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity = find_activity(activities, args.id)
    activity["completed"] = False
    save_activities(activities)
    print(f"Markerade aktivitet #{activity['id']} som inte klar.")


def remove_activity(args: argparse.Namespace) -> None:
    activities = load_activities()
    activity = find_activity(activities, args.id)
    activities = [item for item in activities if item["id"] != args.id]
    save_activities(activities)
    print(f"Tog bort aktivitet #{activity['id']}: {activity['title']}")


def show_summary(_: argparse.Namespace) -> None:
    activities = load_activities()
    total = len(activities)
    completed = sum(1 for item in activities if item["completed"])
    running = sum(1 for item in activities if item["running_since"])
    seconds = sum(get_elapsed_seconds(item) for item in activities)

    print("\nSammanfattning")
    print(f"- Antal aktiviteter: {total}")
    print(f"- Klara aktiviteter: {completed}")
    print(f"- Aktiva tidtagningar: {running}")
    print(f"- Total loggad tid: {format_duration(seconds)}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Checklista för aktiviteter med inbyggd tidtagning."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_parser = sub.add_parser("add", help="Skapa en ny aktivitet")
    add_parser.add_argument("title", help="Namn på aktiviteten")
    add_parser.set_defaults(func=add_activity)

    list_parser = sub.add_parser("list", help="Visa aktiviteter")
    list_parser.set_defaults(func=list_activities)

    start_parser = sub.add_parser("start", help="Starta tidtagning för en aktivitet")
    start_parser.add_argument("id", type=int, help="Aktivitetens id")
    start_parser.set_defaults(func=start_timer)

    stop_parser = sub.add_parser("stop", help="Stoppa tidtagning för en aktivitet")
    stop_parser.add_argument("id", type=int, help="Aktivitetens id")
    stop_parser.set_defaults(func=stop_timer)

    check_parser = sub.add_parser("check", help="Markera aktivitet som klar")
    check_parser.add_argument("id", type=int, help="Aktivitetens id")
    check_parser.set_defaults(func=complete_activity)

    uncheck_parser = sub.add_parser("uncheck", help="Markera aktivitet som inte klar")
    uncheck_parser.add_argument("id", type=int, help="Aktivitetens id")
    uncheck_parser.set_defaults(func=reopen_activity)

    remove_parser = sub.add_parser("remove", help="Ta bort aktivitet")
    remove_parser.add_argument("id", type=int, help="Aktivitetens id")
    remove_parser.set_defaults(func=remove_activity)

    summary_parser = sub.add_parser("summary", help="Visa total sammanfattning")
    summary_parser.set_defaults(func=show_summary)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
