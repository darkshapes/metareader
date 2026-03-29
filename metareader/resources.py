# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from typing import Set, List, Optional
from ast import Constant
import os
from pathlib import Path


class ExtensionType:
    """Valid file formats for metadata reading\n"""

    PNG_: Set[str] = {".png"}
    JPEG: Set[str] = {".jpg", ".jpeg"}
    WEBP: Set[str] = {".webp"}
    JSON: Set[str] = {".json"}
    TOML: Set[str] = {".toml"}
    TEXT: Set[str] = {".txt", ".text"}
    HTML: Set[str] = {".html", ".htm"}
    XML_: Set[str] = {".xml"}
    GGUF: Set[str] = {".gguf"}
    SAFE: Set[str] = {".safetensors", ".sft"}
    PICK: Set[str] = {".pt", ".pth", ".ckpt", ".pickletensor"}
    ONNX: Set[str] = {".onnx"}
    MPG4: Set[str] = {".mp4"}
    MPG3: Set[str] = {".mp3"}
    WAVE: Set[str] = {".wav"}
    OGG_: Set[str] = {".ogg"}
    FLAC: Set[str] = {".flac"}
    GIF_: Set[str] = {".gif"}

    IMAGE: List[str] = list(JPEG.union(WEBP, PNG_, GIF_))
    EXIF: List[str] = list(JPEG.union(WEBP))
    SCHEMA: List[str] = list(JSON.union(TOML))
    PLAIN: List[str] = list(TEXT.union(XML_, HTML))
    AUDIO: List[str] = list(MPG3.union(WAVE, MPG4, OGG_, FLAC))
    VIDEO: List[str] = list(MPG4.union(GIF_))
    MODEL: List[str] = list(SAFE.union(GGUF, PICK, ONNX))

    MEDIA: List[str] = IMAGE + EXIF + SCHEMA + PLAIN + AUDIO + VIDEO

    IGNORE: List[Constant] = [
        "Thumbs.db",
        "desktop.ini",
        ".fseventsd",
        ".DS_Store",
        ".gitattributes",
        ".env",
        ".py",
        "LICENSE",
        ".md",
    ]


def ensure_path(folder_path_named: Path, file_name: Optional[str] = None) -> Optional[Path]:
    """Provide absolute certainty a file location exists\n
    :param folder_path_named: Location to test
    :param file_name: Optional file name to test, defaults to None
    :return: The original folder path, the original folder path with file, or None if failure
    """
    folder_path_named = Path(folder_path_named)
    if not folder_path_named.exists():
        try:
            folder_path_named.mkdir(parents=True, exist_ok=True)  # Ensure the directory is created resiliently
        except OSError:
            try:
                os.makedirs(folder_path_named, exist_ok=False)
            except OSError:
                return None

    if file_name:
        full_path = os.path.join(folder_path_named, file_name)
        full_path = Path(full_path)
        if full_path.exists():
            return full_path
        try:
            full_path.touch(exist_ok=False)  # Create the file only if it doesn't exist
        except (FileExistsError, OSError):
            pass
        return str(full_path)

    return str(folder_path_named) if folder_path_named.exists() else None
