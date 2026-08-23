from scripts.check_commit_message import validate_subject


def test_accepts_standard_subjects():
    assert validate_subject("feat: add IFC export support") == []
    assert validate_subject("fix(viewer): preserve selected element color") == []
    assert validate_subject("refactor(payload)!: replace binary format") == []


def test_accepts_automated_git_subjects():
    assert validate_subject("Merge branch 'main' into firstdraft") == []
    assert validate_subject("fixup! feat: add IFC export support") == []


def test_rejects_invalid_type():
    assert validate_subject("update: change viewer color")


def test_rejects_missing_subject():
    assert validate_subject("feat(viewer)")


def test_rejects_trailing_period():
    assert validate_subject("docs: update installation guide.")


def test_rejects_long_subject():
    assert validate_subject("feat: " + "x" * 67)
