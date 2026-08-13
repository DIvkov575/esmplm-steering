import pytest

from plm_steering import l52_layer_subset_causal_steering
from plm_steering import l51_run_repro
from plm_steering import l55_run_repro
from plm_steering import l56_immunogenicity_proxy_validation
from plm_steering import l57_run_repro


@pytest.mark.parametrize(
    "main",
    [
        l51_run_repro.main,
        l52_layer_subset_causal_steering.main,
        l55_run_repro.main,
        l56_immunogenicity_proxy_validation.main,
        l57_run_repro.main,
    ],
)
def test_legacy_experiment_entry_points_fail_closed(main):
    with pytest.raises(SystemExit, match="disabled.*hard-coded seeds"):
        main()
