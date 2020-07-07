#!/usr/bin/env python3
# coding: utf-8
"""Define the main module.

This deals with either being called as a frozen or dynamic package.
"""

import sys

if __package__ is None and not hasattr(sys, 'frozen'):
    # direct call of __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(path))
    print(os.path.dirname(path))

import zoom_dl

if __name__ == '__main__':
    zoom_dl.main()
