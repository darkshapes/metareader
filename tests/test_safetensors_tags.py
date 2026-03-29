# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

import unittest
import os
import shutil

from metareader.model_tags import ModelTags
import json
from huggingface_hub import snapshot_download


class TestLoadMetadataSafetensors(unittest.TestCase):
    def test_metadata_from_safetensors(self):
        model_tool = ModelTags()
        local_folder = os.path.dirname(os.path.abspath(__file__))
        local_folder_test = os.path.join(local_folder, "test_folder")
        file_name = "model.safetensors"
        folder_path_named = snapshot_download(repo_id="exdysa/RA-SAE-DINOv2-32k", allow_patterns=[file_name], local_dir=local_folder_test)
        real_file = os.path.join(folder_path_named, file_name)
        virtual_data_00 = model_tool.metadata_from_safetensors(real_file)
        safetensors_state_dict = os.path.join(local_folder, "test_safetensor_tag_expected.json")
        with open(safetensors_state_dict, "tr", encoding="UTF-8") as f:
            expected_output = json.load(f)

        assert virtual_data_00 == expected_output
        try:
            shutil.rmtree(local_folder_test)
            shutil.rmtree(os.path.join(local_folder, ".cache"))
        except OSError:
            pass


if __name__ == "__main__":
    # unittest.main()
    import pytest

    pytest.main(["-vv", __file__])
