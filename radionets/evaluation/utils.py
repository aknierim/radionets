import numpy as np
import pandas as pd
from radionets.dl_framework.model import load_pre_model
from radionets.dl_framework.data import do_normalisation, load_data
import radionets.dl_framework.architecture as architecture
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import h5py
from pathlib import Path


def source_list_collate(batch):
    """Collate function for the DataLoader with source list

    Parameters
    ----------
    batch : tuple
        input and target images alongside with the corresponding source_list

    Returns
    -------
    tuple
        stacked images and list for source_list values
    """

    x = [item[0] for item in batch]
    y = [item[1] for item in batch]
    z = [item[2][0] for item in batch]
    return torch.stack(x), torch.stack(y), z


def create_databunch(data_path, fourier, source_list, batch_size):
    # Load data sets
    test_ds = load_data(
        data_path, mode="test", fourier=fourier, source_list=source_list,
    )

    # Create databunch with defined batchsize and check for source_list
    if source_list:
        data = DataLoader(
            test_ds, batch_size=batch_size, shuffle=True, collate_fn=source_list_collate
        )
    else:
        data = DataLoader(test_ds, batch_size=batch_size, shuffle=True)
    return data


def read_config(config):
    eval_conf = {}
    eval_conf["data_path"] = config["paths"]["data_path"]
    eval_conf["model_path"] = config["paths"]["model_path"]
    eval_conf["model_path_2"] = config["paths"]["model_path_2"]
    eval_conf["norm_path"] = config["paths"]["norm_path"]

    eval_conf["quiet"] = config["mode"]["quiet"]
    eval_conf["gpu"] = config["mode"]["gpu"]

    eval_conf["format"] = config["general"]["output_format"]
    eval_conf["fourier"] = config["general"]["fourier"]
    eval_conf["amp_phase"] = config["general"]["amp_phase"]
    eval_conf["arch_name"] = config["general"]["arch_name"]
    eval_conf["source_list"] = config["general"]["source_list"]
    eval_conf["arch_name_2"] = config["general"]["arch_name_2"]
    eval_conf["diff"] = config["general"]["diff"]

    eval_conf["vis_pred"] = config["inspection"]["visualize_prediction"]
    eval_conf["vis_source"] = config["inspection"]["visualize_source_reconstruction"]
    eval_conf["plot_contour"] = config["inspection"]["visualize_contour"]
    eval_conf["vis_dr"] = config["inspection"]["visualize_dynamic_range"]
    eval_conf["vis_blobs"] = config["inspection"]["visualize_blobs"]
    eval_conf["vis_ms_ssim"] = config["inspection"]["visualize_ms_ssim"]
    eval_conf["num_images"] = config["inspection"]["num_images"]
    eval_conf["random"] = config["inspection"]["random"]

    eval_conf["viewing_angle"] = config["eval"]["evaluate_viewing_angle"]
    eval_conf["dynamic_range"] = config["eval"]["evaluate_dynamic_range"]
    eval_conf["ms_ssim"] = config["eval"]["evaluate_ms_ssim"]
    eval_conf["mean_diff"] = config["eval"]["evaluate_mean_diff"]
    eval_conf["area"] = config["eval"]["evaluate_area"]
    eval_conf["batch_size"] = config["eval"]["batch_size"]
    eval_conf["point"] = config["eval"]["evaluate_point"]
    return eval_conf


def reshape_2d(array):
    """
    Reshape 1d arrays into 2d ones.

    Parameters
    ----------
    array: 1d array
        input array

    Returns
    -------
    array: 2d array
        reshaped array
    """
    shape = [int(np.sqrt(array.shape[-1]))] * 2
    return array.reshape(-1, *shape)


