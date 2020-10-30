cd $HOME || exit
apt update && apt install wget && wget https://github.com/MasterDevX/Termux-ADB/raw/master/InstallTools.sh && bash InstallTools.sh
pkg install python
pkg install tesseract
git clone https://github.com/bullbulk/codm_clicker.git
cd codm_clicker || exit
pip install -r requirements.txt
echo "cd $HOME/codm_clicker" > clicker.sh
echo "python main.py" >> clicker.sh
echo alias clicker="bash $HOME/clicker.sh"