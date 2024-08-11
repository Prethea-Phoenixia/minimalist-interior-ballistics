from ballistics.charge import Charge
from ballistics.form_function import FormFunction
from ballistics.gun import Gun

if __name__ == "__main__":

    type_54_76mm = Gun(
        caliber=76.2e-3, shot_mass=6.2, chamber_volume=1.484e-3, loss_fraction=0.03
    )
    charge_9__7 = Charge.from_areal_impulse(
        density=1600,
        force=95000,
        pressure_exponent=0.83,
        covolume=1e-3,
        adiabatic_index=1.2,
        gas_molar_mass=1,
        form_function=FormFunction.multi_perf(
            arch_width=10e-3, perforation_diameter=5e-3, height=0.12, n_perforation=7
        ),
        arch_thickness=10e-3,
        burn_rate_coefficient = ,
    )
    pass

"""
kgf s   9.8 kg m    s           kg
----- = -------- ------- = 980 ----
 dm^2     s^2    0.01m^2        m s
"""
