# Helix

## Building

To build this project, use the following command in the root of the project:

`pyinstaller __init__.py --clean -y -n Helix -w -i images/icon.ico`

This creates an executable version of the software in `dist/Helix`. Just remember to copy the `images` folder from the root into `dist/Helix`, then you can run the software.

## Libraries

Helix is built using:

- `numpy`
- `matplotlib`
- `sympy`
- `PyInstaller`
