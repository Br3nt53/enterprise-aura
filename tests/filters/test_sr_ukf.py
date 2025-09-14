import numpy as np

from aura_v2.domain.filters.models import cv_transition, position_measurement
from aura_v2.domain.filters.sr_ukf import SquareRootUKF, SRUKFConfig


def test_sr_ukf_prediction_update():
    cfg = SRUKFConfig(n=4, m=2, process_noise=0.1, meas_noise=0.5)
    ukf = SquareRootUKF(cfg, cv_transition, position_measurement)
    ukf.set_state(np.array([[0.0], [0.0], [1.0], [0.0]]), np.eye(4) * 0.1)
    ukf.predict(dt=1.0)
    z = np.array([[0.9], [0.05]])
    pre = ukf.x.copy()
    ukf.update(z)
    post = ukf.x
    assert np.linalg.norm(post - pre) > 0.0
