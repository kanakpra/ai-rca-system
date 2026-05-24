VALID_PREFIXES = [
    "app/",
    "tests/"
]


def validate_plan(plan):

    invalid_files = []

    files = plan.get(
        "files_to_modify",
        []
    )

    for file_name in files:

        valid = False

        for prefix in VALID_PREFIXES:

            if file_name.startswith(prefix):
                valid = True
                break

        if not valid:
            invalid_files.append(
                file_name
            )

    return invalid_files