#/usr/bin/env python3
from .zoomdl import zoomdl
import requests

def main(url, fname=None, password=None):
    zoomdl(url, fname, password)