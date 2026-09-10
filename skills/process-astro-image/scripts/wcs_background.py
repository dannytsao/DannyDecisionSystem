#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy>=1.26"]
# ///

# ruff: noqa: CPY001, RUF001, TRY003, EM101, PLR2004

"""Small, deterministic background model used by the WCS mosaic adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray


class BackgroundModelError(ValueError):
    """Report an unusable tile background model."""


def fit_background(image: NDArray[np.floating]) -> NDArray[np.float32]:
    """Fit a quadratic sky model from sigma-clipped border block medians."""
    import numpy as np  # noqa: PLC0415 - optional runtime dependency

    if image.ndim != 2:
        raise BackgroundModelError("背景模型只接受 2D image")
    height, width = image.shape
    step = 32
    radius = 8
    xs = np.arange(radius, width - radius, step)
    ys = np.arange(radius, height - radius, step)
    if len(xs) < 4 or len(ys) < 4:
        raise BackgroundModelError("影像太小，無法估計背景模型")
    grid_x, grid_y = np.meshgrid(xs, ys)
    values = np.array(
        [
            np.nanmedian(image[y - radius:y + radius, x - radius:x + radius])
            for y in ys for x in xs
        ],
        dtype=np.float64,
    )
    x = grid_x.ravel() / (width / 2) - 1
    y = grid_y.ravel() / (height / 2) - 1
    design = np.column_stack((
        np.ones_like(x), x, y, x * x, x * y, y * y,
    ))
    border = (np.abs(x) >= 0.55) | (np.abs(y) >= 0.55)
    finite = border & np.isfinite(values)
    if int(np.count_nonzero(finite)) < design.shape[1]:
        raise BackgroundModelError("有效背景取樣不足")
    border_design = design[border]
    border_values = values[border]
    keep = np.isfinite(border_values)
    for _ in range(3):
        coefficients = np.linalg.lstsq(
            border_design[keep], border_values[keep], rcond=None,
        )[0]
        residual = border_values - border_design @ coefficients
        center = np.median(residual[keep])
        spread = 1.4826 * np.median(np.abs(residual[keep] - center))
        keep &= np.abs(residual - center) <= max(3 * spread, 1e-5)
    full_y, full_x = np.mgrid[0:height, 0:width]
    full_x = full_x / (width / 2) - 1
    full_y = full_y / (height / 2) - 1
    full_design = np.column_stack((
        np.ones(full_x.size), full_x.ravel(), full_y.ravel(),
        full_x.ravel() ** 2, full_x.ravel() * full_y.ravel(),
        full_y.ravel() ** 2,
    ))
    model = (full_design @ coefficients).reshape(image.shape)
    if not np.all(np.isfinite(model)) or float(np.nanmedian(model)) <= 0:
        raise BackgroundModelError("背景模型不是正的有限值")
    return np.asarray(model, dtype=np.float32)
