#!/usr/bin/env python3
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# ---------- helpers ----------
def rotate_and_compare(x, y, theta_deg, X, M):
    """Return mean squared error after translating by (X,42) and rotating by -theta."""
    th = math.radians(theta_deg)
    u = x - X
    v = y - 42.0
    # rotate by -theta
    u_p =  np.cos(th)*u + np.sin(th)*v  # ~ t
    v_p = -np.sin(th)*u + np.cos(th)*v  # ~ e^{M|t|} sin(0.3 t)
    pred = np.exp(M*np.abs(u_p)) * np.sin(0.3*u_p)
    mse = np.mean((v_p - pred)**2)
    return mse, u_p, v_p, pred

def grid_search(x, y):
    # Coarse ranges are deliberately small and human-readable.
    theta_grid = np.arange(20.0, 40.1, 1.0)      # degrees
    M_grid     = np.arange(0.0,  0.0501, 0.005)  # exponent scale
    X_grid     = np.arange(40.0, 70.1, 1.0)      # x-translation

    best = (float("inf"), None, None, None)
    for th in theta_grid:
        for M in M_grid:
            for X in X_grid:
                mse, *_ = rotate_and_compare(x, y, th, X, M)
                if mse < best[0]:
                    best = (mse, th, M, X)

    # Fine search around the coarse best
    _, th0, M0, X0 = best
    theta_grid = np.arange(th0-1.0, th0+1.01, 0.1)
    M_grid     = np.arange(M0-0.01, M0+0.0101, 0.001)
    X_grid     = np.arange(X0-2.0, X0+2.01, 0.1)

    for th in theta_grid:
        for M in M_grid:
            for X in X_grid:
                mse, *_ = rotate_and_compare(x, y, th, X, M)
                if mse < best[0]:
                    best = (mse, th, M, X)

    return best  # (mse, theta_deg, M, X)

# ---------- main ----------
def main():
    df = pd.read_csv("data/xy_data.csv")
    x = df["x"].to_numpy()
    y = df["y"].to_numpy()

    mse, theta_deg, M, X = grid_search(x, y)

    # Compute errors and plot
    mse, u_p, v_p, pred = rotate_and_compare(x, y, theta_deg, X, M)
    l1 = float(np.mean(np.abs(v_p - pred)))

    th = math.radians(theta_deg)
    t  = np.linspace(max(6, u_p.min()), min(60, u_p.max()), 1000)
    xx = t*np.cos(th) - np.exp(M*np.abs(t))*np.sin(0.3*t)*np.sin(th) + X
    yy = 42 + t*np.sin(th) + np.exp(M*np.abs(t))*np.sin(0.3*t)*np.cos(th)

    plt.figure(figsize=(6,6))
    plt.scatter(x, y, s=6, alpha=0.7, label="data")
    plt.plot(xx, yy, linewidth=2, label="fit")
    plt.legend()
    plt.xlabel("x"); plt.ylabel("y")
    plt.title(f"theta={theta_deg:.3f}°, M={M:.5f}, X={X:.3f}\nL1={l1:.3e}, MSE={mse:.3e}")
    plt.tight_layout()
    plt.savefig("outputs/fit_plot.png", dpi=160)

    with open("outputs/params.txt", "w") as f:
        f.write(f"theta_deg: {theta_deg}\n")
        f.write(f"theta_rad: {math.radians(theta_deg)}\n")
        f.write(f"M: {M}\n")
        f.write(f"X: {X}\n")
        f.write(f"L1 (rotated frame): {l1}\n")
        f.write(f"MSE (rotated frame): {mse}\n")

    print("Done.")
    print(f"theta_deg={theta_deg}, M={M}, X={X}")
    print("Saved: outputs/fit_plot.png and outputs/params.txt")

if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    main()