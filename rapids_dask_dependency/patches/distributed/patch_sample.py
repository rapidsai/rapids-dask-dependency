# Copyright (c) 2024, NVIDIA CORPORATION.


def patch_distributed_attr(mod):
    mod.test_attr = "hello world"
