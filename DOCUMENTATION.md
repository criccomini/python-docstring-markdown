# `python_docstring_markdown`

## Table of Contents

- 🅼 [python\_docstring\_markdown](#python_docstring_markdown)
- 🅼 [python\_docstring\_markdown\.\_\_main\_\_](#python_docstring_markdown-__main__)
- 🅼 [python\_docstring\_markdown\.generate](#python_docstring_markdown-generate)

<a name="python_docstring_markdown"></a>
## 🅼 python\_docstring\_markdown

- **[Exports](#python_docstring_markdown-exports)**

<a name="python_docstring_markdown-exports"></a>
### Exports

- 🅼 [`crawl_package`](#python_docstring_markdown-crawl_package)
<a name="python_docstring_markdown-__main__"></a>
## 🅼 python\_docstring\_markdown\.\_\_main\_\_
<a name="python_docstring_markdown-generate"></a>
## 🅼 python\_docstring\_markdown\.generate

This script crawls a Python package directory, extracts docstrings from modules,

classes, functions, methods, and constants using the \`ast\` module, and stores them in the associated data classes\.

Additional features:
  - For each \_\_init\_\_\.py, if an \_\_all\_\_ is defined, an exports list is generated\.
  - Headers have HTML anchors derived from the fully qualified names\.
  - For each function/method, its signature is included with type hints \(if present\) and its return type\.
  - Autodetects docstring formats \(Google-style, NumPy-style, etc\.\) and reformats them into Markdown\.
  - Constants are detected and their types are included when available\.
  - Parameter and return sections now include type information when available\.

- **Functions:**
  - 🅵 [should\_include](#python_docstring_markdown-generate-should_include)
  - 🅵 [get\_string\_value](#python_docstring_markdown-generate-get_string_value)
  - 🅵 [build\_signature](#python_docstring_markdown-generate-build_signature)
  - 🅵 [parse\_function](#python_docstring_markdown-generate-parse_function)
  - 🅵 [parse\_class](#python_docstring_markdown-generate-parse_class)
  - 🅵 [parse\_module\_docstring](#python_docstring_markdown-generate-parse_module_docstring)
  - 🅵 [parse\_module\_exports](#python_docstring_markdown-generate-parse_module_exports)
  - 🅵 [parse\_module\_constants](#python_docstring_markdown-generate-parse_module_constants)
  - 🅵 [parse\_module\_functions](#python_docstring_markdown-generate-parse_module_functions)
  - 🅵 [parse\_module\_classes](#python_docstring_markdown-generate-parse_module_classes)
  - 🅵 [parse\_module\_submodules](#python_docstring_markdown-generate-parse_module_submodules)
  - 🅵 [parse\_module](#python_docstring_markdown-generate-parse_module)
  - 🅵 [crawl\_package](#python_docstring_markdown-generate-crawl_package)
  - 🅵 [escaped\_markdown](#python_docstring_markdown-generate-escaped_markdown)
  - 🅵 [main](#python_docstring_markdown-generate-main)
- **Classes:**
  - 🅲 [DocumentedItem](#python_docstring_markdown-generate-DocumentedItem)
  - 🅲 [Package](#python_docstring_markdown-generate-Package)
  - 🅲 [Module](#python_docstring_markdown-generate-Module)
  - 🅲 [Class](#python_docstring_markdown-generate-Class)
  - 🅲 [Function](#python_docstring_markdown-generate-Function)
  - 🅲 [Constant](#python_docstring_markdown-generate-Constant)
  - 🅲 [MarkdownRenderer](#python_docstring_markdown-generate-MarkdownRenderer)

### Functions

<a name="python_docstring_markdown-generate-should_include"></a>
### 🅵 python\_docstring\_markdown\.generate\.should\_include

```python
def should_include(name: str, include_private: bool) -> bool:
```

Returns True if the given name should be included based on the value

of include\_private\. Always include dunder names like \_\_init\_\_\.
<a name="python_docstring_markdown-generate-get_string_value"></a>
### 🅵 python\_docstring\_markdown\.generate\.get\_string\_value

```python
def get_string_value(node: ast.AST) -> str | None:
```

Extract a string from an AST node representing a constant\.
<a name="python_docstring_markdown-generate-build_signature"></a>
### 🅵 python\_docstring\_markdown\.generate\.build\_signature

```python
def build_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
```

Construct a signature string for a function/method from its AST node\.
<a name="python_docstring_markdown-generate-parse_function"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_function

```python
def parse_function(node: ast.FunctionDef | ast.AsyncFunctionDef, file_path: Path, parent: Class | Module) -> Function:
```

Parse a function or method node into a Function dataclass instance\.
<a name="python_docstring_markdown-generate-parse_class"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_class

```python
def parse_class(node: ast.ClassDef, parent: Module | Class, file_path: Path, include_private: bool) -> Class:
```

Parse a class node into a Class dataclass instance and process its methods and nested classes\.
<a name="python_docstring_markdown-generate-parse_module_docstring"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module\_docstring

```python
def parse_module_docstring(module_ast: ast.Module) -> docstring_parser.Docstring | None:
```

Extract and parse the module docstring\.
<a name="python_docstring_markdown-generate-parse_module_exports"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module\_exports

```python
def parse_module_exports(module_ast: ast.Module) -> list[str]:
```

Extract \_\_all\_\_ exports from an \_\_init\_\_\.py module if present\.
<a name="python_docstring_markdown-generate-parse_module_constants"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module\_constants

```python
def parse_module_constants(module_ast: ast.Module, module: Module, file_path: Path, include_private: bool) -> None:
```

Parse constants defined in a module\.

A constant is considered any assignment at module level whose target is a Name in ALL CAPS,
excluding \_\_all\_\_\. Supports both regular assignments \(with optional type comments\)
and annotated assignments\.
<a name="python_docstring_markdown-generate-parse_module_functions"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module\_functions

```python
def parse_module_functions(module_ast: ast.Module, module: Module, file_path: Path, include_private: bool) -> None:
```

Parse top-level functions in a module\.
<a name="python_docstring_markdown-generate-parse_module_classes"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module\_classes

```python
def parse_module_classes(module_ast: ast.Module, module: Module, file_path: Path, include_private: bool) -> None:
```

Parse classes in a module\.
<a name="python_docstring_markdown-generate-parse_module_submodules"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module\_submodules

```python
def parse_module_submodules(module: Module, file_path: Path, include_private: bool) -> None:
```

Parse submodules of a module\.
<a name="python_docstring_markdown-generate-parse_module"></a>
### 🅵 python\_docstring\_markdown\.generate\.parse\_module

```python
def parse_module(file_path: Path, fully_qualified_name: str, include_private: bool) -> Module:
```

Parse a single module file into a Module dataclass instance\.
<a name="python_docstring_markdown-generate-crawl_package"></a>
### 🅵 python\_docstring\_markdown\.generate\.crawl\_package

```python
def crawl_package(package_path: Path, include_private: bool = False) -> Package:
```

Recursively crawl the package directory, parsing each \.py or \.pyi file as a Module\.

If include\_private is False, items \(functions, classes, constants, submodules\)
whose names start with a single underscore \(but not dunder names like \_\_init\_\_\)
are excluded\.
<a name="python_docstring_markdown-generate-escaped_markdown"></a>
### 🅵 python\_docstring\_markdown\.generate\.escaped\_markdown

```python
def escaped_markdown(text: str) -> str:
```
<a name="python_docstring_markdown-generate-main"></a>
### 🅵 python\_docstring\_markdown\.generate\.main

```python
def main() -> None:
```

### Classes

<a name="python_docstring_markdown-generate-DocumentedItem"></a>
### 🅲 python\_docstring\_markdown\.generate\.DocumentedItem

```python
class DocumentedItem(Protocol):
```
<a name="python_docstring_markdown-generate-Package"></a>
### 🅲 python\_docstring\_markdown\.generate\.Package

```python
class Package:
```
<a name="python_docstring_markdown-generate-Module"></a>
### 🅲 python\_docstring\_markdown\.generate\.Module

```python
class Module:
```
<a name="python_docstring_markdown-generate-Class"></a>
### 🅲 python\_docstring\_markdown\.generate\.Class

```python
class Class:
```
<a name="python_docstring_markdown-generate-Function"></a>
### 🅲 python\_docstring\_markdown\.generate\.Function

```python
class Function:
```
<a name="python_docstring_markdown-generate-Constant"></a>
### 🅲 python\_docstring\_markdown\.generate\.Constant

```python
class Constant:
```
<a name="python_docstring_markdown-generate-MarkdownRenderer"></a>
### 🅲 python\_docstring\_markdown\.generate\.MarkdownRenderer

```python
class MarkdownRenderer:
```

**Functions:**

<a name="python_docstring_markdown-generate-MarkdownRenderer-render"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render

```python
def render(self, package: Package, output_path: Path | None = None) -> None:
```

Render the given package as Markdown\. If output\_path is None or '-', output to stdout\.

If output\_path is a directory, each module gets its own file; otherwise, all modules go into one file\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-render_constant"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render\_constant

```python
def render_constant(self, const: Constant, level: int = 2) -> list[str]:
```
<a name="python_docstring_markdown-generate-MarkdownRenderer-render_module"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render\_module

```python
def render_module(self, module: Module, level: int = 2, is_one_file: bool = True) -> list[str]:
```

Render a module section that includes the module's signature \(if any\), its docstring details,

and a table of contents linking to its classes, functions, constants, exports, and submodules\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-render_class_toc"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render\_class\_toc

```python
def render_class_toc(self, module: Module, cls: Class, indent: int) -> list[str]:
```

Render a TOC entry for a class and its nested classes\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-render_class_details"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render\_class\_details

```python
def render_class_details(self, cls: Class, level: int) -> list[str]:
```

Render detailed documentation for a class including its signature, docstring details,

its methods, and any nested classes\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-render_function"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render\_function

```python
def render_function(self, func: Function, level: int) -> list[str]:
```

Render detailed documentation for a function/method including its signature and

docstring details \(parameters, returns, raises, etc\.\)\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-render_docstring"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.render\_docstring

```python
def render_docstring(self, doc: docstring_parser.Docstring, indent: int = 0) -> list[str]:
```

Render detailed docstring information including description, parameters,

returns, raises, and attributes\. An indent level can be provided for nested output\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-anchor"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.anchor

```python
def anchor(self, fq_name: str) -> str:
```

Generate a sanitized anchor from a fully qualified name\.

This implementation replaces dots with hyphens\.
<a name="python_docstring_markdown-generate-MarkdownRenderer-link"></a>
#### 🅵 python\_docstring\_markdown\.generate\.MarkdownRenderer\.link

```python
def link(self, module: Module, item: DocumentedItem | None = None, is_in_file: bool = True) -> str:
```

Generate a link to a fully qualified name\.
