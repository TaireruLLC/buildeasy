# buildeasy/buildeasy.py
"""Main code for 'buildeasy' Python package which allows the user to make files into classes."""

import sys
import inspect
import pickle
from functools import wraps
from typing import List, Optional

# Custom exception for handling transformation errors in the module.
class TransformationError(Exception):
    pass

class FileAsClass:
    # A cache to hold instances of transformed modules.
    _cache = {}

    def __init_subclass__(cls, **init_kwargs):
        """
        This is a special method that gets invoked when a class is subclassed. 
        It is used here to transform a regular Python file into a class instance.
        This transformation involves capturing public methods, setting default 
        arguments, injecting static and class methods, and caching the result.
        
        Arguments:
        - **init_kwargs: Arbitrary keyword arguments that may be passed during 
          class instantiation.
        
        The method performs several actions:
        1. Fetches the module's name and determines if the transformation 
           has already been cached.
        2. Builds the `init_args` based on the class's `__init__` signature.
        3. Instantiates the class and injects static/class methods.
        4. Sets `__all__` to expose public methods and class instance.
        5. Copies key module attributes to the class instance.
        6. Handles method resolution order (MRO) to bring inherited methods.
        7. Caches the transformed module instance.
        """
        super().__init_subclass__(**init_kwargs)  # Call the parent class's __init_subclass__()

        # Obtain the caller's frame to inspect the module's details
        caller_frame = sys._getframe(1)
        module_name = caller_frame.f_globals.get('__name__')

        if module_name is None:
            raise RuntimeError("Cannot determine module name from caller's frame.")
        module = sys.modules[module_name]  # Fetch the module object using its name.

        # Handle caching: Return the cached instance if the module has already been transformed.
        if module_name in FileAsClass._cache:
            return FileAsClass._cache[module_name]

        # Prepare initialization arguments based on class's __init__ signature
        init_signature = inspect.signature(cls.__init__)  # Inspect the __init__ method of the class
        parameters = list(init_signature.parameters.values())[1:]  # Skip 'self'
        init_args = {}

        # Collect arguments: if provided in init_kwargs, use them; otherwise use defaults (or None)
        for param in parameters:
            if param.name in init_kwargs:
                init_args[param.name] = init_kwargs[param.name]
            elif param.default is not param.empty:
                init_args[param.name] = param.default
            else:
                init_args[param.name] = None  # Default to None if no value and no default

        # Instantiate the class using the prepared arguments
        try:
            instance = cls(**init_args)
        except TypeError as e:
            # If instantiation fails, raise a TransformationError with detailed info
            raise TransformationError(f"Error instantiating {cls.__name__}: {e}") from e

        # Gather public methods (instance methods) from the class.
        public_methods = []
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value) and not attr_name.startswith("_"):
                public_methods.append(attr_name)

        # Inject static and class methods into the instance
        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, staticmethod):
                setattr(instance, attr_name, attr_value)
            elif isinstance(attr_value, classmethod):
                setattr(instance, attr_name, attr_value)

        # Set up `__all__` attribute (listing public methods and the instance itself)
        instance.__all__ = public_methods + ['instance']
        instance.instance = instance  # Add an 'instance' attribute pointing to the current instance

        # Copy key module-level attributes to the instance (e.g., '__name__', '__file__', etc.)
        for attr in ("__name__", "__package__", "__loader__", "__spec__", "__file__"):
            setattr(instance, attr, getattr(module, attr, None))

        # Handle mixins and multiple inheritance (MRO)
        for base_cls in cls.__mro__:
            if base_cls is not cls:  # Skip the current class itself
                for method_name, method_value in base_cls.__dict__.items():
                    if callable(method_value) and not method_name.startswith("_"):
                        setattr(instance, method_name, method_value)

        # Cache the transformed instance so it doesn't get reprocessed
        sys.modules[module_name] = instance
        FileAsClass._cache[module_name] = instance

        return instance  # Return the transformed class instance

    def add_dynamic_method(cls, method_name: str, method: callable):
        """
        Dynamically add a method to the transformed class instance.
        
        Arguments:
        - method_name (str): The name of the method to be added.
        - method (callable): The method function to be added.

        This method allows adding methods to the instance of the class, 
        allowing runtime modification of the class's behavior.
        """
        setattr(cls.instance, method_name, method)

    @staticmethod
    def load_from_cache(module_name: str):
        """
        Load a module's instance from cache if available.

        Arguments:
        - module_name (str): The name of the module to retrieve from cache.

        Returns:
        - The cached instance of the module or None if not found.
        """
        return FileAsClass._cache.get(module_name)

    def __getstate__(self):
        """
        Custom serialization method for pickling the instance's state.

        Returns:
        - dict: The state dictionary that can be pickled.
        
        This method allows the instance's state to be serialized into a 
        format that can be saved and restored later.
        """
        state = self.__dict__.copy()  # Make a copy of the instance's __dict__
        # Optionally, exclude large data like file handles or connections that cannot be serialized.
        return state

    def __setstate__(self, state):
        """
        Custom deserialization method to restore the instance's state.

        Arguments:
        - state (dict): The state dictionary that was previously serialized.
        
        This method allows the instance to be restored to its previous state 
        after being unpickled.
        """
        self.__dict__.update(state)  # Restore instance's __dict__ from the saved state

    @classmethod
    def save_to_file(cls, filename: str):
        """
        Save the current state of the class instance to a file using pickle.

        Arguments:
        - filename (str): The name of the file to save the instance to.

        This method serializes the instance to a file, so it can be loaded 
        later with `load_from_file()`.
        """
        with open(filename, 'wb') as f:
            pickle.dump(cls.instance, f)

    @classmethod
    def load_from_file(cls, filename: str):
        """
        Load the class instance's state from a file.

        Arguments:
        - filename (str): The name of the file to load the instance from.

        This method allows restoring a saved class instance from a file.
        """
        with open(filename, 'rb') as f:
            cls.instance = pickle.load(f)

    @classmethod
    def scan_for_plugins(cls, directory: str, extension: str = ".py"):
        """
        Scan a directory for Python files and dynamically load them as modules.

        Arguments:
        - directory (str): The directory to scan for Python files.
        - extension (str): The file extension to look for (default: ".py").

        This method searches the specified directory for Python files 
        and attempts to import them, transforming them into class instances.
        """
        import os
        for filename in os.listdir(directory):
            if filename.endswith(extension):
                module_name = filename[:-3]  # Remove ".py" extension from filename
                try:
                    module = __import__(module_name)  # Import the module dynamically
                    FileAsClass(module)  # Transform the module into a class
                except Exception as e:
                    # Catch and print errors that occur during plugin loading
                    print(f"Failed to load plugin {module_name}: {e}")

    def __getattribute__(self, name):
        """
        Custom attribute lookup to allow dynamic behavior.

        Arguments:
        - name (str): The name of the attribute to retrieve.

        Returns:
        - The requested attribute's value, or raises an AttributeError if not found.

        This method overrides the default attribute lookup to allow dynamic 
        behavior, such as retrieving a method or performing additional checks 
        before returning the attribute.
        """
        try:
            # First, attempt the normal attribute lookup
            return super().__getattribute__(name)
        except AttributeError:
            # If attribute is not found, check if it is dynamically assigned
            if hasattr(self, name):
                # If it’s a method, it might be a tuple; unpack it if necessary
                if isinstance(getattr(self, name), tuple):
                    return getattr(self, name)[0]
                else:
                    return getattr(self, name)
            else:
                # If not found, raise an AttributeError
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")