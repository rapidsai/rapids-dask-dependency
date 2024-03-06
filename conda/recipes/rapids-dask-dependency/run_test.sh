#!/bin/bash
# Copyright (c) 2024, NVIDIA CORPORATION.

echo "The recipe dir is: ${RECIPE_DIR}"
echo "The source dir is: ${SRC_DIR}"
cd ${RECIPE_DIR}/../../..
ls
python -m pytest -v tests/
