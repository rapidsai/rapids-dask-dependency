# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

# This package only exists to hold patches for submodules of `distributed.protocol`.
# It intentionally does not define `load_module`, so `distributed.protocol` itself is
# imported unmodified.
