# Helix Graphing Tool

## Using the Software

### Windows

If you are on 64-bit Windows, you can use the build of the software [here](https://github.com/Fluxanoia/Helix/raw/master/builds/Helix-Win64.zip). If you are on 32-bit Windows, see the section on [building](#building-the-project) or [running from the source](#running-from-source). If something doesn\'t work, it would be appreciated if you shared the error via an issue or [email](mailto:contact@fluxanoia.co.uk).

### MacOS and Linux

See the section on [building](#building-the-project) to get the software up and running on MacOS and Linux. If that doesn\'t work, try [running from the source](#running-from-source).

I have been unable to get hold of a Mac on the current version of MacOS, so there currently isn\'t a build for Mac. The guidance for Linux users is to build the project. If you do give building a try, it would be much appreciated if you:
- shared the error if it was unsuccessful (via an issue),
- contributed it to the project if it was successful (via a pull request or [email](mailto:contact@fluxanoia.co.uk)).

## Development

### Dependencies

Helix is written in [Python 3](https://www.python.org/downloads/) (specifically version 3.8.5, but more recent or earlier versions should work too) and uses the following libraries:

- [NumPy](https://numpy.org),
- [Matplotlib](https://matplotlib.org),
- [PIL](https://python-pillow.org),
- [SymPy](https://www.sympy.org/en/index.html),

as well as [PyInstaller](http://www.pyinstaller.org) for building.

### Building the Project

To build this project, you\'ll need every package listed in the [dependencies](#dependencies) section. Use the following command in the root of the project:

`pyinstaller __init__.py --clean -y -n Helix -w -i images/icon.ico`

This creates an executable version of the software in `dist/Helix`. Just remember to copy the `images` folder from the root into `dist/Helix`.

### Running from Source

To run from the source, you\'ll need every package listed in the [dependencies](#dependencies) section except [PyInstaller](http://www.pyinstaller.org). Simply run `__init__.py` in the project root with:

`python __init__.py`
