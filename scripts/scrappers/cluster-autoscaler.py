#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from packaging import version

from __utils import dump_tool_data

# Do not retrieve info for kube < v1.19
min_limit = "1.19.0"

home = "https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/README.md"
sources = "https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler"
compat_source = "https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/README.md#releases"

raw_md = requests.get(compat_source).json()["payload"]["blob"]["richText"]
soup = BeautifulSoup(raw_md, "html.parser")

entries = soup.find("table").find("tbody").find_all("tr")

compat_data = []
for entry in entries:
  # Very simple table. There is one exception on kube 1.6.X, but we don't take version down to this point
  # ca_vers: '1.24.X' ; kube_vers: '1.24.X'
  kube_vers, ca_vers = [e.text.replace(".X","") for e in entry.find_all("td")]

  compat_data.append({
    "kube_vers": kube_vers,
    "versions": {
      "min": kube_vers,
      "max": kube_vers,
    }
  })

if min_limit:
  compat_data = [d for d in compat_data if version.parse(d["kube_vers"]) >= version.parse(min_limit)]

dump_tool_data("cluster-autoscaler", {
  "home": home,
  "sources": sources,
  "compat_source": compat_source,
  "compat_matrix": compat_data
})
