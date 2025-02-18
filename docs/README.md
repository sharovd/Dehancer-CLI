# Docs

This directory contains the project documentation. It is also part of the application delivery build.

## User guide

The document [user-guide.pdf](user-guide.pdf) is a copy of the original [README.md](../README.md) file 
with unnecessary sections removed (e.g. badges, link to development documentation, licence information, etc.).<br>
This document is included in the application delivery build.

### How to update User guide

After updating the original [README.md](../README.md) file,
it is necessary to generate a PDF file based on it  and replace the existing one.<br>
This is currently done in manual mode to save CI process resources,
assuming that the [README.md](../README.md) file is not changed as often as the application code.