You are working on a Python AI RCA backend project.

Project structure:

- app/reasoning/parser.py
  Handles log extraction and event parsing

- app/reasoning/severity.py
  Handles severity scoring

- app/reasoning/correlation.py
  Handles timeline correlation and root cause detection

- tests/test_parser.py
  Parser tests

- tests/test_severity.py
  Severity tests

Current features:
- timeline correlation
- severity scoring
- AI RCA generation
- FastAPI API
- GitHub Actions CI
- Render deployment

Feature request:
{{FEATURE_REQUEST}}

Return ONLY valid JSON.

Format:

{
  "files_to_modify": [],
  "logic_changes": [],
  "tests_required": [],
  "possible_risks": []
}