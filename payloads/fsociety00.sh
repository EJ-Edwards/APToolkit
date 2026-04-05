#!/bin/bash
# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root/sudo"
  sudo "$0" "$@"
  exit $?
fi
# Set target dir
TARGET_DIR="$HOME/.local/share/fsociety00"
mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR" || exit
# create the readme
cat <<EOF > readme.txt
-----readme.txt-----

LEAVE ME HERE

-----readme.txt-----
EOF
# secondary payload
cat <<EOF > fsociety00_payload.sh
#!/bin/bash
# persistence logic
(crontab -l 2>/dev/null; echo "@reboot $TARGET_DIR/fsociety00_payload.sh") | crontab -
# add your payload commands here
EOF
chmod +x fsociety00_payload.sh
# Run the payload in the background
nohup ./fsociety00_payload.sh >/dev/null 2>&1 &
exit 0
