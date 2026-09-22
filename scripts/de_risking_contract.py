"""Single source of truth for the De-Risking Judgement Call decision grades.

Shared by check_de_risking_judgement_call.py and test_de_risking_judgement_call_browser.py so the
expected grades are derived from one constant and not repeated in each script.
"""

GRADE_LABELS = {
    "best": "Supported on the text, whichever reading applies",
    "incomplete": "Supported on the text but incomplete",
    "reading": "Rests on one reading of an open point",
    "unsupported": "Not supported on the text",
    "unsupported-facts": "Not supported on the stated facts",
}

ALLOWED_GRADES = tuple(GRADE_LABELS)

# decision key (the form's data-scenario-id) -> option value -> grade
EXPECTED_OPTION_GRADES = {
    "respondent": {
        "terminate": "reading",
        "unchanged": "unsupported",
        "escalate": "best",
        "restrict": "reading",
    },
    "ownership": {
        "apply31": "best",
        "enhanced": "unsupported",
        "notice": "unsupported",
        "wait": "unsupported-facts",
    },
    "residual": {
        "exit30": "unsupported",
        "test": "best",
        "fatf": "unsupported",
        "unchanged": "incomplete",
    },
}
