"""
Punto de entrada principal del proyecto (redirecciona a principal.py).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from principal import main

if __name__ == "__main__":
    main()
