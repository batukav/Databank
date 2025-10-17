"""
:module: core/experiment.py

:description: Module for handling experimental data entries in the databank.
"""
import os
from abc import ABC, abstractmethod

import yaml

from DatabankLib import NMLDB_EXP_PATH


class Experiment(ABC):
    """
    Abstract base class representing an experimental dataset in the databank.

    This class provides an interface for interacting with experiment-related
    files, which are stored in a dedicated folder within the databank's
    `Experiments` directory. It handles loading metadata and provides
    access to the experiment's properties.
    """

    _exp_id: str
    _metadata: dict | None = None

    def __init__(self, exp_id: str):
        """
        Initializes the Experiment object.

        :param exp_id: The unique identifier for the experiment, which also
                       corresponds to its directory name.
        """
        self._exp_id = exp_id
        self._populate_meta_data()

    def _get_path(self) -> str:
        """
        Return the absolute path to the experiment's directory.

        :return: The path to the experiment's data folder.
        """
        return os.path.join(NMLDB_EXP_PATH, self._exp_id)

    def _populate_meta_data(self) -> None:
        """
        Populate metadata for the experiment from its README.yaml file.

        This method loads the `README.yaml` file from the experiment's
        directory. If the file is not found, it raises a FileNotFoundError.
        """
        self._metadata = {}
        meta_path = os.path.join(self._get_path(), "README.yaml")
        if os.path.isfile(meta_path):
            with open(meta_path) as yaml_file:
                self._metadata = yaml.load(yaml_file, Loader=yaml.FullLoader)
        else:
            raise FileNotFoundError(f"Metadata file (README.yaml) not found for experiment '{self._exp_id}'.")

    @property
    def metadata(self) -> dict:
        """
        Provides access to the experiment's metadata.

        :return: A dictionary containing the metadata from the README.yaml file.
        """
        if self._metadata is None:
            self._populate_meta_data()
        return self._metadata

    @property
    def id(self) -> str:
        """
        The unique identifier of the experiment.
        """
        return self._exp_id

    def __getitem__(self, key: str):
        """
        Allows dictionary-style access to the metadata.
        """
        return self.metadata[key]

    def __repr__(self):
        return f"{type(self).__name__}(id='{self.id}')"

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id.upper() == other.id.upper()

    def __hash__(self):
        return hash(self.id.upper())
