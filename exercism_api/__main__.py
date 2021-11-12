from typing import Generator
from exercism_api import exercism
from rich.progress import track


def exercise_submission_meta(track_slug: str, exercise_slug: str) -> int:
    return exercism.exercise_submissions(track_slug, exercise_slug)["meta"]


def exercise_outdated_count(track_slug: str, exercise_slug: str) -> Generator:

    for page_num in range(
        1, exercise_submission_meta(track_slug, exercise_slug)["total_pages"] + 1
    ):
        page_data = exercism.exercise_submissions(
            track_slug, exercise_slug, page=page_num
        )
        for submission in page_data["results"]:
            yield 1 if submission["is_out_of_date"] else 0


def main(args):

    total_exercises = exercise_submission_meta(args.track, args.exercise)["total_count"]

    if args.outdated:

        total_outdated = 0

        if not args.no_progress:
            for num in track(
                exercise_outdated_count(args.track, args.exercise),
                description="Parsing exercises...",
                total=total_exercises,
            ):
                total_outdated += num
        else:
            for num in exercise_outdated_count(args.track, args.exercise):
                total_outdated += num

    if args.outdated and args.current:
        delta = total_exercises - total_outdated
        print(delta)
    elif args.outdated:
        print(total_outdated)
    elif args.current:
        print(total_exercises)
    else:
        print("No output selected!")


if __name__ == "__main__":

    from argparse import ArgumentParser

    args = ArgumentParser(
        description="Simple module to get data from the exercism.org website."
    )

    args.add_argument(
        "track",
        action="store",
        metavar="T",
        help="The track-slug to get data from.",
    )

    args.add_argument(
        "exercise",
        action="store",
        metavar="E",
        help="The exercise-slug to get data of.",
    )

    args.add_argument(
        "-c",
        "--current",
        action="store_true",
        dest="current",
        help="Returns number of current submissions. If combined with '--outdated' returns delta of the two.",
    )

    args.add_argument(
        "-O",
        "--outdated",
        action="store_true",
        dest="outdated",
        help="Returns number of outdated submissions. If combined with '--current' returns delta of the two.",
    )

    args.add_argument(
        "-np",
        "--no-progress",
        action="store_true",
        dest="no_progress",
        help="When enabled, the program won't show its progress, just end output.",
    )

    main(args.parse_args())
