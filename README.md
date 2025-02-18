**BuildEasy** is a Python package that transforms Python files into class instances dynamically. It enhances modularity by allowing runtime modifications, automatic method injection, and plugin-based loading of modules. Here's a breakdown of its key features and usage:

### **Key Features**
1. **Automatic File-to-Class Conversion**  
   - Python files (`.py`) are converted into class instances when subclassed from `FileAsClass`.
  
2. **Dynamic Method Injection**  
   - Methods can be added dynamically (static, class, or instance methods).
  
3. **Caching for Performance**  
   - Prevents redundant transformations by caching instances.

4. **State Persistence**  
   - Supports saving and loading instances using `pickle`.

5. **Plugin System**  
   - Scans directories for Python files and loads them dynamically.

6. **Custom Attribute Resolution**  
   - Overrides attribute lookups for flexible behavior.

---

### **How It Works**
#### **1. Converting a Python File into a Class**
By subclassing `FileAsClass`, a module (`my_module.py`) is transformed into a class instance:

```python
from buildeasy import FileAsClass

class MyModule(FileAsClass):
    def __init__(self, name="buildeasy"):
        self.name = name

    def greet(self):
        return f"Hello from {self.name}!"
```

Accessing the module (`main.py`):
```python
import my_module

print(my_module.greet())  # Outputs: Hello from my_module.py!
print(my_module.name)  # Outputs: buildeasy
```

---

#### **2. Adding Methods Dynamically**
```python
def farewell():
    return "Goodbye!"

my_module.add_dynamic_method("farewell", farewell)
print(my_module.farewell())  # Outputs: Goodbye!
```

---

#### **3. Saving and Loading Instances**
```python
my_module.save_to_file("module_state.pkl")
loaded_instance = my_module.load_from_file("module_state.pkl")
```

---

#### **4. Scanning for Plugins**
```python
my_module.scan_for_plugins("plugins/")
```

---

### **Why Use BuildEasy?**
- Makes Python files behave like objects with dynamic behaviors.
- Eliminates redundant file imports by turning them into reusable instances.
- Enables plugin-like extensibility by auto-loading modules.

It's especially useful for building **dynamic applications, plugin-based architectures, or frameworks** where Python files need to be loaded and modified at runtime. 🚀