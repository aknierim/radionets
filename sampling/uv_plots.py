import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import cartopy.crs as ccrs
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from uv_simulations import get_uv_coverage
from obspy.imaging.cm import viridis_white_r


def plot_uv_coverage(u, v):
    plt.plot(u, v, marker='o', linestyle='none', markersize=2, color='#1f77b4')
    plt.xlabel(r'u / $\lambda$', fontsize=16)
    plt.ylabel(r'v / $\lambda$', fontsize=16)
    plt.tight_layout()
    

def plot_baselines(antenna):
    x_base, y_base = antenna.get_baselines()
    plt.plot(x_base, y_base, linestyle='--',
             color='#2ca02c', zorder=0, label='Baselines', alpha=0.35)
    

def plot_antenna_distribution(source_lon, source_lat, source, antenna, baselines=False):
    x, y, z = source.to_ecef(val=[source_lon, source_lat])
    x_enu_ant, y_enu_ant = antenna.to_enu(x, y, z)

    ax = plt.axes(projection=ccrs.Orthographic(source_lon, source_lat))
    ax.set_global()
    ax.coastlines()

    plt.plot(x_enu_ant, y_enu_ant, marker='o', markersize=6, color='#1f77b4',
             linestyle='none', label='Antenna positions')
    plt.plot(x, y, marker='*', linestyle='none', color='#ff7f0e', markersize=15,
             transform=ccrs.Geodetic(), zorder=10, label='Source')

    if baselines is True:
        plot_baselines(antenna)

    plt.legend(fontsize=16, markerscale=1.5)
    plt.tight_layout()


def animate_baselines(source, antenna, filename, fps):
    s_lon = source.lon_prop
    s_lat = source.lat_prop
    
    fig = plt.figure(figsize=(6, 6), dpi=100)

    def init():
        pass

    def update(frame):
        lon = s_lon[frame]
        lat = s_lat[frame]
        plot_antenna_distribution(lon, lat, source, antenna, baselines=True)

    ani = FuncAnimation(fig, update, frames=len(s_lon),
                        init_func=init, interval=1000 / fps)

    ani.save(str(filename)+'.gif', writer=PillowWriter(fps=fps))


def animate_uv_coverage(source, antenna, filename, fps):
    u, v, steps = get_uv_coverage(source, antenna, iterate=True)

    fig = plt.figure(figsize=(6, 6), dpi=100)

    def init():
        pass

    def update(frame):
        plot_uv_coverage(u[frame], v[frame])
        plt.ylim(-5e8, 5e8)
        plt.xlim(-5e8, 5e8)

    ani = FuncAnimation(fig, update, frames=steps,
                        init_func=init, interval=0.001, repeat=False)

    ani.save(str(filename)+'.gif', dpi=80, writer=PillowWriter(fps=fps))


def plot_image(source, ft=False):
    plt.rcParams.update({'font.size': 18})
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    if ft is False:
        img = source
    else:
        img = FT(source)
    s = ax.imshow(img, cmap=viridis_white_r)
    fig.colorbar(s, label='Intensity')
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.xaxis.set_ticks_position('none') 
    ax.yaxis.set_ticks_position('none')
    ax.set_xlabel('l')
    ax.set_ylabel('m')
    plt.tight_layout()
    
    
def plot_frequencies(source, ft=True):
    plt.rcParams.update({'font.size': 18})
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)
    if ft is True:
        img = FT(source)
    else:
        img = source
    s = ax.imshow(img, cmap=viridis_white_r, norm=LogNorm())
    fig.colorbar(s, label='Amplitude')
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.xaxis.set_ticks_position('none') 
    ax.yaxis.set_ticks_position('none')
    ax.set_xlabel('u')
    ax.set_ylabel('v')
    plt.tight_layout()


def FT(img):
    return np.abs(np.fft.fftshift(np.fft.fft2(img)))


def apply_mask(img, mask):
    img[~mask] = 0
    return img