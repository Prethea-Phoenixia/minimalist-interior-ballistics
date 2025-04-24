"""
GAU Tables parameters:
    ---Propellant Thermochemical
    f           950,000     kgf-dm/kg   propellant force
    alpha       1           dm^3/kg     covolume
    delta       1.6         kg/dm^3     bulk density
    theta       0.2                     adiabatic index -1

    ---Projectile
    p_0         300         kgf/cm^2    resistance to start
    (phi_1+1)   1                       work factor (assume no additional drag)

    ---Charge Shape
    chi         1.06                    6% arch/length, single perforated
    lambda      -0.06/1.06              as above
    phi         1                       as above

Constants:
    g_0         9.81        m/s^2       gravitational acceleration
"""

import os
import psutil
from minimalist_interior_ballistics import Significance
from minimalist_interior_ballistics.gun import Gun
from minimalist_interior_ballistics.state import StateList
from minimalist_interior_ballistics.charge import Charge
from minimalist_interior_ballistics.form_function import FormFunction
from tabulate import tabulate
from minimalist_interior_ballistics.num import dekker
from multiprocessing import Pool


def form(val: float) -> str:
    if val < 1:
        return f"{val:.4g}"[:6]
    else:
        return f"{val:.5g}"[:6]


gau_charge = Charge(
    density=1600,
    force=950000 * 0.981,
    form_function=FormFunction(chi=1.06, labda=-0.06 / 1.06, mu=0),
    pressure_exponent=1,
    adiabatic_index=1.2,
    covolume=0.001,
    reduced_burnrate=1e-6,
)

w, m = 1, 1
f = gau_charge.force
phi = 1 + w / (3 * m)


def vel_to_rv(v: float) -> float:
    return v * ((phi * m) / w) ** 0.5


def gun_burnout(B: float, Delta: float) -> tuple[Gun, StateList]:
    """

    Parameters
    ----------

    Notes
    -----
    phi = 1 + w / (3 m)
    V_0 = w / Delta
    S = sqrt(B f w phi m) / (e_1/u_1)

    Returns
    -------
    P
    """

    S = (B * f * w * phi * m) ** 0.5 * gau_charge.reduced_burnrate
    V_0 = w / Delta

    gun = Gun(
        cross_section=S,  # S
        charge_mass=w,  # w
        chamber_volume=V_0,  # V_0
        shot_mass=m,  # m
        charge=gau_charge,
        loss_fraction=0,
        start_pressure=300 * 9.81e4,
    )
    results = gun.to_burnout(acc=1e-6)

    return gun, results


def f_burnout(B: float, Delta: float) -> tuple[float, float, float, float, float]:
    gun, results = gun_burnout(B=B, Delta=Delta)
    burn_out_state = results.get_state_by_marker(Significance.BURNOUT)
    peak_pressure_state = results.get_state_by_marker(Significance.PEAK_PRESSURE)
    if any(v < 0 for v in (results.peak_average_pressure, vel_to_rv(results.burnout_velocity), gun.l_0)):
        raise ValueError("HERE!!")
    return (
        results.peak_average_pressure,
        burn_out_state.average_pressure,
        vel_to_rv(results.burnout_velocity),
        peak_pressure_state.travel / gun.l_0,
        burn_out_state.travel / gun.l_0,
    )


def table_4(p_d: float, Delta: float, B_min: float = 0.2, B_max: float = 25.0) -> float:

    def _f_burnout(B: float) -> float:
        p, _, _, _, _ = f_burnout(B=B, Delta=Delta)
        return p - p_d

    if _f_burnout(B_min) > 0 > _f_burnout(B_max):
        B_d, _ = dekker(_f_burnout, x_0=B_min, x_1=B_max, tol=B_min * 1e-6)
        return B_d
    else:
        return 0


def table_4_v(B_d: float, rv_d: float, Delta: float) -> float:
    Labda_d = 0
    if B_d != 0:
        gun, results = gun_burnout(B=B_d, Delta=Delta)
        burnout_state = results.get_state_by_marker(Significance.BURNOUT)
        Labda_b = burnout_state.travel / gun.l_0
        rv_b = vel_to_rv(burnout_state.velocity)

        rv_asymp = vel_to_rv(gun.asymptotic_velocity)

        def _f_muzzle(Labda: float) -> float:
            rv = vel_to_rv(gun.get_velocity_post_burnout(burnout_state=burnout_state, travel=Labda * gun.l_0))
            return rv - rv_d

        Labda_u = 10 * Labda_b
        if rv_asymp > rv_d > rv_b:
            while _f_muzzle(Labda_u) < 0:
                Labda_u *= 10
            Labda_d, _ = dekker(_f_muzzle, x_0=Labda_b, x_1=Labda_u, tol=Labda_b * 1e-6)

    return Labda_d


