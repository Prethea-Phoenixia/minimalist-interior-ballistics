from ballistics.charge import Charge
from ballistics.form_function import FormFunction
from ballistics.gun import Gun


def unitary_to_exponent(
    unitary_burn_rate: float, pressure_exponent: float = 1
) -> float:
    """
    convert unitary burn rate (dm^3/s-kgf) to burn rate coefficient (m/s-Pa^n)
    """
    return unitary_burn_rate * 1e-3 * 9.8**-pressure_exponent


if __name__ == "__main__":

    type_54_76mm = Gun(
        caliber=76.2e-3, shot_mass=6.2, chamber_volume=1.484e-3, loss_fraction=0.03
    )

    pass
