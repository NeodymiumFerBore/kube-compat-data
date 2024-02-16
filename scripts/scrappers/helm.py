#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from packaging import version

from __utils import dump_tool_data

# Do not retrieve info for kube < v1.19
min_limit = "1.19.0"

home = "https://helm.sh/"
sources = "https://github.com/helm/helm"
compat_source = "https://helm.sh/docs/topics/version_skew/"

page = requests.get(compat_source)
soup = BeautifulSoup(page.content, "html.parser")

entries = soup.find(id="helm").find("table").find("tbody").find_all("tr")

compat_sort_by_helm = []
for entry in entries:
  # helm_vers: '3.14.x' ; kube_maxmin: '1.29.x - 1.26.x'
  helm_vers, kube_maxmin = [e.text.replace(".x","") for e in entry.find_all("td")]
  kube_max, kube_min = kube_maxmin.split(" - ")

  compat_sort_by_helm.append({
    "helm_vers": helm_vers,
    "kube_min": kube_min,
    "kube_max": kube_max,
  })

# Now we have a compat table sorted by helm version, with kube version ranges
# We have to convert it to our format, sorted by kube version, with helm ranges
# compat_matrix:
# - kube_vers: v1.22
#   versions:
#     min: v3.7
#     max: v3.10

kube_versions = sorted(set([d[k] for d in compat_sort_by_helm for k in ["kube_min", "kube_max"]]), key=lambda v: version.parse(v), reverse=True)

compat_data = []
for kube_ver in kube_versions:
  # Retrieve all helm version where kube_min <= kube_ver <= kube_max
  helm_vers = sorted([
    d["helm_vers"] for d in compat_sort_by_helm 
    if version.parse(d["kube_min"]) <= version.parse(kube_ver) <= version.parse(d["kube_max"])
  ], key=lambda v: version.parse(v))

  compat_data.append({
    "kube_vers": f"v{kube_ver}",
    "versions": {
      "min": f"v{helm_vers[0]}",
      "max": f"v{helm_vers[-1]}"
    }
  })

if min_limit:
  compat_data = [d for d in compat_data if version.parse(d["kube_vers"]) >= version.parse(min_limit)]

dump_tool_data("helm", {
  "home": home,
  "sources": sources,
  "compat_source": compat_source,
  "compat_matrix": compat_data
})
