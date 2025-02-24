#!/usr/bin/env python3
"""
This script crawls a Python package directory, extracts docstrings from modules,
classes, functions, methods, and constants using the `ast` module, and stores them in the associated data classes.

Additional features:
  - For each __init__.py, if an __all__ is defined, an exports list is generated.
  - Headers have HTML anchors derived from the fully qualified names.
  - For each function/method, its signature is included with type hints (if present) and its return type.
  - Autodetects docstring formats (Google-style, NumPy-style, etc.) and reformats them into Markdown.
  - Constants are detected and their types are included when available.
  - Parameter and return sections now include type information when available.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import docstring_parser


# Define a protocol for documented items that have a name and fully_qualified_name.
class DocumentedItem(Protocol):
    name: str
    fully_qualified_name: str


@dataclass
class Package:
    path: Path
    name: str  # final name (directory name)
    fully_qualified_name: str  # same as name for the top-level package
    modules: list[Module] = field(default_factory=list)


@dataclass
class Module:
    path: Path
    # final module name (file stem)
    name: str
    # e.g. package_name.module or just package_name for __init__
    fully_qualified_name: str
    submodules: list[Module] = field(default_factory=list)
    docstring: docstring_parser.Docstring | None = None
    constants: list[Constant] = field(default_factory=list)
    functions: list[Function] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)
    exports: list[str] = field(default_factory=list)


@dataclass
class Class:
    path: Path
    # final class name
    name: str
    # e.g. foo.bar.Baz
    fully_qualified_name: str
    signature: str
    docstring: docstring_parser.Docstring | None = None
    functions: list[Function] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)  # For nested classes


@dataclass
class Function:
    path: Path
    name: str  # final function/method name
    fully_qualified_name: str  # e.g. foo.bar.Baz.method
    signature: str
    docstring: docstring_parser.Docstring | None = None


@dataclass
class Constant:
    path: Path
    name: str  # constant name
    fully_qualified_name: str  # e.g. foo.bar.MY_CONSTANT
    value: str  # the string representation of the value
    type: str | None = None  # the constant's type, if available


# --- Helper functions ---


def should_include(name: str, include_private: bool) -> bool:
    """
    Returns True if the given name should be included based on the value
    of include_private. Always include dunder names like __init__.
    """
    if include_private:
        return True
    # Exclude names starting with a single underscore.
    if name.startswith("_") and not (name.startswith("__") and name.endswith("__")):
        return False
    return True


def get_string_value(node: ast.AST) -> str | None:
    """Extract a string from an AST node representing a constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def build_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Construct a signature string for a function/method from its AST node."""
    args = node.args
    param_strings = []

    # Process positional arguments (with or without defaults)
    pos_args = args.args
    num_defaults = len(args.defaults)
    num_no_default = len(pos_args) - num_defaults
    for i, arg in enumerate(pos_args):
        param = arg.arg
        if arg.annotation:
            param += f": {ast.unparse(arg.annotation)}"
        if i >= num_no_default:
            default_val = args.defaults[i - num_no_default]
            param += f" = {ast.unparse(default_val)}"
        param_strings.append(param)

    # Process variable positional arguments (*args)
    if args.vararg:
        vararg = f"*{args.vararg.arg}"
        if args.vararg.annotation:
            vararg += f": {ast.unparse(args.vararg.annotation)}"
        param_strings.append(vararg)

    # Process keyword-only arguments
    for i, arg in enumerate(args.kwonlyargs):
        param = arg.arg
        if arg.annotation:
            param += f": {ast.unparse(arg.annotation)}"
        default = args.kw_defaults[i]
        if default is not None:
            param += f" = {ast.unparse(default)}"
        param_strings.append(param)

    # Process variable keyword arguments (**kwargs)
    if args.kwarg:
        kwarg = f"**{args.kwarg.arg}"
        if args.kwarg.annotation:
            kwarg += f": {ast.unparse(args.kwarg.annotation)}"
        param_strings.append(kwarg)

    params = ", ".join(param_strings)
    ret = ""
    if node.returns:
        ret = f" -> {ast.unparse(node.returns)}"
    return f"{node.name}({params}){ret}"


def parse_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    file_path: Path,
    parent: Class | Module,
) -> Function:
    """Parse a function or method node into a Function dataclass instance."""
    signature = build_signature(node)
    raw_doc = ast.get_docstring(node)
    parsed_doc = docstring_parser.parse(raw_doc) if raw_doc else None
    fq_name = f"{parent.fully_qualified_name}.{node.name}"
    return Function(
        path=file_path,
        name=node.name,
        fully_qualified_name=fq_name,
        signature=f"def {signature}:",
        docstring=parsed_doc,
    )


def parse_class(
    node: ast.ClassDef, parent: Module | Class, file_path: Path, include_private: bool
) -> Class:
    """Parse a class node into a Class dataclass instance and process its methods and nested classes."""
    raw_doc = ast.get_docstring(node)
    parsed_doc = docstring_parser.parse(raw_doc) if raw_doc else None
    fq_name = f"{parent.fully_qualified_name}.{node.name}"
    # Build a signature for the class, including base classes if any.
    if node.bases:
        bases = ", ".join(ast.unparse(base) for base in node.bases)
        signature = f"class {node.name}({bases}):"
    else:
        signature = f"class {node.name}:"
    cls = Class(
        path=file_path,
        name=node.name,
        fully_qualified_name=fq_name,
        signature=signature,
        docstring=parsed_doc,
        functions=[],
        classes=[],
    )
    # Process methods and nested classes.
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not should_include(child.name, include_private):
                continue
            method = parse_function(child, file_path, parent=cls)
            cls.functions.append(method)
        elif isinstance(child, ast.ClassDef):
            if not should_include(child.name, include_private):
                continue
            nested_cls = parse_class(
                child, parent=cls, file_path=file_path, include_private=include_private
            )
            cls.classes.append(nested_cls)
    return cls


def parse_module_docstring(module_ast: ast.Module) -> docstring_parser.Docstring | None:
    """Extract and parse the module docstring."""
    raw_doc = ast.get_docstring(module_ast)
    return docstring_parser.parse(raw_doc) if raw_doc else None


def parse_module_exports(module_ast: ast.Module) -> list[str]:
    """Extract __all__ exports from an __init__.py module if present."""
    exports: list[str] = []
    for node in module_ast.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(node.value, (ast.List, ast.Tuple)):
                        for elt in node.value.elts:
                            value = get_string_value(elt)
                            if value:
                                exports.append(value)
                    break
    return exports


def parse_module_constants(
    module_ast: ast.Module,
    module: Module,
    file_path: Path,
    include_private: bool,
) -> None:
    """Parse constants defined in a module.

    A constant is considered any assignment at module level whose target is a Name in ALL CAPS,
    excluding __all__. Supports both regular assignments (with optional type comments)
    and annotated assignments.
    """
    for node in module_ast.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            # Process ast.Assign nodes (may have multiple targets).
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id.isupper()
                        and target.id != "__ALL__"
                        and should_include(target.id, include_private)
                    ):
                        type_annotation = None
                        if hasattr(node, "type_comment") and node.type_comment:
                            type_annotation = node.type_comment
                        value = ast.unparse(node.value)
                        fq_name = f"{module.fully_qualified_name}.{target.id}"
                        constant = Constant(
                            path=file_path,
                            name=target.id,
                            fully_qualified_name=fq_name,
                            value=value,
                            type=type_annotation,
                        )
                        module.constants.append(constant)
                        break
            # Process annotated assignments.
            elif isinstance(node, ast.AnnAssign):
                if (
                    isinstance(node.target, ast.Name)
                    and node.target.id.isupper()
                    and node.target.id != "__ALL__"
                    and should_include(node.target.id, include_private)
                ):
                    type_annotation = (
                        ast.unparse(node.annotation) if node.annotation else None
                    )
                    value = (
                        ast.unparse(node.value) if node.value is not None else "None"
                    )
                    fq_name = f"{module.fully_qualified_name}.{node.target.id}"
                    constant = Constant(
                        path=file_path,
                        name=node.target.id,
                        fully_qualified_name=fq_name,
                        value=value,
                        type=type_annotation,
                    )
                    module.constants.append(constant)


def parse_module_functions(
    module_ast: ast.Module,
    module: Module,
    file_path: Path,
    include_private: bool,
) -> None:
    """Parse top-level functions in a module."""
    for node in module_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not should_include(node.name, include_private):
                continue
            func = parse_function(node, file_path, parent=module)
            module.functions.append(func)


def parse_module_classes(
    module_ast: ast.Module,
    module: Module,
    file_path: Path,
    include_private: bool,
) -> None:
    """Parse classes in a module."""
    for node in module_ast.body:
        if isinstance(node, ast.ClassDef):
            if not should_include(node.name, include_private):
                continue
            cls = parse_class(
                node,
                parent=module,
                file_path=file_path,
                include_private=include_private,
            )
            module.classes.append(cls)


def parse_module_submodules(
    module: Module,
    file_path: Path,
    include_private: bool,
) -> None:
    """Parse submodules of a module."""
    for file_path in file_path.parent.iterdir():
        init_py = file_path / "__init__.py"
        if init_py.is_file():
            submodule = parse_module(
                init_py,
                f"{module.fully_qualified_name}.{file_path.name}",
                include_private,
            )
            module.submodules.append(submodule)
        elif file_path.suffix == ".py" and file_path.stem != "__init__":
            if (
                not include_private
                and file_path.name.startswith("_")
                and not file_path.name.startswith("__")
            ):
                continue
            submodule = parse_module(
                file_path,
                f"{module.fully_qualified_name}",
                include_private,
            )
            module.submodules.append(submodule)


def parse_module(
    file_path: Path,
    fully_qualified_name: str,
    include_private: bool,
) -> Module:
    """Parse a single module file into a Module dataclass instance."""
    with file_path.open("r", encoding="utf8") as f:
        source = f.read()
    module_ast = ast.parse(source, filename=str(file_path))
    mod_name = file_path.stem
    if mod_name != "__init__":
        fully_qualified_name = f"{fully_qualified_name}.{mod_name}"
    module = Module(
        path=file_path,
        name=mod_name,
        fully_qualified_name=fully_qualified_name,
        docstring=parse_module_docstring(module_ast),
        constants=[],
        functions=[],
        classes=[],
        exports=[],
    )
    parse_module_constants(module_ast, module, file_path, include_private)
    parse_module_functions(module_ast, module, file_path, include_private)
    parse_module_classes(module_ast, module, file_path, include_private)
    if mod_name == "__init__":
        module.exports = parse_module_exports(module_ast)
        parse_module_submodules(module, file_path, include_private)
    return module


def crawl_package(package_path: Path, include_private: bool = False) -> Package:
    """Recursively crawl the package directory, parsing each .py file as a Module.

    If include_private is False, items (functions, classes, constants, submodules)
    whose names start with a single underscore (but not dunder names like __init__)
    are excluded.
    """
    pkg_name = package_path.name
    package = Package(
        path=package_path, name=pkg_name, fully_qualified_name=pkg_name, modules=[]
    )
    modules = []
    for file_path in package_path.glob("*.py"):
        if (
            not include_private
            and file_path.stem.startswith("_")
            and not file_path.stem.startswith("__")
        ):
            continue
        module = parse_module(file_path, package.fully_qualified_name, include_private)
        if module.name == "__init__":
            modules.append(module)

    # Add all modules to the package (including nested)
    while modules:
        module = modules.pop()
        package.modules.append(module)
        modules.extend(module.submodules)

    # Sort package.modules by fully_qualified_name
    package.modules.sort(key=lambda m: m.fully_qualified_name)

    return package


# --- Renderer Classes ---


_MARKDOWN_CHARACTERS_TO_ESCAPE = set(r"\`*_{}[]<>()#+.!|")


# From https://stackoverflow.com/questions/68699165/how-to-escape-texts-for-formatting-in-python
def escaped_markdown(text: str) -> str:
    return "".join(
        f"\\{character}" if character in _MARKDOWN_CHARACTERS_TO_ESCAPE else character
        for character in text.strip()
    )


class MarkdownRenderer:
    def render(self, package: Package, output_path: Path | None = None) -> None:
        """
        Render the given package as Markdown. If output_path is None or '-', output to stdout.
        If output_path is a directory, each module gets its own file; otherwise, all modules go into one file.
        """
        is_one_file = (
            output_path is None or output_path.is_file() or output_path.suffix != ""
        )
        lines = []
        lines.append(f"# `{package.name}`")
        lines.append("")
        lines.append("## Table of Contents")
        lines.append("")
        for module in package.modules:
            link = self.link(module, is_in_file=is_one_file)
            lines.append(f"- 🅼 [{module.fully_qualified_name}]({link})")
        lines.append("")

        if is_one_file:
            # Render all modules
            for module in package.modules:
                lines.extend(self.render_module(module, is_one_file=is_one_file))
            lines.append("")
            output = "\n".join(lines)
            if output_path is None:
                print(output)
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(output, encoding="utf8")
        elif output_path is not None:
            # If the output path has no suffix, treat it as a directory.
            output_path.mkdir(parents=True, exist_ok=True)
            for module in package.modules:
                file_name = self.link(module, is_in_file=is_one_file)
                module_lines = self.render_module(module, is_one_file=is_one_file)
                module_lines.append("")
                module_output = "\n".join(module_lines)
                file_path = output_path / file_name
                file_path.write_text(module_output, encoding="utf8")
            # Write the index file table of contents linking to each module
            lines.append("")
            (output_path / "index.md").write_text("\n".join(lines), encoding="utf8")

    def render_constant(self, const: Constant, level: int = 2) -> list[str]:
        lines: list[str] = []
        header_prefix = "#" * level
        type_str = f": {const.type}" if const.type else ""
        # Constant header with an HTML anchor.
        lines.append(f'<a name="{self.anchor(const.fully_qualified_name)}"></a>')
        lines.append(f"{header_prefix} 🆅 {const.fully_qualified_name}")
        lines.append("")
        lines.append("```python")
        lines.append(f"{const.name}{type_str} = {const.value}")
        lines.append("```")
        return lines

    def render_module(
        self, module: Module, level: int = 2, is_one_file: bool = True
    ) -> list[str]:
        """
        Render a module section that includes the module's signature (if any), its docstring details,
        and a table of contents linking to its classes, functions, constants, exports, and submodules.
        """
        lines: list[str] = []
        header_prefix = "#" * level
        # Module header with an HTML anchor.
        lines.append(f'<a name="{self.anchor(module.fully_qualified_name)}"></a>')
        lines.append(f"{header_prefix} 🅼 {module.fully_qualified_name}")
        lines.append("")

        # Render module docstring details if available.
        if module.docstring:
            lines.extend(self.render_docstring(module.docstring))
            lines.append("")

        # Second-level table of contents for this module.
        if module.constants:
            lines.append("- **Constants:**")
            for const in module.constants:
                lines.append(
                    "  " * 1 + f"- 🆅 [{const.name}]({self.link(module, const)})"
                )
        if module.functions:
            lines.append("- **Functions:**")
            for func in module.functions:
                lines.append("  " * 1 + f"- 🅵 [{func.name}]({self.link(module, func)})")
        if module.classes:
            lines.append("- **Classes:**")
            for cls in module.classes:
                lines.extend(self.render_class_toc(module, cls, indent=1))
        if module.exports:
            lines.append(
                f"- **[Exports](#{self.anchor(module.fully_qualified_name)}-exports)**"
            )

        if module.constants or module.functions or module.classes or module.exports:
            lines.append("")

        # Detailed sections.
        if module.constants:
            lines.append(f"{header_prefix}# Constants")
            lines.append("")
            for const in module.constants:
                lines.extend(self.render_constant(const, level=level + 1))
            lines.append("")
        if module.functions:
            lines.append(f"{header_prefix}# Functions")
            lines.append("")
            for func in module.functions:
                lines.extend(self.render_function(func, level=level + 1))
            lines.append("")
        if module.classes:
            lines.append(f"{header_prefix}# Classes")
            lines.append("")
            for cls in module.classes:
                lines.extend(self.render_class_details(cls, level=level + 1))
            lines.append("")
        if module.exports:
            lines.append(
                f'<a name="{self.anchor(module.fully_qualified_name)}-exports"></a>'
            )
            lines.append(f"{header_prefix}# Exports")
            lines.append("")
            for exp in module.exports:
                # Hack since we have the fqn for a module as a string
                fqn = f"{module.fully_qualified_name}.{exp}"
                link = f"#{self.anchor(fqn)}" if is_one_file else f"{fqn}.md"
                lines.append(f"- 🅼 [`{exp}`]({link})")
            lines.append("")
        lines.pop()
        return lines

    def render_class_toc(self, module: Module, cls: Class, indent: int) -> list[str]:
        """Render a TOC entry for a class and its nested classes."""
        lines: list[str] = []
        indent_str = "  " * indent
        lines.append(
            f"{indent_str}- 🅲 [{cls.name}]({self.link(module, cls)})",
        )
        for nested in cls.classes:
            lines.extend(self.render_class_toc(module, nested, indent + 1))
        return lines

    def render_class_details(self, cls: Class, level: int) -> list[str]:
        """
        Render detailed documentation for a class including its signature, docstring details,
        its methods, and any nested classes.
        """
        lines: list[str] = []
        header_prefix = "#" * level
        lines.append(f'<a name="{self.anchor(cls.fully_qualified_name)}"></a>')
        lines.append(f"{header_prefix} 🅲 {cls.fully_qualified_name}")
        lines.append("")
        lines.append("```python")
        lines.append(cls.signature)
        lines.append("```")
        lines.append("")
        if cls.docstring:
            lines.extend(self.render_docstring(cls.docstring))
            lines.append("")
        if cls.functions:
            lines.append("**Functions:**")
            lines.append("")
            for func in cls.functions:
                lines.extend(self.render_function(func, level=level + 1))
            lines.append("")
        if cls.classes:
            # Flatten all nested classes in this class.
            for nested in cls.classes:
                lines.extend(self.render_class_details(nested, level=level))
            lines.append("")
        lines.pop()
        return lines

    def render_function(self, func: Function, level: int) -> list[str]:
        """
        Render detailed documentation for a function/method including its signature and
        docstring details (parameters, returns, raises, etc.).
        """
        lines: list[str] = []
        header_prefix = "#" * level
        lines.append(f'<a name="{self.anchor(func.fully_qualified_name)}"></a>')
        lines.append(f"{header_prefix} 🅵 {func.fully_qualified_name}")
        lines.append("")
        lines.append("```python")
        lines.append(func.signature)
        lines.append("```")
        lines.append("")
        if func.docstring:
            lines.extend(self.render_docstring(func.docstring))
            lines.append("")
        lines.pop()
        return lines

    def render_docstring(
        self, doc: docstring_parser.Docstring, indent: int = 0
    ) -> list[str]:
        """
        Render detailed docstring information including description, parameters,
        returns, raises, and attributes. An indent level can be provided for nested output.
        """
        indent_str = "  " * indent
        lines: list[str] = []
        if doc.short_description:
            lines.append(f"{indent_str}{escaped_markdown(doc.short_description)}")
            lines.append("")
        if doc.long_description:
            lines.append(f"{indent_str}{escaped_markdown(doc.long_description)}")
            lines.append("")
        if doc.params:
            lines.append(f"{indent_str}**Parameters:**")
            lines.append("")
            for param in doc.params:
                line = f"{indent_str}- **{param.arg_name}**"
                if param.type_name:
                    line += f" (`{param.type_name}`)"
                if param.default:
                    line += f" (default: `{param.default}`)"
                if param.description:
                    line += f": {escaped_markdown(param.description)}"
                lines.append(line)
            lines.append("")
        if doc.attrs:
            lines.append(f"{indent_str}**Attributes:**")
            lines.append("")
            for attr in doc.attrs:
                line = f"{indent_str}- **{attr.arg_name}**"
                if attr.type_name:
                    line += f" (`{attr.type_name}`)"
                if attr.description:
                    line += f": {escaped_markdown(attr.description)}"
                lines.append(line)
            lines.append("")
        if doc.returns:
            lines.append(f"{indent_str}**Returns:**")
            lines.append("")
            ret_line = ""
            if doc.returns.type_name:
                ret_line += f"`{doc.returns.type_name}`: "
            if doc.returns.description:
                ret_line += f"{escaped_markdown(doc.returns.description)}"
            else:
                # Trim the trailing colon if no description is provided.
                ret_line = ret_line[:-2]
            lines.append(f"{indent_str}- {ret_line}")
            lines.append("")
        if doc.raises:
            lines.append(f"{indent_str}**Raises:**")
            lines.append("")
            for raise_item in doc.raises:
                raise_line = f"{indent_str}- **{raise_item.type_name}**: "
                if raise_item.description:
                    raise_line += f"{escaped_markdown(raise_item.description)}"
                else:
                    raise_line = raise_line[:-2]
                lines.append(raise_line)
            lines.append("")
        lines.pop()
        return lines

    def anchor(self, fq_name: str) -> str:
        """
        Generate a sanitized anchor from a fully qualified name.
        This implementation replaces dots with hyphens.
        """
        return fq_name.replace(".", "-")

    def link(
        self,
        module: Module,
        item: DocumentedItem | None = None,
        is_in_file: bool = True,
    ) -> str:
        """
        Generate a link to a fully qualified name.
        """
        match (item, is_in_file):
            case (None, True):
                return f"#{self.anchor(module.fully_qualified_name)}"
            case (None, False):
                return f"{module.fully_qualified_name}.md"
            case (item, True):
                return f"#{self.anchor(item.fully_qualified_name)}"
            case (item, False):
                return f"{module.fully_qualified_name}.md#{self.anchor(item.fully_qualified_name)}"


# --- Main function ---


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl a Python package and extract docstrings into Markdown."
    )
    parser.add_argument("package_path", help="Path to the Python package directory")
    parser.add_argument(
        "output_path",
        help="Path to write the Markdown file(s)"
        "Can be a directory or a single file. If a directory, each module will get its own file.",
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private functions, classes, and constants (names starting with '_')",
    )
    args = parser.parse_args()
    package_dir = Path(args.package_path)

    if not package_dir.is_dir():
        print(f"Error: {package_dir} is not a directory.")
        return

    package = crawl_package(package_dir, include_private=args.include_private)
    renderer = MarkdownRenderer()

    output_path = Path(args.output_path)
    renderer.render(package, output_path)


if __name__ == "__main__":
    main()
