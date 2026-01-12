"""
:module: core/experiment.py

:description: Module for handling experimental data entries in the databank.
"""

import json
import os
from abc import ABC, abstractmethod
from collections.abc import MutableSet
from typing import Any

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
    _data: dict | None = None

    def __init__(self, exp_id: str, path: str):
        """
        Initialize the Experiment object.

        :param exp_id: The unique identifier for the experiment, which also
                       corresponds to its directory name.
        :param path: The absolute path to the experiment's directory.
        """
        self._exp_id = exp_id
        self._path = path
        self._populate_meta_data()

    def _get_path(self) -> str:
        """
        Return the absolute path to the experiment's directory.

        :return: The path to the experiment's data folder.
        """
        return self._path

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
            msg = f"Metadata file (README.yaml) not found for experiment '{self._exp_id}'."
            raise FileNotFoundError(msg)

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
    def exp_id(self) -> str:
        """The unique identifier of the experiment."""
        return self._exp_id

    @property
    @abstractmethod
    def data(self) -> dict:
        """Provide access to the experiment's data."""

    @property
    @abstractmethod
    def schema(self) -> str:
        """Path to the JSON schema for validation."""

    def __getitem__(self, key: str):
        """Allow dictionary-style access to the metadata."""
        return self.metadata[key]

    def __repr__(self):
        return f"{type(self).__name__}(id='{self.exp_id}')"

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.exp_id == other.exp_id

    def __hash__(self):
        return hash(self.exp_id)

class OPExperiment(Experiment):
    """
    Represents an order parameter experiment.
    """

    _schema_path = "path/to/op_schema.json"  # Placeholder

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = {}
            for fname in os.listdir(self._get_path()):
                if fname.endswith("_Order_Parameters.json"):
                    molecule_name = fname.replace("_Order_Parameters.json", "")
                    fpath = os.path.join(self._get_path(), fname)
                    with open(fpath) as json_file:
                        self._data[molecule_name] = json.load(json_file)
        return self._data

    def transform_data(self) -> Any:
        """
        Calculates the average order parameter for each molecule.

        :return: A dictionary with molecule names as keys and average order parameters as values.
        """
        transformed_data = {}
        for molecule, data in self.data.items():
            if not data:
                continue
            total_s = 0
            count = 0
            for atom_data in data.values():
                if 'S' in atom_data:
                    total_s += atom_data['S']
                    count += 1
            if count > 0:
                transformed_data[molecule] = total_s / count
        return transformed_data



class FFExperiment(Experiment):
    """
    Represents a form factor experiment.
    """

    _schema_path = "src/DatabankLib/SchemaValidation/Schema/ff_schema.json"  # Placeholder

    @property
    def data(self) -> dict:
        if self._data is None:
            self._data = {}
            for fname in os.listdir(self._get_path()):
                if fname.endswith("_FormFactor.json"):
                    fpath = os.path.join(self._get_path(), fname)
                    with open(fpath) as json_file:
                        self._data = json.load(json_file)
                    break  # Assuming one form factor file per experiment
        return self._data

    def transform_data(self) -> Any:
        """
        Placeholder for data transformation.

        :return: The raw data.
        """
        return self.data

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
            self._ids.add(item.exp_id.upper())
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

class ExperimentCollection(Collection):
    """
    A collection of experiments.
    """

    def _test_item_type(self, item: Any) -> bool:
        return isinstance(item, Experiment)

    def _create_item(self, name: str) -> Experiment:
        raise NotImplementedError("Cannot create an experiment by name. Use load_from_data.")

    @staticmethod
    def load_from_data() -> "ExperimentCollection":
        """
        Load experiment data from the designated directory and returns a set of experiments.
        """
        collection = ExperimentCollection()
        for exp_type, exp_cls in [("OrderParameters", OPExperiment), ("FormFactors", FFExperiment)]:
            path = os.path.join(NMLDB_EXP_PATH, exp_type)
            if not os.path.isdir(path):
                continue
            for subdir, _, files in os.walk(path):
                if "README.yaml" in files:
                    exp_id = os.path.basename(subdir)
                    try:
                        exp = exp_cls(exp_id, subdir)
                        collection.add(exp)
                    except FileNotFoundError:
                        # Log this error?
                        pass
        return collection

    def loc(self, exp_id: str) -> Experiment:
        """
        Locate an experiment by its path-ID.

        :param path-id: ????.
        :return: The Experiment object if found, else None.
        """
        for exp in self:
            if exp.expt_id == exp_id:
                return exp
        msg = f"Experiment with path-ID '{exp_id}' not found in the collection."
        raise KeyError(msg)
