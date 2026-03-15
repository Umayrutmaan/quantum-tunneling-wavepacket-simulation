# Quantum Tunneling Wave Packet Simulation

This project presents a numerical simulation of **quantum tunneling** using the **time-dependent Schrödinger equation**.

The simulation models the propagation of a **Gaussian wave packet** traveling toward a **rectangular potential barrier**. When the wave packet reaches the barrier, part of the probability density reflects while another portion penetrates and emerges on the other side. This behavior demonstrates the fundamental quantum mechanical phenomenon known as **quantum tunneling**, where particles can pass through energy barriers even when their energy is lower than the barrier height.

The Schrödinger equation is solved numerically using the **Split-Step Fourier Method**, a spectral technique widely used in computational quantum mechanics. This method alternates between position space and momentum space using the **Fast Fourier Transform (FFT)** to efficiently compute time evolution.

Through this simulation we can visualize several important physical effects:

- propagation of a localized quantum wave packet  
- interaction of the wave packet with a potential barrier  
- partial reflection and transmission of probability density  
- conservation of total probability  
- dependence of tunneling probability on barrier height and width  

The project also performs **parameter sweeps** to analyze how tunneling probability changes when the barrier properties are varied.

---

# Physics Model

The system is governed by the **time-dependent Schrödinger equation**

```math
i\hbar \frac{\partial \psi(x,t)}{\partial t}
=
-\frac{\hbar^2}{2m}\frac{\partial^2 \psi(x,t)}{\partial x^2}
+
V(x)\psi(x,t)
