# `sample_package`

## Table of Contents

- 🅼 [sample_package](#sample_package)
- 🅼 [sample_package.core](#sample_package-core)
- 🅼 [sample_package.exotic](#sample_package-exotic)
- 🅼 [sample_package.exotic.advanced_types](#sample_package-exotic-advanced_types)
- 🅼 [sample_package.exotic.deep](#sample_package-exotic-deep)
- 🅼 [sample_package.exotic.deep.recursive](#sample_package-exotic-deep-recursive)
- 🅼 [sample_package.exotic.descriptors](#sample_package-exotic-descriptors)
- 🅼 [sample_package.exotic.protocols](#sample_package-exotic-protocols)
- 🅼 [sample_package.models](#sample_package-models)
- 🅼 [sample_package.utils](#sample_package-utils)

<a name="sample_package"></a>
## 🅼 sample_package

Sample package for testing docstring to markdown conversion\.

This package contains various Python constructs with different docstring formats
to test the python-docstring-markdown package\.

Available modules:
    - core: Core functionality with Google-style docstrings
    - utils: Utility functions with ReST-style docstrings
    - models: Data models with Numpydoc-style docstrings

- **[Exports](#sample_package-exports)**

<a name="sample_package-exports"></a>
### Exports

- 🅼 [`core`](#sample_package-core)
- 🅼 [`utils`](#sample_package-utils)
- 🅼 [`models`](#sample_package-models)
<a name="sample_package-core"></a>
## 🅼 sample_package.core

Core functionality module using Google-style docstrings\.

This module demonstrates Google-style docstrings with various Python constructs
including nested classes, methods, and functions\.

- **Functions:**
  - 🅵 [batch_process](#sample_package-core-batch_process)
- **Classes:**
  - 🅲 [DataProcessor](#sample_package-core-DataProcessor)
    - 🅲 [Config](#sample_package-core-DataProcessor-Config)

### Functions

<a name="sample_package-core-batch_process"></a>
### 🅵 sample_package.core.batch_process

```python
def batch_process(processor: DataProcessor, items: List[Any]) -> Dict[str, List[Any]]:
```

Batch process items using a DataProcessor\.

This is a module-level function demonstrating Google-style docstrings\.

**Parameters:**

- **processor**: DataProcessor instance to use
- **items**: List of items to process

**Returns:**

- `Dictionary containing`: - 'processed': List of processed items
- 'errors': List of items that failed processing

### Classes

<a name="sample_package-core-DataProcessor"></a>
### 🅲 sample_package.core.DataProcessor

```python
class DataProcessor:
```

Main data processing class\.

This class demonstrates nested class definitions and various method types\.

**Attributes:**

- **name**: The name of the processor
- **config**: Configuration dictionary

**Functions:**

<a name="sample_package-core-DataProcessor-__init__"></a>
#### 🅵 sample_package.core.DataProcessor.__init__

```python
def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
```

Initialize the DataProcessor\.

**Parameters:**

- **name**: Name of the processor
- **config**: Optional configuration dictionary
<a name="sample_package-core-DataProcessor-process"></a>
#### 🅵 sample_package.core.DataProcessor.process

```python
def process(self, data: List[Any]) -> List[Any]:
```

Process the input data\.

**Parameters:**

- **data**: List of data items to process

**Returns:**

- Processed data items

**Raises:**

- **ValueError**: If data is empty

<a name="sample_package-core-DataProcessor-Config"></a>
### 🅲 sample_package.core.DataProcessor.Config

```python
class Config:
```

Nested configuration class\.

This demonstrates nested class documentation\.

**Functions:**

<a name="sample_package-core-DataProcessor-Config-__init__"></a>
#### 🅵 sample_package.core.DataProcessor.Config.__init__

```python
def __init__(self):
```

Initialize Config object\.
<a name="sample_package-core-DataProcessor-Config-update"></a>
#### 🅵 sample_package.core.DataProcessor.Config.update

```python
def update(self, settings: Dict[str, Any]) -> None:
```

Update configuration settings\.

**Parameters:**

- **settings**: Dictionary of settings to update
<a name="sample_package-exotic"></a>
## 🅼 sample_package.exotic

Exotic module demonstrating advanced Python features and docstring styles\.

This module showcases various Python features including:
    - Type hints with Protocol and TypeVar
    - Async functions and context managers
    - Descriptors and metaclasses
    - Mixed docstring styles \(Google, ReST, and Numpydoc\)

- **[Exports](#sample_package-exotic-exports)**

<a name="sample_package-exotic-exports"></a>
### Exports

- 🅼 [`advanced_types`](#sample_package-exotic-advanced_types)
- 🅼 [`protocols`](#sample_package-exotic-protocols)
- 🅼 [`descriptors`](#sample_package-exotic-descriptors)
<a name="sample_package-exotic-advanced_types"></a>
## 🅼 sample_package.exotic.advanced_types

Advanced type hints and generic types demonstration\.

This module uses various type hints and generic types to showcase
complex typing scenarios\.

- **Constants:**
  - 🆅 [T](#sample_package-exotic-advanced_types-T)
  - 🆅 [S](#sample_package-exotic-advanced_types-S)
- **Classes:**
  - 🅲 [Serializable](#sample_package-exotic-advanced_types-Serializable)

### Constants

<a name="sample_package-exotic-advanced_types-T"></a>
### 🆅 sample_package.exotic.advanced_types.T

```python
T = TypeVar('T')
```
<a name="sample_package-exotic-advanced_types-S"></a>
### 🆅 sample_package.exotic.advanced_types.S

```python
S = TypeVar('S', bound='Serializable')
```

### Classes

<a name="sample_package-exotic-advanced_types-Serializable"></a>
### 🅲 sample_package.exotic.advanced_types.Serializable

```python
class Serializable(Generic[T]):
```

A generic serializable container\.

Type Parameters
--------------
T
    The type of value being stored

**Attributes:**

- **value** (`T`): The contained value
- **created_at** (`datetime`): Timestamp of creation

**Functions:**

<a name="sample_package-exotic-advanced_types-Serializable-__init__"></a>
#### 🅵 sample_package.exotic.advanced_types.Serializable.__init__

```python
def __init__(self, value: T):
```
<a name="sample_package-exotic-advanced_types-Serializable-serialize"></a>
#### 🅵 sample_package.exotic.advanced_types.Serializable.serialize

```python
def serialize(self) -> dict:
```

Convert the container to a dictionary\.

**Returns:**

- `dict`: A dictionary containing the value and metadata
<a name="sample_package-exotic-deep"></a>
## 🅼 sample_package.exotic.deep
<a name="sample_package-exotic-deep-recursive"></a>
## 🅼 sample_package.exotic.deep.recursive

A little recursive module using ReST-style docstrings\.

This module demonstrates ReST-style docstrings with various utility functions\.

- **Classes:**
  - 🅲 [Serializable](#sample_package-exotic-deep-recursive-Serializable)

### Classes

<a name="sample_package-exotic-deep-recursive-Serializable"></a>
### 🅲 sample_package.exotic.deep.recursive.Serializable

```python
class Serializable:
```

**Functions:**

<a name="sample_package-exotic-deep-recursive-Serializable-__init__"></a>
#### 🅵 sample_package.exotic.deep.recursive.Serializable.__init__

```python
def __init__(self, data: Dict[str, Any]) -> None:
```

Initialize a Serializable object\.

**Parameters:**

- **data**: Data to serialize
<a name="sample_package-exotic-deep-recursive-Serializable-serialize"></a>
#### 🅵 sample_package.exotic.deep.recursive.Serializable.serialize

```python
def serialize(self) -> Dict[str, Any]:
```

Serialize the object to a dictionary\.

**Returns:**

- `Dict[str, Any]`: Dictionary representation of the object
<a name="sample_package-exotic-descriptors"></a>
## 🅼 sample_package.exotic.descriptors

Descriptors and metaclasses demonstration\.

This module shows how to use descriptors and metaclasses
with proper documentation\.

- **Classes:**
  - 🅲 [ValidatedField](#sample_package-exotic-descriptors-ValidatedField)

### Classes

<a name="sample_package-exotic-descriptors-ValidatedField"></a>
### 🅲 sample_package.exotic.descriptors.ValidatedField

```python
class ValidatedField:
```

A descriptor that validates its values\.

**Parameters:**

- **validator** (`callable`): A function that takes a value and returns True if valid
- **error_message** (`str`): Message to display when validation fails

**Functions:**

<a name="sample_package-exotic-descriptors-ValidatedField-__init__"></a>
#### 🅵 sample_package.exotic.descriptors.ValidatedField.__init__

```python
def __init__(self, validator, error_message):
```
<a name="sample_package-exotic-descriptors-ValidatedField-__get__"></a>
#### 🅵 sample_package.exotic.descriptors.ValidatedField.__get__

```python
def __get__(self, instance, owner):
```

Get the field value\.

**Parameters:**

- **instance**: The instance being accessed
- **owner**: The owner class

**Returns:**

- The field value
<a name="sample_package-exotic-descriptors-ValidatedField-__set__"></a>
#### 🅵 sample_package.exotic.descriptors.ValidatedField.__set__

```python
def __set__(self, instance, value):
```

Set and validate the field value\.

**Parameters:**

- **instance**: The instance being modified
- **value**: The new value to set

**Raises:**

- **ValueError**: If the value fails validation
<a name="sample_package-exotic-protocols"></a>
## 🅼 sample_package.exotic.protocols

Protocol and structural subtyping examples\.

This module demonstrates the use of Protocol for structural subtyping
and abstract base classes\.

- **Classes:**
  - 🅲 [Loggable](#sample_package-exotic-protocols-Loggable)

### Classes

<a name="sample_package-exotic-protocols-Loggable"></a>
### 🅲 sample_package.exotic.protocols.Loggable

```python
class Loggable(Protocol):
```

Protocol for objects that can be logged\.

**Functions:**

<a name="sample_package-exotic-protocols-Loggable-log_format"></a>
#### 🅵 sample_package.exotic.protocols.Loggable.log_format

```python
def log_format(self) -> str:
```

Format the object for logging\.

**Returns:**

- A string representation of the object
<a name="sample_package-models"></a>
## 🅼 sample_package.models

Models module using Numpydoc-style docstrings\.

This module demonstrates Numpydoc-style docstrings with data model classes\.

- **Classes:**
  - 🅲 [BaseModel](#sample_package-models-BaseModel)
  - 🅲 [User](#sample_package-models-User)

### Classes

<a name="sample_package-models-BaseModel"></a>
### 🅲 sample_package.models.BaseModel

```python
class BaseModel:
```

Base model class for all data models\.

**Attributes:**

- **id** (`str`): Unique identifier
- **created_at** (`datetime`): Creation timestamp

**Functions:**

<a name="sample_package-models-BaseModel-to_dict"></a>
#### 🅵 sample_package.models.BaseModel.to_dict

```python
def to_dict(self) -> Dict[str, Any]:
```

Convert model to dictionary\.

**Returns:**

- `Dict[str, Any]`: Dictionary representation of the model
<a name="sample_package-models-User"></a>
### 🅲 sample_package.models.User

```python
class User(BaseModel):
```

User model representing system users\.

**Functions:**

<a name="sample_package-models-User-__init__"></a>
#### 🅵 sample_package.models.User.__init__

```python
def __init__(self, id: str, username: str, email: str, active: bool = True):
```

**Parameters:**

- **id** (`str`): Unique identifier for the user
- **username** (`str`): User's username
- **email** (`str`): User's email address
- **active** (`bool`) (default: `True`): Whether the user is active, by default True

**Attributes:**

- **username** (`str`): User's username
- **email** (`str`): User's email address
- **active** (`bool`): User's active status
<a name="sample_package-models-User-to_dict"></a>
#### 🅵 sample_package.models.User.to_dict

```python
def to_dict(self) -> Dict[str, Any]:
```

Convert user to dictionary\.

**Returns:**

- `Dict[str, Any]`: Dictionary containing all user fields
<a name="sample_package-utils"></a>
## 🅼 sample_package.utils

Utility functions module using ReST-style docstrings\.

This module demonstrates ReST-style docstrings with various utility functions\.

- **Functions:**
  - 🅵 [load_json](#sample_package-utils-load_json)
  - 🅵 [validate_data](#sample_package-utils-validate_data)
- **Classes:**
  - 🅲 [ValidationError](#sample_package-utils-ValidationError)

### Functions

<a name="sample_package-utils-load_json"></a>
### 🅵 sample_package.utils.load_json

```python
def load_json(filepath: str) -> Dict[str, Any]:
```

Load and parse a JSON file\.

**Parameters:**

- **filepath** (`str`): Path to the JSON file

**Returns:**

- `dict`: Parsed JSON content as a dictionary

**Raises:**

- **FileNotFoundError**: If the file doesn't exist
- **json.JSONDecodeError**: If the file contains invalid JSON
<a name="sample_package-utils-validate_data"></a>
### 🅵 sample_package.utils.validate_data

```python
def validate_data(data: Any, schema: Dict[str, Any]) -> List[str]:
```

Validate data against a schema\.

This function demonstrates multi-paragraph ReST docstrings\.

The schema should be a dictionary defining the expected structure
and types of the data\.

**Parameters:**

- **data**: Data to validate
- **schema**: Schema to validate against

**Returns:**

- List of validation errors, empty if valid

### Classes

<a name="sample_package-utils-ValidationError"></a>
### 🅲 sample_package.utils.ValidationError

```python
class ValidationError(Exception):
```

Custom exception for validation errors\.

**Parameters:**

- **message**: Error message
- **errors**: List of specific validation errors
Example::

    raise ValidationError\("Invalid data", \["field1 is required"\]\)

**Functions:**

<a name="sample_package-utils-ValidationError-__init__"></a>
#### 🅵 sample_package.utils.ValidationError.__init__

```python
def __init__(self, message: str, errors: List[str]):
```

Initialize ValidationError\.

**Parameters:**

- **message**: Error message
- **errors**: List of validation errors
