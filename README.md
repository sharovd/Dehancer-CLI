[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Test Coverage](https://github.com/dnsxns/Dehancer-CLI/blob/gh-pages/unit-test/unit-test-coverage.svg?raw=true)
![Vulnerabilities status](https://github.com/dnsxns/Dehancer-CLI/blob/gh-pages/vulnerabilities/vulnerabilities-snyk-result.svg?raw=true)

# Dehancer CLI

Dehancer CLI is an unofficial command line application that interacts with the [Dehancer Online API](https://online.dehancer.com/) to process images using various film presets. <br>
It allows you to view available presets, create contacts for an image, and develop images using specific film presets and settings.

## Features

- **Print presets**: Displays a list of available presets from the Dehancer Online API.
- **Create contacts**: Uploads an image and creates contacts using all available presets.
- **Develop image(s)**: Processes image(s) using specified film preset and custom settings.

## Usage

### Print list of available presets

```bash
$ dehancer-cli presets
```

### Create contacts for an image

```bash
$ dehancer-cli contacts path/to/image.jpg
```

### Develop image(s)

```bash
$ dehancer-cli develop path/to/image_or_directory --preset PRESET_NUMBER [OPTIONS]
```

Options

    --preset, -p: Preset number (required).
    --set_contrast, -s: Contrast setting.
    --set_exposure, -e: Exposure setting.
    --set_temperature, -t: Temperature setting.
    --set_tint, -i: Tint setting.
    --set_color_boost, -b: Color boost setting.
    --settings_file: Path to a settings file containing key-value pairs for settings.
    --logs, -l: Enable debug logs (1 for enabled, 0 for disabled).

## Development mode: setup python virtual environment

```bash
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Development mode: usage

### Print list of available presets

```bash
$ python dehancer-cli.py presets
```

### Create contacts for an image

```bash
$ python dehancer-cli.py contacts path/to/image.jpg
```

### Develop image(s)

```bash
$ python dehancer-cli.py develop path/to/image_or_directory --preset PRESET_NUMBER [OPTIONS]
```

Options

    --preset, -p: Preset number (required).
    --set_contrast, -s: Contrast setting.
    --set_exposure, -e: Exposure setting.
    --set_temperature, -t: Temperature setting.
    --set_tint, -i: Tint setting.
    --set_color_boost, -b: Color boost setting.
    --settings_file: Path to a settings file containing key-value pairs for settings.
    --logs, -l: Enable debug logs (1 for enabled, 0 for disabled).

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
