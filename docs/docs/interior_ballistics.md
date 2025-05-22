# Interior Ballistics

## Pressure Gradient
Propellant gas behaviour behind the projectile is complex. Modern approaches 
treats propellant solid-gas mixture as mixed-phase flow, and simulates 
fluctuation using CFD methods in 2D space.

Classical methods employs additional assumptions to yield tractable solution.
Stipulating instantaneous diffusion of the combustion gas product to 
iso-density, and analyzing with pseudo-steady-state newtonian dynamics yields 
the Lagrange Gradient, which describes the distribution of pressure and 
velocity as:

$$
\begin{align}
\frac{P_{gas}}{P_{proj}} &= \{1 + \frac{w}{2\varphi_1 m} [1-(\frac{v_{gas}}{v_{proj}})^2]\} \\
\frac{v_{gas}}{v_{proj}} &= \frac{x+l_0}{x_{proj} + l_0}
\end{align}
$$

Where:

* $v$: velocity
* $P$: pressure
* $x$: displacement from the projectile base's initial position
* $l_0$: equivalent length of chamber
* $w$: mass of propellant
* $m$: mass of projectile
* $\varphi_1$: projectile's fictitious mass adjustment factor

From this, the pressure at the breech face is:

$$
\frac{P_{breech}}{P_{proj}} = 1 + \frac{w}{2\varphi_1 m}
$$

and the length-averaged <u>mean pressure</u> in bore (or <u>average pressure</u>
for short), is:

$$
\begin{align}
\overline{P} &= \frac{P_{proj}}{x_{proj} + L} \int_{-l_0}^{x_{proj}} \{1 + \frac{w}{2\varphi_1 m} [1- (\frac{x+l_0}{x_{proj} + l_0})^2 ]\} \ dx \\
\frac{\overline{P}}{P_{proj}} &= 1 + \frac{w}{3\varphi_1 m} 
\end{align}
$$

