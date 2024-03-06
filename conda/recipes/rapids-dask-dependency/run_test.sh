#!/bin/bash
# Copyright (c) 2024, NVIDIA CORPORATION.

echo "The current directory is ${PWD}"
ls
python -m pytest -v tests/
