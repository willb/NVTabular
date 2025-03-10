#
# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import nest_asyncio
import pytest
from testbook import testbook

from tests.conftest import REPO_ROOT

pytest.importorskip("cudf")
pytest.importorskip("tensorflow")
nest_asyncio.apply()


def test_example_02_advanced_workflow():
    with testbook(
        REPO_ROOT / "examples" / "02-Advanced-NVTabular-workflow.ipynb",
        execute=False,
        timeout=180,
    ) as tb:
        tb.inject(
            """
            import os
            from unittest.mock import patch
            from merlin.datasets.synthetic import generate_data
            from pathlib import Path
            mock_train, mock_valid = generate_data(
                input="movielens-1m",
                num_rows=1000,
                set_sizes=(0.8, 0.2)
            )
            input_path = os.environ.get(
                "INPUT_DATA_DIR",
                os.path.expanduser("~/merlin-framework/movielens/")
            )
            Path(f'{input_path}ml-1m').mkdir(parents=True, exist_ok=True)
            mock_train.compute().to_parquet(f'{input_path}ml-1m/train.parquet')
            mock_train.compute().to_parquet(f'{input_path}ml-1m/valid.parquet')

            p1 = patch(
                "merlin.datasets.entertainment.get_movielens",
                return_value=[mock_train, mock_valid]
            )
            p1.start()
            """
        )
        tb.execute_cell(range(5))
        tb.inject(
            """
                from merlin.core.dispatch import get_lib
                import string
                import numpy as np

                def generate_title():
                    letters = list(string.ascii_letters)
                    np.random.shuffle(letters)
                    return ''.join(letters)[:np.random.randint(len(letters))]

                train = get_lib().read_parquet(f'{input_path}ml-1m/train.parquet')
                valid = get_lib().read_parquet(f'{input_path}ml-1m/train.parquet')

                num_rows = train.movieId.unique().size
                movies = get_lib().DataFrame(
                    data={
                        'movieId': train.movieId.unique(),
                        'title': [generate_title() for i in range(num_rows)],
                        'genres': [['a_genre'] for i in range(num_rows)]}
                )
                """
        )
        tb.execute_cell(range(6, len(tb.cells)))
        metrics = tb.ref("metrics")
        assert set(metrics.history.keys()) == set(
            [
                "auc_1",
                "binary_accuracy",
                "loss",
                "loss_batch",
                "precision_1",
                "recall_1",
                "regularization_loss",
                "val_auc_1",
                "val_binary_accuracy",
                "val_loss",
                "val_loss_batch",
                "val_precision_1",
                "val_recall_1",
                "val_regularization_loss",
            ]
        )
