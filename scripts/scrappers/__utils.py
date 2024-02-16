import yaml
from __models import ToolData
from pydantic_core._pydantic_core import ValidationError

# For testing:

# Assert fail
#check("toto", {"truc": "toto", "compat_matrix": [{"kube_vers": "1", "versions": {"min": "1", "max": "2"}}]})
#check("toto", {"compat_matrix": [{"kube_vers": "1", "toto": "truc", "versions": {"min": "1", "max": "2"}}]})
#check("toto", {"compat_matrix": [{"kube_vers": "1", "versions": {"min": "1", "max": "2", "toto": "truc"}}]})

# Assert success (need to add homes, sources, compat_source)
#check("toto", {"compat_matrix": [{"kube_vers": "1", "versions": {"min": "1", "max": "2"}}]})

def patch_tool_data(tool_name: str, data: ToolData) -> None:
  try:
    ToolData(**data)  # Validate directly using the model
  except ValidationError as e:
    print(f"Validation error for tool '{tool_name}': {str(e).splitlines()[0]}\n")
    raise e

  # Overwrite {repo_root}/tools/{tool_name}/data.yaml
  print(yaml.dump(data, indent=2))

  # Then open a PR
