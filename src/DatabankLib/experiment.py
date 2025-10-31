"""
:module: core/experiment.py

:description: Module for handling experimental data entries in the databank.
"""

import os
from abc import ABC, abstractmethod
from collections.abc import MutableSet
from typing import Any

import yaml

from DatabankLib import NMLDB_EXP_PATH


class Collection(MutableSet, ABC):
    """Set repeating normal set functionality with some additional molecule-specific things."""

    def __init__(self, *args):
        """Initialize the LipidSet with optional initial elements."""
        self._items = set()
        self._ids = set()
        for arg in args:
            self.add(arg)

    @abstractmethod
    def _test_item_type(self, item: Any) -> bool:
        """
        Test if item is of proper Molecule type

        :param item: any type variable
        :return: bool answer
        """

    @abstractmethod
    def _create_item(self, name: str) -> "Experiment":
        """
        Construct the molecule of the proper type

        :param name: unique name of the molecule
        :return: constructed Molecule
        """

    def __contains__(self, item: "Experiment"):
        """Check if a lipid is in the set."""
        return (self._test_item_type(item) and item in self._items) or (
            isinstance(item, str) and item.upper() in self._ids
        )

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def add(self, item: "Experiment"):
        """
        Add a lipid to the set.

        :param item: Can add either Molecule or str (then Molecule constructor
                     will be called)
        """
        if self._test_item_type(item):
            self._items.add(item)
            self._ids.add(item.id.upper())
        elif isinstance(item, str):
            self._items.add(self._create_item(item))  # here we call Lipid constructor
            self._ids.add(item.upper())
        else:
            raise TypeError(f"Only proper instances can be added to {type(self).__name__}.")

    def discard(self, item):
        """
        Remove a lipid from the set without raising an error if it does not exist.
        """
        if self._test_item_type(item):
            self._items.discard(item)
            self._ids.discard(item.id.upper())
        elif isinstance(item, str):
            if item.upper() not in self._ids:
                return
            ifound = None
            for i in self._items:
                if i.id.upper() == item.upper():
                    ifound = i
                    break
            assert ifound is not None
            self._items.discard(ifound)
            self._ids.discard(item.upper())

    def get(self, key: str, default=None) -> "Experiment" | None:
        """
        Get a molecule by its name.
        :param key: The name of the molecule to retrieve.
        :param default: The value to return if the molecule is not found.
        """
        if key.upper() in self._ids:
            for item in self._items:
                if item.id.upper() == key.upper():
                    return item
        return default

    def __repr__(self):
        return f"{type(self).__name__}[{self._ids}]"

    @property
    def ids(self) -> set[str]:
        return self._ids


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
