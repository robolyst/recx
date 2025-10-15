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


def test_check_extra_indices(multi_index_frames):
    b, c = multi_index_frames

    result = Rec(
        align_date_col=None,
        columns={},
        check_missing_indices=True,
        check_extra_indices=True,
        check_all=True,
    ).run(b, c)

    # Should fail because of the extra index in candidate
    assert not result.passed()

    result = Rec(
        align_date_col=None,
        columns={},
        check_missing_indices=True,
        check_extra_indices=False,
        check_all=True,
    ).run(b, c)

    # Should pass because we are not checking for extra indices
    assert result.passed()


def test_check_missin_indices(multi_index_frames):
    b, c = multi_index_frames

    # The candidate has extra indicies, so swap them so that the candidate has
    # missing indices
    b, c = c, b

    result = Rec(
        align_date_col=None,
        columns={},
        check_missing_indices=True,
        check_extra_indices=True,
        check_all=True,
    ).run(b, c)

    # Should fail because of the missing index in candidate
    assert not result.passed()

    result = Rec(
        align_date_col=None,
        columns={},
        check_missing_indices=False,
        check_extra_indices=True,
        check_all=True,
    ).run(b, c)

    # Should pass because we are not checking for missing indices
    assert result.passed()


def test_summary_runs_without_error(abs_tol_frames_large):
    b, c = abs_tol_frames_large
    rec = Rec(
        columns={
            "B": AbsTolCheck(tol=0.5, sort="desc"),
        },
        align_date_col="date",
    )
    result = rec.run(b, c)

    assert not result.passed()
    result.summary()
