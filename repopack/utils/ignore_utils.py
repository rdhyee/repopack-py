import os
from typing import List, Dict, Any, Callable
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from .logger import logger

# Default list of patterns to ignore in repository packing
DEFAULT_IGNORE_LIST: List[str] = [
    # Version control
    ".git",
    ".gitignore",
    ".gitattributes",
    ".hg",
    ".hgignore",
    ".svn",
    # Dependency directories
    "node_modules",
    "bower_components",
    # Logs
    "logs",
    "*.log",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    # Runtime data
    "pids",
    "*.pid",
    "*.seed",
    "*.pid.lock",
    # Directory for instrumented libs generated by jscoverage/JSCover
    "lib-cov",
    # Coverage directory used by tools like istanbul
    "coverage",
    # nyc test coverage
    ".nyc_output",
    # Grunt intermediate storage
    ".grunt",
    # Bower dependency directory
    "bower_components",
    # node-waf configuration
    ".lock-wscript",
    # Compiled binary addons
    "build/Release",
    # Dependency directories
    "jspm_packages/",
    # TypeScript v1 declaration files
    "typings/",
    # Optional npm cache directory
    ".npm",
    # Optional eslint cache
    ".eslintcache",
    # Optional REPL history
    ".node_repl_history",
    # Output of 'npm pack'
    "*.tgz",
    # Yarn files
    ".yarn/*",
    # Yarn Integrity file
    ".yarn-integrity",
    # dotenv environment variables file
    ".env",
    # next.js build output
    ".next",
    # nuxt.js build output
    ".nuxt",
    # vuepress build output
    ".vuepress/dist",
    # Serverless directories
    ".serverless/",
    # FuseBox cache
    ".fusebox/",
    # DynamoDB Local files
    ".dynamodb/",
    # TypeScript output
    "dist",
    # OS generated files
    ".DS_Store",
    "Thumbs.db",
    # Editor directories and files
    ".idea",
    ".vscode",
    "*.swp",
    "*.swo",
    "*.swn",
    "*.bak",
    # Package manager locks
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    # Build outputs
    "build",
    "out",
    # Temporary files
    "tmp",
    "temp",
    # repopack output
    "repopack-output.txt",
]


def get_ignore_patterns(filename: str, root_dir: str) -> List[str]:
    """
    Get ignore patterns from a file.

    Args:
        filename (str): The name of the ignore file (e.g., '.gitignore').
        root_dir (str): The root directory of the project.

    Returns:
        List[str]: A list of ignore patterns read from the file.
    """
    ignore_path: str = os.path.join(root_dir, filename)
    patterns: List[str] = []
    if os.path.exists(ignore_path):
        try:
            with open(ignore_path, "r") as f:
                patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except IOError as e:
            logger.warning(f"Error reading ignore file {ignore_path}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error reading ignore file {ignore_path}: {str(e)}")
    else:
        logger.debug(f"Ignore file not found: {ignore_path}")
    return patterns


def get_all_ignore_patterns(root_dir: str, config: Dict[str, Any]) -> List[str]:
    """
    Get all ignore patterns based on the configuration.

    Args:
        root_dir (str): The root directory of the project.
        config (Dict[str, Any]): The configuration dictionary.

    Returns:
        List[str]: A list of all ignore patterns to be used.
    """
    patterns: List[str] = []
    if config["ignore"]["use_default_patterns"]:
        patterns.extend(DEFAULT_IGNORE_LIST)
    if config["ignore"]["use_gitignore"]:
        patterns.extend(get_ignore_patterns(".gitignore", root_dir))
    patterns.extend(get_ignore_patterns(".repopackignore", root_dir))
    patterns.extend(config["ignore"]["custom_patterns"])
    return patterns


def create_ignore_filter(patterns: List[str]) -> Callable[[str], bool]:
    """
    Create an ignore filter function based on the given patterns.

    Args:
        patterns (List[str]): A list of ignore patterns.

    Returns:
        Callable[[str], bool]: A function that takes a file path and returns True if the file should be included,
                               False if it should be ignored.
    """
    spec: PathSpec = PathSpec.from_lines(GitWildMatchPattern, patterns)
    return lambda path: not spec.match_file(path)
