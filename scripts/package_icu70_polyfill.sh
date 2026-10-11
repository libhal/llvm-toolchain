#!/usr/bin/env bash
# Copyright 2026 Khalil Estell and the libhal contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Builds Linux_armv8-icu70.tar.gz for the llvm-23-polyfill release.
#
# LLVM 23.1.2's official Linux ARM64 release links lld (ld.lld) against ICU 70,
# which only Ubuntu 22.04 ships. lld's RUNPATH includes $ORIGIN/../lib, so the
# recipe extracts these libraries into the package's lib/ directory.
#
# The libraries are copied unmodified from Ubuntu 22.04's libicu70 arm64
# package, verified against the SHA256 from Ubuntu's package index.
#
# Usage: scripts/package_icu70_polyfill.sh [output_dir]

set -euo pipefail

DEB_URL="http://ports.ubuntu.com/ubuntu-ports/pool/main/i/icu/libicu70_70.1-2_arm64.deb"
DEB_SHA256="ac68372cf4a976e6a206858fd9b28c68e49d37d650b9b8653270038a6e7bc174"
OUTPUT_DIR="$(cd "${1:-.}" && pwd)"
ARCHIVE="${OUTPUT_DIR}/Linux_armv8-icu70.tar.gz"

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "${WORK_DIR}"' EXIT
cd "${WORK_DIR}"

curl -fsSL "${DEB_URL}" -o libicu70.deb
if command -v sha256sum >/dev/null; then
  echo "${DEB_SHA256}  libicu70.deb" | sha256sum -c -
else
  echo "${DEB_SHA256}  libicu70.deb" | shasum -a 256 -c -
fi

# A .deb is an ar archive; the files live in data.tar.*
ar x libicu70.deb
mkdir data
tar -xf data.tar.* -C data

mkdir -p icu70/lib
for lib in libicuuc libicui18n libicudata; do
  # Copy the real file under the SONAME that lld asks for (libicu*.so.70)
  cp -L "data/usr/lib/aarch64-linux-gnu/${lib}.so.70" "icu70/lib/${lib}.so.70"
done
cp data/usr/share/doc/libicu70/copyright icu70/LICENSE.icu70

tar -czf "${ARCHIVE}" -C icu70 lib LICENSE.icu70
echo "Created ${ARCHIVE}"
if command -v sha256sum >/dev/null; then
  sha256sum "${ARCHIVE}"
else
  shasum -a 256 "${ARCHIVE}"
fi
