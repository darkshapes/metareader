# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->


import unittest
from unittest.mock import patch, MagicMock
import struct
import shutil
import os

from metareader.model_tags import ModelTags
import json
from huggingface_hub import snapshot_download
from metareader import ensure_path


class TestLoadMetadataGGUF(unittest.TestCase):
    local_test_folder = os.path.dirname(os.path.abspath(__file__))
    temp_folder = str(ensure_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_folder")))

    @patch("metareader.model_tags.ModelTags.create_llama_parser")
    def setUp(self, MockParseModel) -> None:
        # Create a temporary file with known GGUF header data
        self.local_test_folder = self.local_test_folder
        self.temp_folder = self.temp_folder
        self.model_tool = ModelTags()
        self.test_file_name = "test.gguf"
        magic = b"GGUF"
        with open(self.test_file_name, "wb") as f:
            f.write(magic)
            f.write(struct.pack("<I", 2))

        # Set up the mock parser object
        self.mock_parser = MagicMock()
        self.mock_parser.metadata = {"general": {"architecture": "Llama", "name": "MyModel"}}
        self.mock_parser.scores = MagicMock(dtype=MagicMock(name="float32"))

        # Make parse_gguf_model return the mock parser
        MockParseModel.return_value = self.mock_parser

    def test_read_valid_header(self):
        result = self.model_tool.gguf_check(self.test_file_name)
        self.assertTrue(result)

    def test_metadata_from_gguf(self):
        file_name = "dummy.gguf"
        folder_path_named = snapshot_download(repo_id="exdysa/ratchet-test", allow_patterns=[file_name], local_dir=self.temp_folder)
        real_file = os.path.join(folder_path_named, file_name)
        virtual_data_00 = self.model_tool.attempt_file_open(real_file, separate_desc=False)
        gguf_state_dict = os.path.join(self.local_test_folder, "test_gguf_tag_expected.json")
        expected_output_part_1 = None
        expected_output_attempt_2 = {"dtype": "float32", "name": "Planck-OpenLAiNN-10M"}
        with open(gguf_state_dict, "tr", encoding="UTF-8") as f:
            expected_output_part_2 = json.load(f)
        try:
            assert virtual_data_00 == (expected_output_attempt_2)
        except AssertionError:
            assert virtual_data_00 == (expected_output_part_1, expected_output_part_2)

        try:
            shutil.rmtree(self.temp_folder)
            shutil.rmtree(os.path.join(self.temp_folder, ".cache"))
        except OSError:
            pass

    @classmethod
    def tearDownClass(cls) -> None:
        # Clean up the temporary file after all tests are done
        try:
            os.remove("test.gguf")
            os.remove("test.gguf")
            os.removedir(cls.temp_folder)
        except OSError:
            pass


if __name__ == "__main__":
    unittest.main()
    import pytest

    pytest.main(["-vv", __file__])