# settings for testing
# Deltas = [100 * i for i in range(1, 10)]
# Ps = [981000 * i for i in range(150, 460, 50)]

# settings for production
Deltas = [50 * i for i in range(1, 20)]
Ps = [9810000 * i for i in range(10, 49)]  # + [9810000 * i for i in range(42, 52, 2)]
Bs = [0.1 * i for i in range(1, 41)]
rvs = [100 * i for i in range(5, 18)]


def write_table_4s(rv: float, Bss: float):
    with open(os.path.join("tables", f"rv{rv:.0f}.txt"), "w+") as file:
        rv_table = []
        for P, Bs in zip(Ps, Bss):
            row = [f"{P / 98100:.0f}"]
            for Delta, B in zip(Deltas, Bs):
                Labda = table_4_v(B_d=B, rv_d=rv, Delta=Delta)
                row.append(form(Labda) if Labda else "---------")
            rv_table.append(row)

        file.writelines([r"\captionof{table}{$v_T$ " + f"{rv:.0f} m/s" + r"}" + "\n"])
        file.writelines(
            tabulate(
                rv_table,
                headers=[r"\diagbox[font=\scriptsize]{$P$}{$\Lambda$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )


def generate_row(P: float) -> tuple[list[float], list[str]]:
    B_row = []
    table_row = [f"{P / 98100:.0f}"]
    for Delta in Deltas:
        B = table_4(p_d=P, Delta=Delta)
        B_row.append(B)
        table_row.append(form(B) if B else "---------")
    return B_row, table_row


if __name__ == "__main__":

    # this generates table 1-3
    with (
        open(os.path.join("tables", "pressure_max.txt"), "w+") as max_pressure_file,
        open(os.path.join("tables", "pressure_burnout.txt"), "w+") as burnout_pressure_file,
        open(os.path.join("tables", "travel_burnout.txt"), "w+") as burnout_travel_file,
        open(os.path.join("tables", "velocity_burnout.txt"), "w+") as burnout_velocity_file,
        open(os.path.join("tables", "travel_max.txt"), "w+") as max_pressure_travel_file,
    ):
        P_ms, P_bs, rv_bs, labda_bs, labda_ms = [], [], [], [], []
        for B in Bs:
            B_str = f"{B:.1f}"
            P_m_row, P_b_row, rv_b_row, labda_m_row, labda_b_row = [B_str], [B_str], [B_str], [B_str], [B_str]
            for Delta in Deltas:
                P_m, P_b, rv_b, labda_m, labda_b = f_burnout(B=B, Delta=Delta)
                P_m = P_m / 9.81e4  # convert unit to kgf/cm^2
                P_b = P_b / 9.81e4  # convert unit to kgf/cm^2
                P_m_row.append(form(P_m) if P_m < 1e4 else "---------")
                P_b_row.append(form(P_b) if P_b < 1e4 else "---------")
                rv_b_row.append(form(rv_b))
                labda_m_row.append(form(labda_m))
                labda_b_row.append(form(labda_b))

            P_ms.append(P_m_row)
            P_bs.append(P_b_row)
            rv_bs.append(rv_b_row)
            labda_bs.append(labda_b_row)
            labda_ms.append(labda_m_row)

        max_pressure_file.writelines(
            tabulate(
                P_ms,
                headers=[r"\diagbox[font=\scriptsize]{$B$}{$P_m$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )
        burnout_pressure_file.writelines(
            tabulate(
                P_bs,
                headers=[r"\diagbox[font=\scriptsize]{$B$}{$P_b$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )

        burnout_velocity_file.write(
            tabulate(
                rv_bs,
                headers=[r"\diagbox[font=\scriptsize]{$B$}{$(v_T)_b$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )

        burnout_travel_file.write(
            tabulate(
                labda_bs,
                headers=[r"\diagbox[font=\scriptsize]{$B$}{$\Lambda_b$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )

        max_pressure_travel_file.write(
            tabulate(
                labda_ms,
                headers=[r"\diagbox[font=\scriptsize]{$B$}{$\Lambda_m$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )

    # this generates table 4
    with open(os.path.join("tables", "B.txt"), "w+") as pressure_file:
        with Pool(psutil.cpu_count(logical=False)) as pool:
            Bs, B_table = zip(*pool.map(generate_row, Ps))
        pressure_file.writelines(
            tabulate(
                B_table,
                headers=[r"\diagbox[font=\scriptsize]{$P$}{$B$}{$\Delta$}"] + [delta / 1e3 for delta in Deltas],
                tablefmt="latex_raw",
                disable_numparse=True,
            )
        )

        with Pool(psutil.cpu_count(logical=False)) as pool:
            pool.starmap(write_table_4s, [(rv, Bs) for rv in rvs])
