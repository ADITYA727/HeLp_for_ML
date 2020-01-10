Install pyenv from https://github.com/pyenv/pyenv.
###################################################

git clone https://github.com/pyenv/pyenv.git ~/.pyenv
pyenv install 3.6.0
pyenv virtualenv 3.6.0 stp
pyenv activate stealth

Install required packages
#########################

cd directory-of-code
pip install -r requirements.txt





