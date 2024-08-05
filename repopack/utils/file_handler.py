import os
import chardet
from typing import List, Dict, Any
from ..exceptions import FileProcessingError
from .file_manipulator import FileManipulator
from .logger import logger


def is_binary(file_path: str) -> bool:
    """Check if a file is binary."""
    try:
        with open(file_path, "tr") as check_file:
            check_file.read()
            return False
    except:
        return True


def sanitize_files(
    file_paths: List[str], root_dir: str, config: Dict[str, Any]
) -> List[Dict[str, str]]:
    """Sanitize files based on the given configuration."""
    sanitized_files = []
    for file_path in file_paths:
        full_path = os.path.join(root_dir, file_path)
        logger.trace(f"Sanitizing file: {file_path}")
        try:
            if not is_binary(full_path):
                content = sanitize_file(full_path, config)
                if content:
                    sanitized_files.append({"path": file_path, "content": content})
                    logger.trace(f"File sanitized: {file_path}")
                else:
                    logger.trace(f"File skipped (empty content): {file_path}")
        except Exception as e:
            raise FileProcessingError(f"Error processing file {file_path}: {str(e)}")
    return sanitized_files


def sanitize_file(file_path: str, config: Dict[str, Any]) -> str:
    """Sanitize a single file."""
    try:
        with open(file_path, "rb") as f:
            raw_content = f.read()

        encoding = chardet.detect(raw_content)["encoding"] or "utf-8"
        content = raw_content.decode(encoding)
        logger.trace(f"File encoding detected: {encoding}")

        if config["output"]["remove_comments"]:
            raise NotImplementedError("Comment removal is not implemented yet.")
            # file_extension = os.path.splitext(file_path)[1]
            # content = FileManipulator.remove_comments(content, file_extension)
            # logger.trace(f"Comments removed from file: {file_path}")

        if config["output"]["remove_empty_lines"]:
            content = remove_empty_lines(content)
            logger.trace(f"Empty lines removed from file: {file_path}")

        content = content.strip()

        if config["output"]["show_line_numbers"]:
            content = add_line_numbers(content)
            logger.trace(f"Line numbers added to file: {file_path}")

        return content
    except Exception as e:
        raise FileProcessingError(f"Error sanitizing file {file_path}: {str(e)}")


def remove_empty_lines(content: str) -> str:
    """Remove empty lines from the content."""
    return "\n".join(line for line in content.splitlines() if line.strip())


def add_line_numbers(content: str) -> str:
    """Add line numbers to the content."""
    lines = content.split("\n")
    max_line_num = len(lines)
    line_num_width = len(str(max_line_num))
    return "\n".join(f"{str(i+1).rjust(line_num_width)} | {line}" for i, line in enumerate(lines))