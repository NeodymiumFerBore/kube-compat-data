from pydantic import BaseModel, HttpUrl

class VersionRange(BaseModel):
  min: str
  max: str

  class Config:
    extra = "forbid"

class KubeCompatEntry(BaseModel):
  kube_vers: str
  versions: VersionRange

  class Config:
    extra = "forbid"

class ToolData(BaseModel):
  home: HttpUrl
  sources: HttpUrl
  compat_source: HttpUrl
  compat_matrix: list[KubeCompatEntry]

  class Config:
    extra = "forbid"
