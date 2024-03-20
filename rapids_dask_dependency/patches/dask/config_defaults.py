# Copyright (c) 2024, NVIDIA CORPORATION.


def set_config_defaults(mod):
    # Set "dataframe.query-planning" default to False
    if mod.__name__ == "dask":
        if mod.config.get("dataframe.query-planning", None) is None:
            mod.config.set({"dataframe.query-planning": False})
