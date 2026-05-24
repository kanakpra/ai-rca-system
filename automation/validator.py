VALID_FILES = [
    "app/reasoning/parser.py",
    "app/reasoning/severity.py",
    "app/reasoning/correlation.py",
    "app/api/routes.py",
    "tests/test_parser.py",
    "tests/test_severity.py"
]


def validate_plan(plan):

    invalid_files = []

    files = plan.get(
        "files_to_modify",
        []
    )

    for file in files:

        if isinstance(file, dict):
            file_name = file.get(
                "file_name"
            )
        else:
            file_name = file

        if file_name not in VALID_FILES:
            invalid_files.append(
                file_name
            )

    return invalid_files