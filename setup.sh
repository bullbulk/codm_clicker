cd "$HOME" || exit
apt update && apt install wget && wget https://github.com/MasterDevX/Termux-ADB/raw/master/InstallTools.sh
bash "$HOME/InstallTools.sh"
apt install python
apt install tesseract
apt install git
git clone https://github.com/bullbulk/codm_clicker.git
cd codm_clicker || exit
pip install -r "$HOME/codm_clicker/requirements.txt"
cd "$HOME" || exit
echo "cd $HOME/codm_clicker" > clicker.sh
echo "python main.py" >> clicker.sh
echo "alias clicker='bash $HOME/clicker.sh'" >> "$HOME/../usr/etc/bash.bashrc"
rm "$HOME/setup.sh"
exit