def make_axes_nice(fig, ax, im, title, phase=False, phase_diff=False, unc=False):
    """Create nice colorbars with bigger label size for every axis in a subplot.
    Also use ticks for the phase.
    Parameters
    ----------
    fig : figure object
        current figure
    ax : axis object
        current axis
    im : ndarray
        plotted image
    title : str
        title of subplot
    """
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    ax.set_title(title)

    if phase:
        cbar = fig.colorbar(
            im,
            cax=cax,
            orientation="vertical",
            ticks=[-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi],
        )
        cbar.set_label("Phase / rad")
    elif phase_diff:
        cbar = fig.colorbar(
            im,
            cax=cax,
            orientation="vertical",
            ticks=[-2 * np.pi, -np.pi, 0, np.pi, 2 * np.pi],
        )
        cbar.set_label("Specific Intensity / a.u.")
    elif unc:
        cbar = fig.colorbar(
            im,
            cax=cax,
            label="Rel. uncertainty / a.u.",
            ticks=[im.get_array().min() + 0.001, im.get_array().max()],
        )
        cbar.ax.set_yticklabels(["Low", "High"])
        cbar.ax.tick_params(size=0)
    else:
        cbar = fig.colorbar(im, cax=cax, orientation="vertical")
        cbar.set_label("Specific Intensity / a.u.")
        # tick_locator = ticker.MaxNLocator(nbins=5)
        # cbar.locator = tick_locator

    # cbar.ax.tick_params(labelsize=16)
    # cbar.ax.yaxis.get_offset_text().set_fontsize(16)
    # cbar.formatter.set_powerlimits((0, 0))
    # cbar.update_ticks()
    if phase:
        # set ticks for colorbar
        cbar.ax.set_yticklabels([r"$-\pi$", r"$-\pi/2$", r"$0$", r"$\pi/2$", r"$\pi$"])
    elif phase_diff:
        # set ticks for colorbar
        cbar.ax.set_yticklabels([r"$-2\pi$", r"$-\pi$", r"$0$", r"$\pi$", r"$2\pi$"])


def reshape_split(img):
    """
    reshapes and splits the the given image based on the image shape.
    If the image is based on two channels, it reshapes with shape
    (1, 2, img_size, img_size), otherwise with shape (img_size, img_size).
    Afterwards, the array is splitted in real and imaginary part if given.
    Parameters
    ----------
    img : ndarray
        image
    Returns
    ----------
    img_reshaped : ndarry
        contains the reshaped image in a numpy array
    img_real, img_imag: ndarrays
        contain the real and the imaginary part
    -------
    """
    if img.shape[0] == 1:
        img_size = int(np.sqrt(img.shape[0]))
        img_reshaped = img.reshape(img_size, img_size)

        return img_reshaped

    else:
        img_size = int(np.sqrt(img.shape[0] / 2))
        img_reshaped = img.reshape(1, 2, img_size, img_size)
        img_real = img_reshaped[0, 0, :]
        img_imag = img_reshaped[0, 1, :]

        return img_real, img_imag


def check_vmin_vmax(inp):
    """
    Check wether the absolute of the maxmimum or the minimum is bigger.
    If the minimum is bigger, return value with minus. Otherwise return
    maximum.
    Parameters
    ----------
    inp : float
        input image
    Returns
    -------
    float
        negative minimal or maximal value
    """
    if np.abs(inp.min()) > np.abs(inp.max()):
        a = -inp.min()
    else:
        a = inp.max()
    return a


def load_pretrained_model(arch_name, model_path, img_size=63):
    """
    Load model architecture and pretrained weigths.

    Parameters
    ----------
    arch_name: str
        name of the architecture (architectures are in dl_framework.architectures)
    model_path: str
        path to pretrained model

    Returns
    -------
    arch: architecture object
        architecture with pretrained weigths
    """
    if "filter_deep" in arch_name or "resnet" in arch_name:
        arch = getattr(architecture, arch_name)(img_size)
    else:
        arch = getattr(architecture, arch_name)()
    load_pre_model(arch, model_path, visualize=True)
    return arch


def get_images(test_ds, num_images, norm_path="none", rand=False):
    """
    Get n random test and truth images.

    Parameters
    ----------
    test_ds: h5_dataset
        data set with test images
    num_images: int
        number of test images
    norm_path: str
        path to normalization factors, if None: no normalization is applied

    Returns
    -------
    img_test: n 2d arrays
        test images
    img_true: n 2d arrays
        truth images
    """
    indices = torch.arange(num_images)
    if rand:
        indices = torch.randint(0, len(test_ds), size=(num_images,))
    img_test = test_ds[indices][0]
    norm = "none"
    if norm_path != "none":
        norm = pd.read_csv(norm_path)
    img_test = do_normalisation(img_test, norm)
    img_true = test_ds[indices][1]
    return img_test, img_true


