from ballistics.charge import Charge
from ballistics.form_function import FormFunction
from ballistics.gun import Gun
from ballistics.problem import MatchingProblem, Target

if __name__ == "__main__":

    p = MatchingProblem(
        caliber=76.2e-3,
        shot_mass=6.2,
        chamber_volume=1.484e-3,
        travel=2.687,
        loss_fraction=0.03,
        start_pressure=30e6,
        ignition_pressure=10e6,
        density=1600,
        force=95000,
        pressure_exponent=0.83,
        covolume=1e-3,
        adiabatic_index=1.2,
        gas_molar_mass=23.55,
        form_function=FormFunction.multi_perf(
            arch_width=10e-3, perforation_diameter=5e-3, height=0.12, n_perforations=7
        ),
    )

    p.solve(
        mass=1.08,
        velocity=680,
        pressure=238e6,
        target=Target.AVERAGE,
        n_intg=10,
        acc=1e-3,
    )


"""
kgf s   9.8 kg m    s           kg
----- = -------- ------- = 980 ----
 dm^2     s^2    0.01m^2        m s
"""
