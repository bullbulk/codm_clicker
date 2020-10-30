@echo off
cd "$HOME" || exit
apt -y install wget python tesseract git
wget https://github.com/MasterDevX/Termux-ADB/raw/master/InstallTools.sh
bash "$HOME/InstallTools.sh"
git clone https://github.com/bullbulk/codm_clicker.git
cd codm_clicker || exit
pip install -r "$HOME/codm_clicker/requirements.txt"
cd "$HOME" || exit
echo "cd $HOME/codm_clicker" > clicker.sh
echo "python main.py" >> clicker.sh
echo "alias clicker='bash $HOME/clicker.sh'" >> "$HOME/../usr/etc/bash.bashrc"
echo "alias clicker-update='cd $HOME/codm_clicker && git pull'" >> "$HOME/../usr/etc/bash.bashrc"
termux-setup-storage
mkdir -p "/sdcard/codm_clicker"
rm "$HOME/setup.sh"
