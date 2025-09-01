import pandas as pd

from recx.rec import clip_to_last_common_date, get_col


def test_get_col_with_index():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}).set_index("A")
    assert list(get_col(df, "A")) == [1, 2, 3]
    assert list(get_col(df.reset_index(), "A")) == [1, 2, 3]


def test_clip_to_last_common_date_index(dated_frames):
    baseline, candidate = dated_frames
    a_clip, b_clip = clip_to_last_common_date(baseline, candidate, "date")
    assert a_clip.equals(baseline)
    # Candidate should be clipped to remove trailing 2024-01-03, keeping first two rows
    assert list(b_clip.index) == ["2024-01-01", "2024-01-02"]


def test_clip_to_last_common_date_index_on_multi_index(multi_index_frames):
    b, c = multi_index_frames
    a_clip, b_clip = clip_to_last_common_date(b, c, "vintage_date")
    assert a_clip.equals(b)

    assert b_clip.index.get_level_values("vintage_date").tolist() == [
        "2024-01-01",
        "2024-01-02",
    ]
