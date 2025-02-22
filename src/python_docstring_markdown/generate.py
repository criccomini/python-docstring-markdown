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
  - Classes now include a signature (showing base classes) and are rendered with their signature.
  - Parameter and return sections now include type information when available.
"""

from __future__ import annotations

import argparse
import ast
import re
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
    package: Package
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
    # the class signature (including base classes)
    signature: str
    # Can be either a module or another class (for nested classes)
    parent: Module | Class
    docstring: docstring_parser.Docstring | None = None
    functions: list[Function] = field(default_factory=list)
    classes: list[Class] = field(default_factory=list)  # For nested classes


@dataclass
class Function:
    path: Path
    name: str  # final function/method name
    fully_qualified_name: str  # e.g. foo.bar.Baz.method
    signature: str
    parent: Class | Module
    docstring: docstring_parser.Docstring | None = None


@dataclass
class Constant:
    path: Path
    name: str  # constant name
    fully_qualified_name: str  # e.g. foo.bar.MY_CONSTANT
    value: str  # the string representation of the value
    type: str | None = None  # the constant's type, if available


# --- Helper functions ---


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
        signature=signature,
        parent=parent,
        docstring=parsed_doc,
    )


def parse_class(node: ast.ClassDef, parent: Module | Class, file_path: Path) -> Class:
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
        parent=parent,
        docstring=parsed_doc,
        functions=[],
        classes=[],
    )
    # Process methods and nested classes.
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            method = parse_function(child, file_path, parent=cls)
            cls.functions.append(method)
        elif isinstance(child, ast.ClassDef):
            nested_cls = parse_class(child, parent=cls, file_path=file_path)
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
) -> None:
    """Parse top-level functions in a module."""
    for node in module_ast.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = parse_function(node, file_path, parent=module)
            module.functions.append(func)


def parse_module_classes(
    module_ast: ast.Module,
    module: Module,
    file_path: Path,
) -> None:
    """Parse classes in a module."""
    for node in module_ast.body:
        if isinstance(node, ast.ClassDef):
            cls = parse_class(node, parent=module, file_path=file_path)
            module.classes.append(cls)


def parse_module(file_path: Path, package: Package) -> Module:
    """Parse a single module file into a Module dataclass instance."""
    with file_path.open("r", encoding="utf8") as f:
        source = f.read()
    module_ast = ast.parse(source, filename=str(file_path))
    # If the file is __init__.py, use the package's fully qualified name.
    mod_name = file_path.stem
    if mod_name == "__init__":
        fq_name = package.fully_qualified_name
    else:
        fq_name = f"{package.fully_qualified_name}.{mod_name}"
    module = Module(
        path=file_path,
        name=mod_name,
        fully_qualified_name=fq_name,
        package=package,
        docstring=parse_module_docstring(module_ast),
        constants=[],
        functions=[],
        classes=[],
        exports=[],
    )
    if file_path.name == "__init__":
        module.exports = parse_module_exports(module_ast)
    parse_module_constants(module_ast, module, file_path)
    parse_module_functions(module_ast, module, file_path)
    parse_module_classes(module_ast, module, file_path)
    return module


def crawl_package(package_path: Path) -> Package:
    """Recursively crawl the package directory, parsing each .py file as a Module."""
    pkg_name = package_path.name
    package = Package(
        path=package_path, name=pkg_name, fully_qualified_name=pkg_name, modules=[]
    )
    for file_path in package_path.rglob("*.py"):
        module = parse_module(file_path, package)
        package.modules.append(module)
    return package


# --- Renderer Classes ---


class Renderer:
    def render(self, package: Package) -> str:
        """Render the Package as a string.
        This method should be implemented by subclasses."""
        raise NotImplementedError


class MarkdownRenderer(Renderer):
    def __init__(self, include_private: bool = False):
        # List of tuples: (level, title, slug)
        self.toc: list[tuple[int, str, str]] = []
        self.include_private = include_private

    @staticmethod
    def slugify(text: str) -> str:
        """Convert text to a slug suitable for use as an anchor."""
        text = text.lower()
        text = text.replace(".", "-")  # Replace dots with dashes.
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        text = re.sub(r"\s+", "-", text).strip("-")
        return text

    def is_private(self, item: DocumentedItem) -> bool:
        """Return True if the item is considered private."""
        return not self.include_private and (
            item.name.startswith("_")
            and not (item.name.startswith("__") and item.name.endswith("__"))
        )

    def render_docstring(
        self,
        doc: docstring_parser.Docstring | None,
        signature: str | None = None,
    ) -> str:
        """
        Reformat the parsed docstring into Markdown.
        This implementation produces Markdown by concatenating the short and long descriptions,
        and listing parameters (with types if available), return info (with type), and exceptions.
        """
        if doc is None:
            return ""
        lines = []
        if doc.short_description:
            lines.append(doc.short_description)
            lines.append("")
        if doc.long_description:
            lines.append(doc.long_description)
            lines.append("")
        if signature:
            lines.append("**Signature:**")
            lines.append("")
            lines.append("```python")
            lines.append(signature)
            lines.append("```")
        if doc.attrs:
            lines.append("**Attributes:**")
            lines.append("")
            for attr in doc.attrs:
                attr_line = f"- `{attr.arg_name}`"
                if attr.type_name:
                    attr_line += f" (**{attr.type_name}**)"
                attr_line += f": {attr.description}"
                if attr.default:
                    attr_line += f" (default: `{attr.default}`)"
                if attr.is_optional:
                    attr_line += " (optional)"
                lines.append(attr_line)
            lines.append("")
        if doc.params:
            lines.append("**Parameters:**")
            lines.append("")
            for param in doc.params:
                param_line = f"- `{param.arg_name}`"
                if param.type_name:
                    param_line += f" (**{param.type_name}**)"
                param_line += f": {param.description}"
                if param.default:
                    param_line += f" (default: `{param.default}`)"
                if param.is_optional:
                    param_line += " (optional)"
                lines.append(param_line)
            lines.append("")
        if doc.examples:
            lines.append("**Examples:**")
            lines.append("")
            for example in doc.examples:
                if example.snippet:
                    lines.append("```python")
                    lines.append(example.snippet)
                    lines.append("```")
                    lines.append("")
        if doc.returns:
            lines.append("**Returns:**")
            lines.append("")
            ret_line = "- "
            if doc.returns.type_name:
                ret_line += f"(**{doc.returns.type_name}**) "
            ret_line += f"{doc.returns.description}"
            lines.append(ret_line)
            lines.append("")
        if doc.raises:
            lines.append("**Raises:**")
            for exception in doc.raises:
                lines.append(f"- (**{exception.type_name}**) {exception.description}")
            lines.append("")
        return "\n".join(lines).strip()

    def render_header(
        self,
        level: int,
        item: DocumentedItem,
    ) -> list[str]:
        """
        Render a header using a documented data class.
        Uses the item's name (slugified) as the anchor, and the title_override
        if provided; otherwise uses the item's name.
        Records the header in the TOC and returns a list of Markdown lines.
        """
        slug = self.slugify(item.name)
        self.toc.append((level, item.name, slug))
        return [f'<a id="{slug}"></a>', f"{'#' * level} `{item.fully_qualified_name}`"]

    def render_toc(self) -> list[str]:
        """Render the table of contents based on the collected headers."""
        lines = []
        title = "Table of Contents"
        slug = self.slugify(title)
        lines.append(f'<a id="{slug}"></a>')
        lines.append(f"**{title}**")
        lines.append("")
        for level, title, slug in self.toc:
            indent = "  " * (level - 1)
            lines.append(f"{indent}- [`{title}`](#{slug})")
        lines.append("")
        return lines

    def render_constant(self, const: Constant, heading_level: int) -> list[str]:
        """Render a constant to Markdown and return the lines as a list of strings."""
        # Skip if private.
        if self.is_private(const):
            return []
        lines = []
        lines.extend(self.render_header(heading_level, const))
        lines.append("")
        lines.append("```python")
        if const.type:
            lines.append(f"{const.name}: {const.type} = {const.value}")
        else:
            lines.append(f"{const.name} = {const.value}")
        lines.append("```")
        lines.append("")
        return lines

    def render_function(self, func: Function, heading_level: int) -> list[str]:
        """Render a function or method to Markdown and return the lines as a list of strings."""
        if self.is_private(func):
            return []
        doc = self.render_docstring(func.docstring, func.signature)
        lines = []
        lines.extend(self.render_header(heading_level, func))
        lines.append("")
        if doc:
            lines.append(doc)
            lines.append("")
        return lines

    def render_class(self, cls: Class, heading_level: int) -> list[str]:
        """Recursively render a class, its signature, its methods, and nested classes."""
        if self.is_private(cls):
            return []
        md = []
        md.extend(self.render_header(heading_level, cls))
        md.append("")
        doc = self.render_docstring(cls.docstring, cls.signature)
        if doc:
            md.append(doc)
            md.append("")
        child_lines = []
        for method in cls.functions:
            if self.is_private(method):
                continue
            rendered = self.render_function(method, heading_level=heading_level + 1)
            if rendered:
                child_lines.extend(rendered)
        for nested in cls.classes:
            rendered = self.render_class(nested, heading_level=heading_level + 1)
            if rendered:
                child_lines.extend(rendered)
                child_lines.append("")
        md.extend(child_lines)
        return md

    def render_module(self, module: Module) -> list[str]:
        """Render a module and its children."""
        lines = []
        lines.extend(self.render_header(2, module))
        lines.append("")

        module_doc = self.render_docstring(module.docstring)
        if module_doc:
            lines.append(module_doc)
            lines.append("")
        if module.exports:
            for export in module.exports:
                lines.append(f"- `{export}`")
            lines.append("")

        children_lines = []
        for const in module.constants:
            rendered = self.render_constant(const, heading_level=3)
            if rendered:
                children_lines.extend(rendered)
        for func in module.functions:
            rendered = self.render_function(func, heading_level=3)
            if rendered:
                children_lines.extend(rendered)
        for cls in module.classes:
            rendered = self.render_class(cls, heading_level=3)
            if rendered:
                children_lines.extend(rendered)
                children_lines.append("")
        lines.extend(children_lines)
        return lines

    def render(self, package: Package) -> str:
        """
        Render the Package as a Markdown string.
        The table of contents is inserted immediately after the package header.
        """
        self.toc = []
        package_header = self.render_header(1, package)
        modules_lines: list[str] = []
        for module in package.modules:
            rendered_module = self.render_module(module)
            if rendered_module:
                modules_lines.extend(rendered_module)
        toc_lines = self.render_toc()
        final_lines = []
        final_lines.extend(package_header)
        final_lines.append("")
        final_lines.extend(toc_lines)
        final_lines.append("---")
        final_lines.append("")
        final_lines.extend(modules_lines)
        return "\n".join(final_lines)


# --- Main function ---


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crawl a Python package and extract docstrings."
    )
    parser.add_argument("package_path", help="Path to the Python package directory")
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

    package = crawl_package(package_dir)
    renderer = MarkdownRenderer(include_private=args.include_private)
    markdown_output = renderer.render(package)
    print(markdown_output)


if __name__ == "__main__":
    main()