def eval_model(img, model, test=False):
    """
    Put model into eval mode and evaluate test images.

    Parameters
    ----------
    img: str
        test image
    model: architecture object
        architecture with pretrained weigths

    Returns
    -------
    pred: n 1d arrays
        predicted images
    """
    if len(img.shape) == (3):
        img = img.unsqueeze(0)
    model.eval()
    if not test:
        model.cuda()
    with torch.no_grad():
        if not test:
            pred = model(img.float().cuda())
        else:
            pred = model(img.float())
    return pred.cpu()


def get_ifft(array, amp_phase=False):
    if len(array.shape) == 3:
        array = array.unsqueeze(0)
    if amp_phase:
        amp = 10 ** (10 * array[:, 0] - 10) - 1e-10

        a = amp * np.cos(array[:, 1])
        b = amp * np.sin(array[:, 1])
        compl = a + b * 1j
    else:
        compl = array[:, 0] + array[:, 1] * 1j
    if compl.shape[0] == 1:
        compl = compl.squeeze(0)
    return np.abs(np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(compl))))


def pad_unsqueeze(tensor):
    while tensor.shape[-1] < 160:
        tensor = F.pad(input=tensor, pad=(1, 1, 1, 1), mode="constant", value=0)
    tensor = tensor.unsqueeze(1)
    return tensor


def round_n_digits(tensor, n_digits=3):
    return (tensor * 10 ** n_digits).round() / (10 ** n_digits)


def fft_pred(pred, truth, amp_phase=True):
    """
    Transform predicted image and true image to local domain.

    Parameters
    ----------
    pred: 4D array [1, channel, height, width]
        prediction from eval_model
    truth: 3D array [channel, height, width]
        true image
    amp_phase: Bool
        trained on Amp/Phase or Re/Im

    Returns
    -------
    ifft_pred, ifft_true: two 2D arrays [height, width]
        predicted and true image in local domain
    """
    a = pred[:, 0, :, :]
    b = pred[:, 1, :, :]

    a_true = truth[0, :, :]
    b_true = truth[1, :, :]

    if amp_phase:
        amp_pred_rescaled = (10 ** (10 * a) - 1) / 10 ** 10
        phase_pred = b

        amp_true_rescaled = (10 ** (10 * a_true) - 1) / 10 ** 10
        phase_true = b_true

        compl_pred = amp_pred_rescaled * np.exp(1j * phase_pred)
        compl_true = amp_true_rescaled * np.exp(1j * phase_true)
    else:
        compl_pred = a + 1j * b
        compl_true = a_true + 1j * b_true

    ifft_pred = np.fft.ifft2(compl_pred)
    ifft_true = np.fft.ifft2(compl_true)

    return np.absolute(ifft_pred)[0], np.absolute(ifft_true)


def save_pred(path, x, y, z, name_x="x", name_y="y", name_z="z"):
    """
    write test data and predictions to h5 file
    x: predictions of truth of test data
    y: input image of the test data
    z: truth of the test data
    """
    with h5py.File(path, "w") as hf:
        hf.create_dataset(name_x, data=x)
        hf.create_dataset(name_y, data=y)
        hf.create_dataset(name_z, data=z)
        hf.close()


def read_pred(path):
    """
    read data saved with save_pred from h5 file
    x: predictions of truth of test data
    y: input image of the test data
    z: truth of the test data
    """
    with h5py.File(path, "r") as hf:
        x = np.array(hf["pred"])
        y = np.array(hf["img_test"])
        z = np.array(hf["img_true"])
        hf.close()
    return x, y, z


def check_outpath(model_path):
    model_path = Path(model_path).parent / "evaluation" / "predictions.h5"
    path = Path(model_path)
    exists = path.exists()
    return exists
