import re
from pathlib import Path


def test_tsac_sosac_defaults_and_ranges_in_app_config():
    app_text = Path("app.py").read_text(encoding="utf-8")
    sensitivity_text = Path("sensitivity.py").read_text(encoding="utf-8")

    assert 'if "tsac_beta" not in st.session_state:' in app_text
    assert 'st.session_state["tsac_beta"] = 0.0' in app_text
    assert 'if "sosac_gamma" not in st.session_state:' in app_text
    assert 'st.session_state["sosac_gamma"] = 0.0' in app_text
    assert 'if "equality_mode" not in st.session_state:' in app_text
    assert 'st.session_state["equality_mode"] = True' in app_text
    assert 'if "exclude_hi" not in st.session_state:' in app_text
    assert 'st.session_state["exclude_hi"] = False' in app_text

    tsac_slider_pattern = re.compile(
        r'tsac_beta_pct\s*=\s*st\.sidebar\.slider\(\s*'
        r'"Terrestrial Stewardship Allocation Component \(TSAC\)",\s*'
        r'min_value=0,\s*'
        r'max_value=15,\s*'
        r'step=1,\s*'
        r'format="%d%%",',
        re.DOTALL,
    )
    sosac_slider_pattern = re.compile(
        r'sosac_gamma_pct\s*=\s*st\.sidebar\.slider\(\s*'
        r'"SIDS Ocean Stewardship Allocation Component \(SOSAC\)",\s*'
        r'min_value=0,\s*'
        r'max_value=10,\s*'
        r'step=1,\s*'
        r'format="%d%%",',
        re.DOTALL,
    )

    assert tsac_slider_pattern.search(app_text)
    assert sosac_slider_pattern.search(app_text)
    assert 'tsac_beta = tsac_beta_pct / 100.0' in app_text
    assert 'sosac_gamma = sosac_gamma_pct / 100.0' in app_text

    assert 'if tsac_beta + sosac_gamma >= 1.0:' in app_text
    assert 'st.session_state["tsac_beta"] = 0.05' in app_text
    assert 'st.session_state["sosac_gamma"] = 0.03' in app_text
    assert '"5. Gini-optimal point"' in app_text
    assert 'Gini-optimal point (minimises Gini, Spearman > 0.85)' in app_text
    assert 'file_name="integrity_checks.csv"' in sensitivity_text

    assert '**How stewardship settings affect this country**' in app_text
    assert '"IUSAF only", 0.00, 0.00, False' in app_text
    assert '"Modest stewardship", 0.05, 0.03, False' in app_text
    assert '"Stronger stewardship", 0.10, 0.05, False' in app_text
    assert 'annotation_text=\'Equality reference\'' in app_text
    assert 'TSAC vs SOSAC Sensitivity Heatmap' not in app_text
