from recx import AbsTolCheck, EqualCheck, Rec


def test_basic_diff(diff_frames):
    b, c = diff_frames
    rec = Rec(columns={"B": EqualCheck()}, align_date_col="date")
    result = rec.run(b, c)
    assert not result.passed()
    assert {r.column for r in result.failures()} == {"B"}


def test_skip_column(diff_frames):
    b, c = diff_frames
    rec = Rec(columns={"B": None}, align_date_col="date")
    result = rec.run(b, c)
    assert result.passed()


def test_abs_tol_integration(abs_tol_frames):
    b, c = abs_tol_frames
    rec = Rec(columns={"B": AbsTolCheck(tol=0.5)}, align_date_col="date")
    result = rec.run(b, c)
    assert not result.passed()
    failure = result.failures()[0]
    assert "abs_error" in failure.failed_rows.columns
