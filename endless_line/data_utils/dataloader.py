import os
from pathlib import Path
import git
import pandas as pd
class DataLoader:
    def __init__(self, data_dir_path: str):
        self.root_dir = self._find_git_root()
        self.data_dir_path = os.path.join(self.root_dir, data_dir_path)

    def _find_git_root(self) -> str:
        """Find the root directory of the git repository.

        Returns:
            str: Absolute path to the git root directory

        Raises:
            git.exc.InvalidGitRepositoryError: If not in a git repository
        """
        try:
            git_repo = git.Repo(Path.cwd(), search_parent_directories=True)
            return git_repo.git.rev_parse("--show-toplevel")
        except git.exc.InvalidGitRepositoryError:
            raise git.exc.InvalidGitRepositoryError(
                "Not a git repository. Please run from within the project repository."
            )

    def load_data(self, file_name: str) -> pd.DataFrame:
        """Load the data from the data directory.

        Returns:
            pd.DataFrame: The loaded data
        """
        return pd.read_csv(os.path.join(self.data_dir_path, file_name))

