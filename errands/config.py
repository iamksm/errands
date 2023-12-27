import fnmatch
import os
from importlib.machinery import SourceFileLoader

from errands.executor import (
    LongErrandsExecutor,
    MediumErrandsExecutor,
    ShortErrandsExecutor,
)


class ErrandsConfig:
    """
    A class used to represent the configuration of errands.

    ...

    Attributes
    ----------
    project_base_path : str
        a formatted string to print out the project base path
    current_dir : str
        a formatted string to print out the current directory
    long_errands_executor : obj
        an object of LongErrandsExecutor
    medium_errands_executor : obj
        an object of MediumErrandsExecutor
    short_errands_executor : obj
        an object of ShortErrandsExecutor

    Methods
    -------
    get_package_name(file_path)
        Dynamically determines the package name based on the relative file path.

        Parameters
        ----------
        file_path : str
            The relative file path.

        Returns
        -------
        str
            The package name based on the relative file path.

    auto_discover_errands()
        Discovers errands automatically.
    """

    def __init__(self, project_base_path):
        """
        Initializes an instance of ErrandsConfig with the project base path.
        Calls the auto_discover_errands() method to automatically discover errands.

        Parameters:
        project_base_path (str): The project base path.
        """
        self.project_base_path = project_base_path
        self.current_dir = self.project_base_path
        self.loaded_modules = set()

        self.auto_discover_errands()

        self.long_errands_executor = LongErrandsExecutor
        self.medium_errands_executor = MediumErrandsExecutor
        self.short_errands_executor = ShortErrandsExecutor

    def get_package_name(self, file_path):
        """
        Dynamically determines the package name based on the relative file path.

        Parameters
        ----------
        file_path : str
            The relative file path.

        Returns
        -------
        str
            The package name based on the relative file path.
        """
        rel_path = os.path.splitext(os.path.relpath(file_path))[0]
        package_name = rel_path.replace(os.path.sep, ".")
        return package_name

    def auto_discover_errands(self):
        """
        Discovers errands automatically.

        We expect errands to be in files named tasks.py or *tasks*.py
        """
        for root, dirs, files in os.walk(self.current_dir):
            for file_name in iter(fnmatch.filter(files, "*tasks.py")):
                file_path = os.path.join(root, file_name)

                package_name = self.get_package_name(file_path)
                if file_path not in self.loaded_modules:
                    loader = SourceFileLoader(package_name, file_path)
                    loader.load_module()
                    self.loaded_modules.add(file_path)

            for subdir in iter(dirs):
                subdir_path = os.path.join(root, subdir)
                self.current_dir = subdir_path
                self.auto_discover_errands()

        # Reset current directory once done
        self.current_dir = self.project_base_path
