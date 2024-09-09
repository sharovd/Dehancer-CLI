# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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