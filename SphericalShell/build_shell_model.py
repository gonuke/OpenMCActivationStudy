import argparse

import numpy as np

import openmc

def create_materials(element, density):
    """
    Create a material set with a single material.

    inputs
    -------
    element (string) : element symbol
    density (float) : mass density of elemetn

    returns
    -------
    openmc Materials list with a single openmc Material object

    """
    W = openmc.Material(name='W_Shell')
    W.add_element(element, 1.0)
    W.set_density('g/cm3', density)
    return openmc.Materials([W])

def create_geometry(r_1, r_2, shell_mat):
    """
    Create a spherical shell with inner radius r_1 
    and outer radius r_2.
    
    inputs
    -------
    r_q (float) : inner radius [cm]
    r_2 (float) : outer radius [cm]
    shell_mat (openmc.Material) : material to fill shell

    returns
    --------
    openmc Geometry object
    """
    R_1 = openmc.Sphere(r=r_1)
    R_2 = openmc.Sphere(r=r_2, boundary_type='vacuum')

    # Mapping materials to geometry:
    Void = openmc.Cell(fill=None, region = -R_1)
    Shell = openmc.Cell(fill=shell_mat, region=(R_1 & -R_2))
    return openmc.Geometry([Void, Shell])

def create_isotropic_fusion_point_source():
    """
    Create an OpenMC source at the origin with isotropic
    direction and 14 MeV energy.

    inputs
    ------
    none

    returns
    --------
    openmc Source object
    """

    PointSource = openmc.stats.Point(xyz=(0.0, 0.0, 0.0))
    Prob = openmc.stats.Discrete(14E+06, 1.0)
    return openmc.Source(space=PointSource, energy=Prob, strength = 1.0, particle = 'neutron')

def setup_problem(batches=10, particles_per_batch=100000):
    """
    Set te OpenMC problem run settings.

    inputs
    -------
    batches (int) : number of batches to run for statistical analysis
                    (default: 10)
    particles_per_batch (int) : number of histories per batch
                                (default: 100000)

    returns
    --------
    OpenMC Settings object
    """
    settings = openmc.Settings()
    settings.batches = batches
    settings.particles = particles_per_batch
    settings.run_mode = 'fixed source'
    return settings

def create_tallies(cell):
    """
    Create standard openmc tallies for this problem.
    The standard tallies for this problem include:
    * total flux tally
    * total elastic scattering rate
    * total absorption rate

    inputs
    ------
    cell (OpenMC Cell) : location of tally

    returns
    -------
    OpenMC Tallies object with problem standard tallies
    """
    cell_filter = openmc.CellFilter([cell])

    e_min = 5e2
    e_max = 14.001e6
    groups = 500
    energies = np.logspace(e_min, e_max, groups + 1)
    energy_filter = openmc.EnergyFilter(energies)

    neutron_tally = openmc.Tally(name="Total neutron tally")
    neutron_tally.scores = ['flux', 'elastic', 'absorption']
    neutron_tally.filters = [cell_filter]

    spectrum_tally = openmc.Tally(name="Flux spectrum")
    spectrum_tally.filters = [energy_filter, cell_filter]
    spectrum_tally.scores = ['flux']

    return openmc.Tallies([neutron_tally, spectrum_tally])

def parse_args():
    """
    Setup parser for shell model problem.
    """
    parser = argparse.Parser()

    parser.add_argument("--element", '-e', default='W')
    parser.add_argument("--density", '-d', default=19.28)
    parser.add_argument("--inner_radius", '-r', default=1000)
    parser.add_argument("--shell_thickness", '-t', default=5)

    return parser.parse_args()

def build_shell_model():

    args = parse_args()
    materials = create_materials(args.element, args.density)
    geometry = create_geometry(args.inner_radius, args.inner_radius + args.thickness, materials[0])
    source = create_isotropic_fusion_point_source()
    tallies = create_tallies(geometry[1])
    settings = setup_problem()


if __name__ == "__main__":
    build_shell_model()