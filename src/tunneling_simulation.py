import os
import numpy as np
import matplotlib.pyplot as plt


def normalize(psi, dx):
    norm = np.sqrt(np.sum(np.abs(psi) ** 2) * dx)
    return psi / norm


def make_barrier(x, height, width):
    V = np.zeros_like(x)
    V[np.abs(x) <= width / 2] = height
    return V


def make_wave_packet(x, x0, sigma, k0):
    envelope = np.exp(-((x - x0) ** 2) / (2 * sigma ** 2))
    phase = np.exp(1j * k0 * x)
    return envelope * phase


def estimate_rt(x, density, dx, barrier_width, buffer=30.0):
    left = x < (-barrier_width / 2 - buffer)
    right = x > (barrier_width / 2 + buffer)
    middle_region = (~left) & (~right)

    R = np.sum(density[left]) * dx
    T = np.sum(density[right]) * dx
    middle = np.sum(density[middle_region]) * dx
    return R, T, middle


def split_step_fourier(psi0, V, x, dt, steps):
    dx = x[1] - x[0]
    n = len(x)
    k = 2 * np.pi * np.fft.fftfreq(n, d=dx)

    v_phase = np.exp(-1j * V * dt / 2)
    k_phase = np.exp(-1j * (k ** 2 / 2) * dt)

    psi = psi0.copy()
    prob_history = []

    for _ in range(steps):
        psi = v_phase * psi
        psi_k = np.fft.fft(psi)
        psi_k *= k_phase
        psi = np.fft.ifft(psi_k)
        psi = v_phase * psi

        prob_history.append(np.sum(np.abs(psi) ** 2) * dx)

    return psi, np.array(prob_history)


def run_simulation(
    barrier_height=1.0,
    barrier_width=4.0,
    x0=-100.0,
    sigma=12.0,
    k0=1.35,
    dt=0.02,
    steps=8500,
    n_grid=2048,
    x_min=-260.0,
    x_max=260.0,
):
    x = np.linspace(x_min, x_max, n_grid)
    dx = x[1] - x[0]

    V = make_barrier(x, barrier_height, barrier_width)

    psi0 = make_wave_packet(x, x0, sigma, k0)
    psi0 = normalize(psi0, dx)

    initial_density = np.abs(psi0) ** 2
    psi_final, prob_history = split_step_fourier(psi0, V, x, dt, steps)
    final_density = np.abs(psi_final) ** 2

    R, T, middle = estimate_rt(x, final_density, dx, barrier_width)
    energy = k0 ** 2 / 2
    max_norm_error = np.max(np.abs(prob_history - 1.0))

    return {
        "x": x,
        "initial_density": initial_density,
        "final_density": final_density,
        "prob_history": prob_history,
        "R": R,
        "T": T,
        "middle": middle,
        "energy": energy,
        "barrier_height": barrier_height,
        "barrier_width": barrier_width,
        "max_norm_error": max_norm_error,
    }


