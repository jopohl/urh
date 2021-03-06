#!/bin/bash

DIR=$(dirname "$(readlink -f "$0")")

echo "Copy snapcraft.yaml to base directory"
cd $DIR
cp snapcraft.yaml ..
cd ..
sed -i "s/version\: git/version\: $(python3 src/urh/version.py)/" snapcraft.yaml

mkdir -p snap/gui
cp data/icons/appicon.png snap/gui/urh.png 

echo "Create desktop entry for snap"
echo "[Desktop Entry]" > snap/gui/urh.desktop
echo "Type=Application" >> snap/gui/urh.desktop
echo "Name=Universal Radio Hacker" >> snap/gui/urh.desktop
echo "Comment=Investigate Wireless Protocols Like A Boss" >> snap/gui/urh.desktop
echo "Exec=urh" >> snap/gui/urh.desktop
echo "Icon=\${SNAP}/meta/gui/urh.png" >> snap/gui/urh.desktop
echo "Terminal=false" >> snap/gui/urh.desktop

SNAPCRAFT_BUILD_ENVIRONMENT_CPU=8 SNAPCRAFT_BUILD_ENVIRONMENT_MEMORY=24G snapcraft

#sudo snap install --dangerous urh*.snap
#urh
