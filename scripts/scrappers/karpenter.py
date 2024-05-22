#!/usr/bin/env python3

import requests
import yaml
from packaging import version

from __utils import dump_tool_data

home = "https://karpenter.sh/"
sources = "https://github.com/aws/karpenter-provider-aws"
compat_source = "https://raw.githubusercontent.com/aws/karpenter-provider-aws/main/hack/docs/compatibility-karpenter.yaml"

page = requests.get(compat_source)
data = yaml.safe_load(page.text)

kube_versions = set(
  [
    str(d[k])
    for d in data["compatibility"]
    for k in ["minK8sVersion", "maxK8sVersion"]
  ])

# Some versions are missing, because they are implied by a range, but excluded from next range
# Example: missing v1.22
# - appVersion: 0.27.x
#   minK8sVersion: 1.21
#   maxK8sVersion: 1.25
# - appVersion: 0.28.x
#   minK8sVersion: 1.23
#   maxK8sVersion: 1.27

# To fix it, just increment minor version from min to max
kube_versions = [
  f"1.{v}" for v in range(
    version.parse(min(kube_versions, key=lambda i: version.parse(i))).minor,
    version.parse(max(kube_versions, key=lambda i: version.parse(i))).minor + 1,
  )]

# Convert to our format: instead of sorting by appVersion with compatible k8s ranges,
# sort by k8s version with app compatible ranges.
compat_data = []
for kube_ver in kube_versions:
  # Retrieve all karpenter version where minK8sVersion <= kube_ver <= maxK8sVersion
  karpenter_vers = sorted([
    d["appVersion"]
    for d in data["compatibility"]
    if version.parse(str(d["minK8sVersion"])) <= version.parse(kube_ver) <= version.parse(str(d["maxK8sVersion"]))
  ], key=lambda v: version.parse(v.rstrip(".x")))

  compat_data.append({
    "kube_vers": f"v{kube_ver}",
    "versions": {
      "min": karpenter_vers[0],
      "max": karpenter_vers[-1]
    }
  })

dump_tool_data("karpenter", {
  "home": home,
  "sources": sources,
  "compat_source": compat_source,
  "compat_matrix": compat_data
})
