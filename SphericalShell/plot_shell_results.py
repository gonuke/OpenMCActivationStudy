import matplotlib.pyplot as plt

import openmc

def extract_flux_spectrum():

    with openmc.StatePoint('statepoint.10.h5') as sp:
        t = sp.get_tally(name="Flux spectrum")

    # Get the energies from the energy filter
    energy_filter = t.filters[0]
    energies = energy_filter.bins[:, 0]

    # Get the flux values
    flux = t.get_values(value='mean').ravel()

    return energies, flux
  
def generate_plot(energies, flux):
    fig, ax = plt.subplots()
    ax.loglog(energies, flux, drawstyle='steps-post')
    ax.set_xlabel('Energy [eV]')
    ax.set_ylabel('Flux [neutron-cm/source]')
    ax.grid(True, which='both')
    return fig, ax

def plot_shell_results():
    energies, flux =  extract_flux_spectrum()
    fig, ax = generate_plot(energies, flux)
    plt.savefig('neutron_flux_v_energy.png')
    plt.show()

if __name__ == "__main__":
    plot_shell_results()