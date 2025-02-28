# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-02-28
### Added
- Added cache in user home directory to store presets and auth data.
- Added 'generate_user_guide.py' script and 'md_to_pdf_converter.py' file to generate user guide.
- Added 'user-guide.pdf' as a copy of the original 'README.md' and 'settings.yaml' files in build.
- Added js script 'get-settings-via-browser-console.js' as the 'Web extension' feature.
- Added new CLI command 'web-ext' as the 'Web extension' feature.
- Updated 'Build-executable-files' job in CI pipeline to obfuscate web extension js script.
- Covered 100% new or updated source code by unit tests.

### Changed
- Improved formatting for help command output.
- Updated all outdated dependencies.

### Fixed
- Fixed issue with large log file in debug mode.
- Fixed issue "Error, the program tried to call itself with '-c' argument. Disable with '--no-deployment-flag=self-execution'".
- Fixed linter founded issues.

### Security
- Fixed all vulnerability issues found by the application security framework.


## [0.3.0] - 2024-09-28
### Added
- Support Dehancer Online API v1.
- Support for all preset settings: adjustments and effects via CLI arguments or settings file.
- Covered 100% new or updated source code by unit tests.
- Added test data with different types of settings in the e2e test for the 'develop' (w/o authorisation) command.
- Added the ability to build MacOS and Windows executable files on demand to reduce pipeline time and costs.

### Changed
- Changed the format of the settings file from '.txt' to '.yaml'.
- Improved output of the 'develop' command: added information about the settings used.
- Updated part of the commands to set effects (use '--set_' prefix).
- Improved readability of unit tests: added ID for parameterised tests.
- Updated formatting in 'README.md', moved dev part to separate file 'README_DEV.md'.

### Fixed
- Fixed problem developing large images (support multipart uploads).


## [0.2.0] - 2024-09-09
### Added
- Added new command 'auth' for authorisation in Dehancer Online via API to be able to develop images without watermarks.
- Added new option ("-q", "--quality", "quality") to the 'develop' command to set the output image quality in authorised mode.
- Support for the following image quality levels has been added "low", "medium", "high".
- Covered 100% new or updated source code by unit tests.
- Added two e2e tests: for 'develop' (w/o authorisation) and 'version' commands.


## [0.1.0] - 2024-07-27
### Added
- Initial release of the 'Dehancer CLI' project.
- Implemented CLI to interact with the Dehancer Online API to process images using various film presets.
- Supported the following actions via CLI: print presets, create contacts, develop image(s).
- Supported guest mode only. It is not possible to develop image(s) without a watermark.
- Configured CI/CD process based on github actions.
- Added 'Check-code-style-and-format' job using [Ruff](https://docs.astral.sh/ruff/) as a linter and code formatter.
- Added 'Run-unit-tests' job using [Pytest](https://docs.pytest.org/) as a test framework.
- Added 'Run-e2e-tests' job using [Pytest](https://docs.pytest.org/) as a test framework.
- Added 'Check-for-vulnerabilities' job using [Snyk](https://snyk.io/) as a applicaton security framework.
- Added 'Build-executable-files' job using [Nuitka](https://nuitka.net/) as a python compiler.
- Added 'Publish-badges' to publish badges with code coverage and vulnerability check status.
- Covered 100% source code by unit tests.
- Covered two e2e tests: for 'print presets' and 'create contacts' actions.
- Added and manually verified builds for the next OS: Ubuntu 22.04, MacOS 14.5 and Windows 10.

### Fixed
- Fixed all problems found by linter and code formatter.

### Security
- Fixed all vulnerability issues found by the application security framework.