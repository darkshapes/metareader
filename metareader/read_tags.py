# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

"""Wrap Image/Model Metadatam I/O"""

# pylint: disable=import-outside-toplevel

from dataclasses import dataclass
from typing import Optional


@dataclass
class CollectArgs:
    """Arguments for collect operation"""

    folder_path_named: str
    save_location: bool
    separate_desc: bool
    unsafe: bool


class ReadTags:
    """Interface for metadata and text read operations"""

    def __init__(self) -> None:
        self.show_content = None

        self.nfo = print
        self.dbug = print

    def collect(self, args: CollectArgs):
        import json
        import os

        folder_path_named = args.folder_path_named
        save_location = args.save_location
        target_files = []
        assert os.path.exists(folder_path_named), print(f"Path does not exist: {folder_path_named}")

        if os.path.isfile(folder_path_named):
            target_files = [folder_path_named]
        elif os.path.isdir(folder_path_named):
            for root, folders, files in os.walk(folder_path_named):
                for file_name in files:
                    target_files.append(os.path.join(root, file_name))

        for file_path_named in target_files:
            if not args.unsafe:
                metadata = self.read_header.read_header(file_path_named, args.separate_desc)
            else:
                from metareader.model_tags import ModelTags
                from metareader.resources import ensure_path

                unsafe_reader = ModelTags()
                metadata = unsafe_reader.attempt_all_open(file_path_named, args.separate_desc)
            if metadata is not None and save_location:
                ensure_path(save_location)
                document = os.path.join(folder_path_named, os.path.basename(file_path_named))
                output_name = f"{document}.json" if ".json" not in document else document

                with open(output_name, "tw", encoding="UTF-8") as i:
                    try:
                        os.remove(output_name)
                    except FileNotFoundError:
                        pass
                    json.dump(metadata, i, ensure_ascii=False, indent=4, sort_keys=False)

    def _read_jpg_header(self, file_path_named: str) -> Optional[dict]:
        """
        Open jpg format files\n
        :param file_path_named: The path and file name of the jpg file
        :return: Generator element containing header tags
        """
        from PIL import ExifTags, Image

        img = Image.open(file_path_named)  # pylint: disable=protected-access, line-too-long
        exif_tags = {ExifTags.TAGS[key]: val for key, val in img._getexif().items() if key in ExifTags.TAGS}  # pylint: disable=protected-access, line-too-long
        return exif_tags

    def _read_png_header(self, file_path_named: str) -> Optional[dict]:
        """
        Open png format files\n
        :param file_path_named: The path and file name of the png file
        :return: Generator element containing header tags
        """

        from PIL import Image, UnidentifiedImageError

        try:
            img = Image.open(file_path_named)
            if img is None:  # We dont need to load completely unless totally necessary
                img.load()  # This is the case when we have no choice but to load (slower)
            metadata = img.info
            return metadata  # PNG info directly used here
        except UnidentifiedImageError as error_log:
            self.nfo("Failed to read image at:", file_path_named, error_log)
            return None

    def _read_txt_contents(self, file_path_named: str) -> Optional[dict]:
        """
        Open plaintext files\n
        :param file_path_named: The path and file name of the text file
        :return: Generator element containing content
        """

        try:
            with open(file_path_named, "r", encoding="utf_8") as open_file:
                return open_file.read()  # Reads text file into string
        except UnicodeDecodeError as error_log:
            self.nfo("File did not match expected unicode format %s", file_path_named)
            self.dbug(error_log)
            return None
        try:
            with open(file_path_named, "r", encoding="utf_16-be") as open_file:
                return open_file.read()  # Reads text file into string
        except UnicodeDecodeError as error_log:
            self.nfo("File did not match expected unicode format %s", file_path_named)
            self.dbug(error_log)
            return None

    def _read_schema_file(self, file_path_named: str, mode="r") -> Optional[dict]:
        """
        Open .json or toml files\n
        :param file_path_named: The path and file name of the json file
        :return: Generator element containing content
        """
        import json
        import os
        import tomllib

        from metareader.resources import ExtensionType as Ext

        _, ext = os.path.splitext(file_path_named)
        if ext in Ext.TOML:
            loader, mode = (tomllib.load, {"mode": "rb"})
        else:
            loader, mode = (json.load, {"mode": "r", "encoding": "utf_8"})
        with open(file_path_named, **mode) as open_file:  # pylint:disable=unspecified-encoding
            try:
                return loader(open_file)
            except (tomllib.TOMLDecodeError, json.decoder.JSONDecodeError) as error_log:
                raise SyntaxError(f"Couldn't read file {file_path_named}") from error_log

    def read_header(self, file_path_named: str, separate_desc: bool = True) -> Optional[dict]:
        """
        Direct file read operations for various file formats\n
        :param file_path_named: Location of file with file name and path
        :return: A mapping of information contained within it
        """
        from pathlib import Path

        from metareader.model_tags import ModelTags
        from metareader.resources import ExtensionType as Ext

        ext = Path(file_path_named).suffix.lower()

        match ext:
            case ext if ext in Ext.JPEG:
                return self._read_jpg_header(file_path_named)
            case ext if ext in Ext.PNG_:
                return self._read_png_header(file_path_named)
            case ext if ext in [*Ext.SCHEMA]:
                return self._read_schema_file(file_path_named)
            case ext if ext in [*Ext.PLAIN]:
                return self._read_txt_contents(file_path_named)
            case ext if ext in [*Ext.MODEL]:
                model_tool = ModelTags()
                return model_tool.read_metadata_from(file_path_named, separate_desc)


def main(
    path: str | None = None,
    save_location: str | None = None,
    separate_desc: bool | None = None,
    unsafe: bool | None = None,
) -> None:
    import argparse
    import os
    from sys import modules as sys_modules

    from metareader.resources import ExtensionType as Ext

    if "pytest" not in sys_modules:
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="Scan metadata from files or folders at [path] to the console,\
                 then write to a json file at [save]\nOffline function.",
            usage="meta ~/Downloads/models/images -s ~Downloads/models/metadata",
            epilog=f"Valid input formats: {[*Ext.MODEL]}",
        )
        parser.add_argument("path", help="Path to directory or file where files should be analyzed. (default .)", default=os.getcwd())
        parser.add_argument("-s", "--save_to_folder_path", required=False, help="Path where output should be stored. (default: '.')", type=str, default=".")
        parser.add_argument("-d", "--separate_desc", required=False, action="store_true", help="Ignore the metadata from the header. (default: False)")
        parser.add_argument("-u", "--unsafe", action="store_true", help="Try to read non-standard type files. MAY INCLUDE NON-MODEL FILES. (default: False)")
        args = parser.parse_args()
    else:
        args = None

    folder_path_named = os.getcwd() if not args else path if not args.path else args.path
    separate_desc = True if not args else args.separate_desc
    save_location = os.getcwd() if not args else args.save_to_folder_path
    unsafe = False if not args else args.unsafe

    file_reader = ReadTags()
    file_reader.collect(folder_path_named, separate_desc, save_location, unsafe)


if __name__ == "__main__":
    main()
