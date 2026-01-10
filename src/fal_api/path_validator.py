"""
Path validation utilities for Qwen-Image-Layered.

Provides secure path validation and handling:
- Path existence checks
- File type validation
- Directory creation
- Safe path manipulation
"""

import os
from pathlib import Path
from typing import Optional, List, Union, Tuple

try:
    from .logging_config import get_logger
    from .errors import InvalidInputError, ImageProcessingError
except ImportError:
    # Fallback for direct module loading
    import importlib.util as _util
    from pathlib import Path as _Path

    _spec = _util.spec_from_file_location(
        "logging_config",
        _Path(__file__).parent / "logging_config.py"
    )
    _logging_config = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_logging_config)
    get_logger = _logging_config.get_logger

    _spec = _util.spec_from_file_location(
        "errors",
        _Path(__file__).parent / "errors.py"
    )
    _errors = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_errors)
    InvalidInputError = _errors.InvalidInputError
    ImageProcessingError = _errors.ImageProcessingError

logger = get_logger("path_validator")


# Supported image formats
SUPPORTED_IMAGE_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff"}
SUPPORTED_EXPORT_FORMATS = {".pptx", ".psd", ".zip", ".png"}


class PathValidator:
    """
    Validates and manages file paths.

    Usage:
        validator = PathValidator()
        path = validator.validate_image_path("photo.png")
        output_dir = validator.ensure_directory("./output")
    """

    @staticmethod
    def validate_path(
        path: Union[str, Path],
        must_exist: bool = True,
        allowed_extensions: Optional[set] = None,
    ) -> Path:
        """
        Validate a file path.

        Args:
            path: Path to validate
            must_exist: Whether the file must exist
            allowed_extensions: Set of allowed extensions (e.g., {".png", ".jpg"})

        Returns:
            Validated Path object

        Raises:
            InvalidInputError: If validation fails
        """
        if path is None:
            raise InvalidInputError("Path cannot be None")

        try:
            path = Path(path).resolve()
        except Exception as e:
            raise InvalidInputError(f"Invalid path format: {path}") from e

        # Check existence if required
        if must_exist and not path.exists():
            raise InvalidInputError(f"Path does not exist: {path}")

        # Check extension if specified
        if allowed_extensions:
            ext = path.suffix.lower()
            if ext not in allowed_extensions:
                allowed = ", ".join(sorted(allowed_extensions))
                raise InvalidInputError(
                    f"Invalid file extension '{ext}'. Allowed: {allowed}"
                )

        logger.debug(f"Path validated: {path}")
        return path

    @staticmethod
    def validate_image_path(path: Union[str, Path]) -> Path:
        """
        Validate an image file path.

        Args:
            path: Path to image file

        Returns:
            Validated Path object

        Raises:
            InvalidInputError: If not a valid image path
        """
        return PathValidator.validate_path(
            path,
            must_exist=True,
            allowed_extensions=SUPPORTED_IMAGE_FORMATS,
        )

    @staticmethod
    def validate_output_path(
        path: Union[str, Path],
        allowed_extensions: Optional[set] = None,
    ) -> Path:
        """
        Validate an output file path.

        Args:
            path: Path for output file
            allowed_extensions: Allowed extensions

        Returns:
            Validated Path object (parent directory ensured)

        Raises:
            InvalidInputError: If validation fails
        """
        if path is None:
            raise InvalidInputError("Output path cannot be None")

        try:
            path = Path(path).resolve()
        except Exception as e:
            raise InvalidInputError(f"Invalid path format: {path}") from e

        # Check extension if specified
        if allowed_extensions:
            ext = path.suffix.lower()
            if ext not in allowed_extensions:
                allowed = ", ".join(sorted(allowed_extensions))
                raise InvalidInputError(
                    f"Invalid output extension '{ext}'. Allowed: {allowed}"
                )

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(f"Output path validated: {path}")
        return path

    @staticmethod
    def ensure_directory(
        path: Union[str, Path],
        create: bool = True,
    ) -> Path:
        """
        Ensure a directory exists.

        Args:
            path: Directory path
            create: Whether to create if not exists

        Returns:
            Directory Path object

        Raises:
            InvalidInputError: If directory cannot be created
        """
        if path is None:
            raise InvalidInputError("Directory path cannot be None")

        try:
            path = Path(path).resolve()
        except Exception as e:
            raise InvalidInputError(f"Invalid directory path: {path}") from e

        if path.exists():
            if not path.is_dir():
                raise InvalidInputError(f"Path exists but is not a directory: {path}")
        elif create:
            try:
                path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {path}")
            except Exception as e:
                raise InvalidInputError(f"Cannot create directory: {path}") from e
        else:
            raise InvalidInputError(f"Directory does not exist: {path}")

        return path

    @staticmethod
    def get_safe_filename(
        name: str,
        max_length: int = 255,
        replacement: str = "_",
    ) -> str:
        """
        Create a safe filename from a string.

        Args:
            name: Original name
            max_length: Maximum filename length
            replacement: Character to replace unsafe characters

        Returns:
            Safe filename string
        """
        # Characters unsafe for filenames
        unsafe_chars = '<>:"/\\|?*\x00'

        result = name
        for char in unsafe_chars:
            result = result.replace(char, replacement)

        # Remove leading/trailing spaces and dots
        result = result.strip(". ")

        # Truncate if needed
        if len(result) > max_length:
            # Preserve extension if present
            parts = result.rsplit(".", 1)
            if len(parts) == 2 and len(parts[1]) <= 10:
                base = parts[0][:max_length - len(parts[1]) - 1]
                result = f"{base}.{parts[1]}"
            else:
                result = result[:max_length]

        return result or "unnamed"

    @staticmethod
    def list_images(
        directory: Union[str, Path],
        recursive: bool = False,
    ) -> List[Path]:
        """
        List all image files in a directory.

        Args:
            directory: Directory to search
            recursive: Search subdirectories

        Returns:
            List of image file paths
        """
        directory = PathValidator.ensure_directory(directory, create=False)

        images = []
        if recursive:
            for ext in SUPPORTED_IMAGE_FORMATS:
                images.extend(directory.rglob(f"*{ext}"))
                # Also check uppercase
                images.extend(directory.rglob(f"*{ext.upper()}"))
        else:
            for ext in SUPPORTED_IMAGE_FORMATS:
                images.extend(directory.glob(f"*{ext}"))
                images.extend(directory.glob(f"*{ext.upper()}"))

        # Remove duplicates and sort
        images = sorted(set(images))

        logger.debug(f"Found {len(images)} images in {directory}")
        return images

    @staticmethod
    def get_unique_path(
        path: Union[str, Path],
        separator: str = "_",
    ) -> Path:
        """
        Get a unique path by appending numbers if file exists.

        Args:
            path: Desired path
            separator: Separator before number

        Returns:
            Unique path that doesn't exist
        """
        path = Path(path)
        if not path.exists():
            return path

        base = path.stem
        ext = path.suffix
        parent = path.parent

        counter = 1
        while True:
            new_path = parent / f"{base}{separator}{counter}{ext}"
            if not new_path.exists():
                return new_path
            counter += 1

    @staticmethod
    def validate_image_readable(path: Union[str, Path]) -> Tuple[Path, dict]:
        """
        Validate that an image can be read and get its info.

        Args:
            path: Path to image

        Returns:
            Tuple of (validated path, image info dict)

        Raises:
            ImageProcessingError: If image cannot be read
        """
        path = PathValidator.validate_image_path(path)

        try:
            from PIL import Image

            with Image.open(path) as img:
                info = {
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format,
                    "size_bytes": path.stat().st_size,
                }
                logger.debug(f"Image info: {path} - {info['width']}x{info['height']} {info['mode']}")
                return path, info
        except ImportError:
            # PIL not available, just return basic info
            info = {
                "size_bytes": path.stat().st_size,
            }
            return path, info
        except Exception as e:
            raise ImageProcessingError(f"Cannot read image: {path}") from e


# Convenience functions
def validate_image(path: Union[str, Path]) -> Path:
    """Validate an image file path."""
    return PathValidator.validate_image_path(path)


def validate_output(
    path: Union[str, Path],
    extensions: Optional[set] = None,
) -> Path:
    """Validate an output file path."""
    return PathValidator.validate_output_path(path, extensions)


def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure a directory exists."""
    return PathValidator.ensure_directory(path)


def list_images(directory: Union[str, Path], recursive: bool = False) -> List[Path]:
    """List image files in directory."""
    return PathValidator.list_images(directory, recursive)


def get_unique_path(path: Union[str, Path]) -> Path:
    """Get unique path for file."""
    return PathValidator.get_unique_path(path)


def safe_filename(name: str) -> str:
    """Create safe filename."""
    return PathValidator.get_safe_filename(name)
