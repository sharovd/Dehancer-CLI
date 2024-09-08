[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Test Coverage](https://github.com/dnsxns/Dehancer-CLI/blob/gh-pages/unit-test/unit-test-coverage.svg?raw=true)
![Vulnerabilities status](https://github.com/dnsxns/Dehancer-CLI/blob/gh-pages/vulnerabilities/vulnerabilities-snyk-result.svg?raw=true)

# Dehancer CLI

Dehancer CLI is an unofficial command line application that interacts with the [Dehancer Online](https://online.dehancer.com/) API to process images using various film presets. <br>
It allows you to view available presets, create contacts for an image, and develop images using specific film presets and settings.

## Features

- **Print presets**: Displays a list of the presets available in the Dehancer Online.
- **Create contacts**: Uploads an image and creates contacts using all available presets.
- **Develop image(s)**: Processes image(s) using specified film preset, quality and custom settings.

## Usage

### Setup the executable file

- **Linux**: There are no additional steps required.
- **MacOS**: Run `xattr -c dehancer-cli` to remove all extended attributes from the specified file. You can find out more about this [here](https://support.apple.com/en-gb/guide/mac-help/mchleab3a043/mac) or [here](https://support.apple.com/en-bw/102445).
- **Windows**: Unfortunately, there is no stable and free solution for running build for Windows to bypass antivirus. See [this page](https://nuitka.net/user-documentation/common-issue-solutions.html#windows-virus-scanners) for more details. <br>
You can disable the Microsoft Defender Antivirus service the first time you start the application.

### Authentication in Dehancer Online

Authentication is only required for develop image(s) without a watermark. <br>
All of the commands can be used without authentication as well.

```bash
$ dehancer-cli auth <user@test.com>
```

### Print list of available presets

```bash
$ dehancer-cli presets
```

### Create contacts for an image

```bash
$ dehancer-cli contacts <path/to/image.jpg>
```

### Develop image(s)

```bash
$ dehancer-cli develop <path/to/image_or_directory> --preset <preset_number> [OPTIONS]
```

Options

    --preset, -p: Preset number (required).
    --quality, -q: Image quality level: ["low", "medium", "high"]
    --set_contrast, -s: Contrast setting.
    --set_exposure, -e: Exposure setting.
    --set_temperature, -t: Temperature setting.
    --set_tint, -i: Tint setting.
    --set_color_boost, -b: Color boost setting.
    --settings_file: Path to a settings file containing key-value pairs for settings.
    --logs, -l: Enable debug logs (1 for enabled, 0 for disabled).

Image Quality Levels

    Quality Level  | Description       | Resolution               | Format & Quality
    -------------- | ----------------- | ------------------------ | ------------------
    Low            | Optimised for web | Resized to 2160x2160     | JPEG 80%
    Medium         | Best quality      | Max resolution 3024x3024 | JPEG 100%
    High           | Lossless          | Max resolution 3024x3024 | TIFF 16 bit

### Print application version

```bash
$ dehancer-cli --version
```

## Developer mode: install and setup [poetry](https://python-poetry.org/)

```bash
$ poetry install
```

## Developer mode: usage (you can choose between python and poetry)

### Authentication in Dehancer Online

Authentication is only required for develop image(s) without a watermark. <br>
All of the commands can be used without authentication as well.

```bash
$ python auth <user@test.com>

$ poetry run dehancer-cli auth <user@test.com>
```

### Print list of available presets

```bash
$ python dehancer_cli.py presets

$ poetry run dehancer-cli presets
```

### Create contacts for an image

```bash
$ python dehancer_cli.py contacts <path/to/image.jpg>

$ poetry run dehancer-cli contacts <path/to/image.jpg>
```

### Develop image(s)

```bash
$ python dehancer_cli.py develop <path/to/image_or_directory> --preset <preset_number> [OPTIONS]

$ poetry run dehancer-cli develop <path/to/image_or_directory> --preset <preset_number> [OPTIONS]
```

Options

    --preset, -p: Preset number (required).
    --quality, -q: Image quality level: ["low", "medium", "high"]
    --set_contrast, -s: Contrast setting.
    --set_exposure, -e: Exposure setting.
    --set_temperature, -t: Temperature setting.
    --set_tint, -i: Tint setting.
    --set_color_boost, -b: Color boost setting.
    --settings_file: Path to a settings file containing key-value pairs for settings.
    --logs, -l: Enable debug logs (1 for enabled, 0 for disabled).

Image Quality Levels

    Quality Level  | Description       | Resolution               | Format & Quality
    -------------- | ----------------- | ------------------------ | ------------------
    Low            | Optimised for web | Resized to 2160x2160     | JPEG 80%
    Medium         | Best quality      | Max resolution 3024x3024 | JPEG 100%
    High           | Lossless          | Max resolution 3024x3024 | TIFF 16 bit

### Print application version

```bash
$ python dehancer_cli.py --version

$ poetry run dehancer-cli --version
```

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