def save_and_show(filename, output_dir):
    filepath = os.path.join(output_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()


def plot_density(result, output_dir):
    x = result["x"]
    barrier_width = result["barrier_width"]
    barrier_height = result["barrier_height"]

    plt.figure(figsize=(10, 5))
    plt.plot(x, result["initial_density"], label="Initial density", linewidth=2)
    plt.plot(x, result["final_density"], label="Final density", linewidth=2)
    plt.axvspan(
        -barrier_width / 2,
        barrier_width / 2,
        alpha=0.2,
        label=f"Barrier region (V0 = {barrier_height:.2f})",
    )

    plt.xlabel("Position x")
    plt.ylabel("Probability density")
    plt.title("Quantum Tunneling Through a Rectangular Barrier")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    save_and_show("wavepacket_density.png", output_dir)


def plot_norm_error(result, output_dir):
    steps = np.arange(1, len(result["prob_history"]) + 1)
    norm_error = result["prob_history"] - 1.0

    plt.figure(figsize=(8, 5))
    plt.plot(steps, norm_error, linewidth=2)
    plt.xlabel("Time step")
    plt.ylabel("Total probability - 1")
    plt.title("Probability Norm Conservation")
    plt.grid(True, alpha=0.3)
    plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    plt.tight_layout()
    save_and_show("norm_conservation_error.png", output_dir)


def sweep_barrier_height(heights, base_params, output_dir):
    T_values = []
    R_values = []

    for h in heights:
        params = base_params.copy()
        params["barrier_height"] = h
        result = run_simulation(**params)

        T_values.append(result["T"])
        R_values.append(result["R"])

        print(f"height = {h:.2f} | T = {result['T']:.4f} | R = {result['R']:.4f}")

    plt.figure(figsize=(8, 5))
    plt.plot(heights, T_values, marker="o", linewidth=2, label="Transmission")
    plt.plot(heights, R_values, marker="s", linewidth=2, label="Reflection")
    plt.xlabel("Barrier height")
    plt.ylabel("Probability")
    plt.title("Transmission and Reflection vs Barrier Height")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    save_and_show("transmission_vs_height.png", output_dir)


def sweep_barrier_width(widths, base_params, output_dir):
    T_values = []
    R_values = []

    base_width = base_params["barrier_width"]
    base_steps = base_params["steps"]

    for w in widths:
        params = base_params.copy()
        params["barrier_width"] = w
        params["steps"] = base_steps + int(max(0, w - base_width) * 250)

        result = run_simulation(**params)
        T_values.append(result["T"])
        R_values.append(result["R"])

        print(f"width = {w:.2f} | T = {result['T']:.4f} | R = {result['R']:.4f}")

    plt.figure(figsize=(8, 5))
    plt.plot(widths, T_values, marker="o", linewidth=2, label="Transmission")
    plt.plot(widths, R_values, marker="s", linewidth=2, label="Reflection")
    plt.xlabel("Barrier width")
    plt.ylabel("Probability")
    plt.title("Transmission and Reflection vs Barrier Width")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    save_and_show("transmission_vs_width.png", output_dir)


def convergence_study_dt(dt_values, base_params, output_dir):
    total_time = base_params["dt"] * base_params["steps"]
    T_values = []

    print("\nTime-step convergence")
    for dt in dt_values:
        params = base_params.copy()
        params["dt"] = dt
        params["steps"] = int(round(total_time / dt))

        result = run_simulation(**params)
        T_values.append(result["T"])

        print(
            f"dt = {dt:.4f} | T = {result['T']:.6f} | "
            f"max norm error = {result['max_norm_error']:.2e}"
        )

    reference_T = T_values[-1]
    reference_dt = dt_values[-1]

    plt.figure(figsize=(8, 5))
    plt.plot(dt_values, T_values, marker="o", linewidth=2, label="Measured T")
    plt.axhline(
        reference_T,
        linestyle="--",
        linewidth=1.8,
        label=f"Reference T (dt = {reference_dt:.4f})",
    )
    plt.xlabel("Time step dt")
    plt.ylabel("Transmission probability")
    plt.title("Convergence of Transmission with Time Step")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    save_and_show("convergence_dt.png", output_dir)


def main():
    output_dir = os.path.abspath("results")
    os.makedirs(output_dir, exist_ok=True)

    base_params = {
        "barrier_height": 1.0,
        "barrier_width": 4.0,
        "x0": -100.0,
        "sigma": 12.0,
        "k0": 1.35,
        "dt": 0.02,
        "steps": 8500,
        "n_grid": 2048,
        "x_min": -260.0,
        "x_max": 260.0,
    }

    result = run_simulation(**base_params)

    print("Quantum Tunneling Simulation")
    print(f"Energy = {result['energy']:.4f}")
    print(f"R = {result['R']:.4f}, T = {result['T']:.4f}, middle = {result['middle']:.4f}")
    print(f"Max norm error = {result['max_norm_error']:.2e}\n")

    plot_density(result, output_dir)
    plot_norm_error(result, output_dir)

    sweep_barrier_height([0.6, 0.8, 1.0, 1.2, 1.4], base_params, output_dir)
    print()
    sweep_barrier_width([2.0, 4.0, 6.0, 8.0, 10.0], base_params, output_dir)
    print()
    convergence_study_dt([0.04, 0.03, 0.02, 0.015], base_params, output_dir)


if __name__ == "__main__":
    main()
