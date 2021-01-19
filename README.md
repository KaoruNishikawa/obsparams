# obsparams

Extract and list declared/used obsparams.

## Usage

- Run `poetry install` to configure python environment.
- Use `obsfiles_params_check.ipynb`.
  - 2nd cell: Input your GitHub access token as type `str`  
  How to get the token: GitHub > settings > developer settings > Personal access token > generate new token  
  [Creating a personal access token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token)
- like 5th cell: To get DECLARED obsparams, use `check.get_obsparams(path)`.
- like 8th cell: To get actually USED obsparams, use `check.params_extract([pattern], path)`.
  - This function may not list the params which key is given as substitution (including f-string)
- Paths are something like `"github_username/repository_name/directory_name/../filename"`
- The functions implemented in this repository won't create copy files of GitHub resources.
