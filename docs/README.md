# Docs

This directory contains the project documentation. It is also part of the application delivery build.

## User guide

The document [user-guide.pdf](user-guide.pdf) is a copy of the original [README.md](../README.md) file
with unnecessary sections removed (e.g. badges, link to development documentation, licence information, etc.).<br>
This document is included in the application delivery build.

### How to update User guide

After updating the original [README.md](../README.md) file,
it is necessary to generate a PDF file based on it  and replace the existing one.<br>
This is currently done in manual mode to save CI resources,
assuming that the [README.md](../README.md) file does not change as often as the application code.

To generate the [user-guide.pdf](user-guide.pdf) file, run the script with no arguments,
for example: `$ python scripts/generate_user_guide.py`.
Note that if you add text to the original [README.md](../README.md) file, you will need to change the output_file_height value
when initialising the `MarkdownToPDFConverter`.
This value is responsible for the height of the generated single [user-guide.pdf](user-guide.pdf) file
to make the content of the document more comfortable for the user without splitting it into A4 pages.