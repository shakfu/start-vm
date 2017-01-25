# start-vm

Generates bash setup files from yaml `recipe` files for 1-step setup of **new installed** linux installs (VMs / etc..).

Do **not** use on pre-existing setups as this program may well over-write your files. You have been warned!

## basic usage: installation

Install ubuntu server 16.04 LTS on a virtual machine engine (in this case we are using vmware fusion, but others can be used as well)

```
$ git clone https://github.com/shakfu/start-vm

$ cd start-vm

$ setup/ubuntu_16.04_base.sh
```

## basic usage: generation

To generate a `setup/<platform-recipt>.sh` file from a `recipes/<recipe>.yml` file:

```
$ install.py --bashfile recipes/<recipe>.yml
```

The generated bash recipe files are created in the `setup` folder

**IMPORTANT NOTE**: As of the current implementation *everthing* in `default` is copied into `$HOME` and *everthing* in `config` is copied into `$HOME/.config`.

As of the current implementation, only ubuntu 16.04 LTS `base.yml` is available. Forks and and pull requests for other variations are of course wellcome.

Future plans include the generation of Dockerfiles from the recipe.yml files.
