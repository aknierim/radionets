import click
import toml
from dl_training.utils import read_config, check_outpath, create_databunch, define_arch


@click.command()
@click.argument("configuration_path", type=click.Path(exists=True, dir_okay=False))
def main(configuration_path):
    """
    Start DNN training with options specified in configuration file.

    configuration_path: Path to the config toml file
    """
    config = toml.load(configuration_path)
    train_conf = read_config(config)

    click.echo("\n Simulation config:")
    print(train_conf, "\n")

    # check out path and look for existing files
    check_outpath(train_conf["model_path"])

    # create databunch
    data = create_databunch(
        data_path=train_conf["data_path"],
        fourier=train_conf["fourier"],
        batch_size=train_conf["bs"],
    )

    # get image size
    train_conf["image_size"] = data.train_ds[0][0][0].shape[1]

    # define architecture
    arch = define_arch(
        arch_name=train_conf["arch_name"], img_size=train_conf["image_size"]
    )
    
    # define_learner
    learner = define_learner(
        data,
        arch,
        train_conf,
    )

    # load pretrained model
    if train_conf["pretrained"]:
        load_pre_model(learn, pretrained_model)

    # Train the model, except interrupt
    try:
        learn.fit(num_epochs)
    except KeyboardInterrupt:
        pop_interrupt()


if __name__ == "__main__":
    main()
