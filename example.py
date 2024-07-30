from ballistics.gun import Gun
from ballistics.form_function import single_perf
from ballistics.charge import Charge


def unitary_to_exponent(
    unitary_burn_rate: float, pressure_exponent: float = 1
) -> float:
    """
    convert unitary burn rate (dm^3/s-kgf) to burn rate coefficient (m/s-Pa^n)
    """
    return unitary_burn_rate * 1e-3 * 9.8**-pressure_exponent


if __name__ == "__main__":
    wb004p = Gun(
        caliber=100e-3, shot_mass=15.6, chamber_volume=7.741e-3, loss_fraction=0.06
    )
    ff = single_perf(arch_width=0.17e-2, length=26e-2)

    c = Charge(
        density=1600,
        force=980000,
        pressure_exponent=0.75,
        covolume=1e-3,
        burn_rate_coefficient=0.18e-2 / (1e6) ** 0.75,
        adiabatic_index=1.2,
        gas_molar_mass=23.55,
        arch_thickness=0.17e-2,
        form_function=ff,
    )
    print(c.I_k())
    wb004p.add_charge(charge=c, mass=5.6)

    print(wb004p.prettyprint(wb004p.to_burnout(n_intg=4, acc=1e-3)))
    print()
    print(wb004p.prettyprint(wb004p.to_travel(travel=47.43e-1, n_intg=10, acc=1e-3)))
    print()
    print(wb004p.prettyprint(wb004p.to_velocity(velocity=900, n_intg=10, acc=1e-3)))
    print(unitary_to_exponent(0.18e-2 / (1e6) ** 0.75 * 1e3 * 9.8))
