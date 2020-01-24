import click
import numpy as np
from tqdm import tqdm
from dl_framework.data import open_bundle, save_fft_pair, get_bundles
from simulations.uv_simulations import sample_freqs
import re


@click.command()
@click.argument('in_path', type=click.Path(exists=False, dir_okay=True))
@click.argument('out_path', type=click.Path(exists=False, dir_okay=True))
@click.argument('antenna_config_path', type=click.Path(exists=True,
                                                       dir_okay=False))
@click.option('-train', type=bool, required=True)
@click.option('-samp', type=bool, required=False)
@click.option('-specific_mask', type=bool)
@click.option('-lon', type=float, required=False)
@click.option('-lat', type=float, required=False)
@click.option('-steps', type=float, required=False)
def main(in_path, out_path, antenna_config_path, train=True, samp=True,
         specific_mask=False, lon=None, lat=None, steps=None):
    '''
    get list of bundles
    get len of all all bundles
    split bundles into train and valid (factor 0.2?)
    for every bundle
        calculate fft -> create fft pairs
        save to new h5 file
    tagg train and valid in filename
    '''
    bundles = get_bundles(in_path)
    if train is True:
        bundles = [path for path in bundles if
                   re.findall('gaussian_sources_train', path.name)]
    else:
        bundles = [path for path in bundles if
                   re.findall('gaussian_sources_valid', path.name)]

    for path in tqdm(bundles):
        bundle = open_bundle(path)
        bundle_fft = np.array([np.fft.fftshift(np.fft.fft2(img)) for img
                               in bundle])
        if samp is True:
            if specific_mask is True:
                bundle_fft = np.array([sample_freqs(img, antenna_config_path,
                                       128, lon, lat, steps) for img
                                       in bundle_fft])
            else:
                bundle_fft = np.array([sample_freqs(img, antenna_config_path,
                                       size=128) for img
                                       in bundle_fft])
        out = out_path + path.name.split('_')[-1]
        save_fft_pair(out, bundle_fft, bundle)


if __name__ == '__main__':
    main()
