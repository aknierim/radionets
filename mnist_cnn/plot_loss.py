import click

import dl_framework.architectures as architecture
import torch
from dl_framework.callbacks import Recorder
from dl_framework.learner import get_learner
from dl_framework.model import load_pre_model
from inspection import plot_loss


@click.command()
@click.argument("model_path", type=click.Path(exists=False, dir_okay=True))
@click.argument("arch", type=str)
@click.argument(
    "pretrained_model", type=click.Path(exists=True, dir_okay=True), required=False
)
def main(
    model_path, arch, pretrained_model=None,
):
    data = []
    # Define model
    arch = getattr(architecture, arch)()
    cbfs = [
        Recorder,
    ]
    learn = get_learner(
        data, arch, 1e-3, opt_func=torch.optim.Adam, cb_funcs=cbfs
    )

    load_pre_model(learn, pretrained_model)

    # Plot loss
    plot_loss(learn, model_path)


if __name__ == "__main__":
    main()
