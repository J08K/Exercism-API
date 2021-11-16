from typing import Generator
from exercism_api import exercism
from rich.progress import track
from rich import print_json
import json


SEPERATOR = ","

def exercise_submission_meta(track_slug: str, exercise_slug: str) -> int:
    return exercism.exercise_submissions(track_slug, exercise_slug)["meta"]


def exercise_outdated_count(track_slug: str, exercise_slug: str) -> Generator:
    print(track_slug, exercise_slug)
    for page_num in range(
        1, exercise_submission_meta(track_slug, exercise_slug)["total_pages"] + 1
    ):
        page_data = exercism.exercise_submissions(
            track_slug, exercise_slug, page=page_num
        )
        for submission in page_data["results"]:
            yield 1 if submission["is_out_of_date"] else 0


def track_exercises_slugs(track: str):
    res = exercism.track_exercises(track)
    return [exercise["slug"] for exercise in res]


def main(args):

    if args.exercise == "*":
        target_exercises = track_exercises_slugs(args.track)
    else:
        target_exercises = str(args.exercise).lower().split(SEPERATOR)

    for exercise in str(args.skipped).lower().split(SEPERATOR):
        target_exercises.remove(exercise)

    output = [{"slug": exercise} for exercise in target_exercises]

    # * Step 2: Get number of current submissions for selected exercises.
    for (idx, cur_exercise) in track(
        enumerate(output),
        description=f"Getting current amount of submissions from {args.track}",
        total=len(target_exercises),
    ):
        cur_exercise["total_submissions"] = exercise_submission_meta(
            args.track, cur_exercise["slug"]
        )["total_count"]
        output[idx] = cur_exercise

    # * Step 3: Get number of outdated submissions for selected exercises.
    if args.outdated:

        for idx, cur_exercise in enumerate(output):

            cur_exercise["total_outdated"] = 0

            if not args.no_progress:
                for num in track(
                    exercise_outdated_count(args.track, cur_exercise["slug"]),
                    description=f"Parsing exercises for exercise {cur_exercise['slug']}:",
                    total=cur_exercise["total_submissions"],
                ):
                    cur_exercise["total_outdated"] += num
            else:
                for num in exercise_outdated_count(args.track, cur_exercise["slug"]):
                    cur_exercise["total_outdated"] += num

            output[idx] = cur_exercise

    # * Step 4: Get delta's.

    if args.current and args.outdated:
        for idx, cur_exercise in track(
            enumerate(output), description="Calculating deltas...", total=len(output)
        ):
            cur_exercise["delta"] = (
                cur_exercise["total_submissions"] - cur_exercise["total_outdated"]
            )

    # * Step 5: Calculate '--sum'.
    if args.sum:
        sums = {}
        for cur_exercise in track(
            output, description="Calculating sums:", total=len(output)
        ):
            for key in cur_exercise:
                if type(cur_exercise[key]) == int:
                    if key not in sums.keys():
                        sums[key] = cur_exercise[key]
                    else:
                        sums[key] += cur_exercise[key]
        output.append(sums)

    # * Output handling
    if args.output_type == "json":
        if args.no_progress:
            print(json.dumps(output))
        else:
            print_json(json.dumps(output))

        if args.output_file:
            with open(args.output_file, "w+") as file:
                json.dump(output, file)


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
        help=f"The exercise-slug to get data of. Add multiple exercises by seperating with '{SEPERATOR}' and use '*' to select all in the track.",
    )

    args.add_argument(
        "-c",
        "--current",
        action="store_true",
        dest="current",
        help="Returns number of current submissions. If combined with '--outdated' returns delta of the two as well.",
    )

    args.add_argument(
        "-O",
        "--outdated",
        action="store_true",
        dest="outdated",
        help="Returns number of outdated submissions. If combined with '--current' returns delta of the two as well.",
    )

    args.add_argument(
        "-np",
        "--no-progress",
        action="store_true",
        dest="no_progress",
        help="When enabled, the program won't show its progress, just end output.",
    )

    args.add_argument(
        "-o",
        "--output",
        action="store",
        dest="output_file",
        help="Will output the data to path specified.",
    )

    args.add_argument(
        "-ot",
        "--output-type",
        action="store",
        dest="output_type",
        help="What the output type should be, currently only working on files. Automatically 'json'.",
        default="json",
    )

    args.add_argument(
        "-s",
        "--sum",
        action="store_true",
        dest="sum",
        help="Whether calculate a sum of all the 'totals' of all exercises.",
    )

    args.add_argument(
        "--skip",
        action="store",
        dest="skipped",
        help=f"Which exercises to skip. Seperate by '{SEPERATOR}' for multiple."
    )

    main(args.parse_args())
