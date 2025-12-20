from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_channel_split(exhibit: pd.DataFrame, out_png: str | None = None) -> None:
    n = exhibit["n"].to_numpy()
    g3 = exhibit["G3"].to_numpy()
    g4 = exhibit["G4"].to_numpy()
    c = exhibit["C"].to_numpy()

    plt.figure()
    plt.plot(n, g3, marker="o", label="G3 (symmetry)")
    plt.plot(n, g4, marker="o", label="G4 (collision)")
    plt.xlabel("Shell n")
    plt.ylabel("Empirical unit (eV)")
    plt.legend()
    plt.tight_layout()
    if out_png:
        plt.savefig(out_png, dpi=200)

    plt.figure()
    plt.plot(n, c, marker="o")
    plt.xlabel("Shell n")
    plt.ylabel("Coherence ratio C = G3/G4")
    plt.tight_layout()
    if out_png:
        out2 = out_png.replace(".png", "_ratio.png")
        plt.savefig(out2, dpi=200)