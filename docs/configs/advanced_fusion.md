# Advanced Fusion & Association Configuration

## Association Weights
- `AURA_ASSOC_WEIGHTS= iou:0.5,motion:0.4,confidence:0.1`
- `AURA_ASSOC_MAX_COST=3.5`

## Mahalanobis Gating
- `AURA_ASSOC_CHISQ_DOF2=5.991`  # 95% for 2D
- Increase to 9.210 for 99% tolerance.

## UKF Parameters
- `AURA_UKF_ALPHA=0.001`
- `AURA_UKF_BETA=2.0`
- `AURA_UKF_KAPPA=0`
- `AURA_UKF_SIGMA_ACC=1.0`

## Adaptive Noise
Set `AURA_UKF_ADAPTIVE=1` to enable innovation-based adjustment.

## Performance
- `AURA_ASSOC_SPATIAL_INDEX=1` enables candidate pruning (future feature).
