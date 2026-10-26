"""Compatibility for Meshplot 0.4's removed Matplotlib colormap API."""

from importlib import import_module

import matplotlib as mpl
import numpy as np


def get_colors(values, colormap="viridis", normalize=True, vmin=None, vmax=None):
    """Map scalar values to RGB using Matplotlib's current colormap registry."""
    if normalize:
        vmin, vmax = np.min(values), np.max(values)
    norm = mpl.colors.Normalize(vmin, vmax)
    return mpl.colormaps.get_cmap(colormap)(norm(values))[:, :3]


# Viewer imports this helper by name, so update its binding as well as utils.
# Keep the adaptation here instead of modifying the installed dependency.
import_module("meshplot.utils").get_colors = get_colors
import_module("meshplot.Viewer").get_colors = get_colors
