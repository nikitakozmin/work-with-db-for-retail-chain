sudo apt update && sudo apt upgrade -y
sudo apt install postgresql postgresql-contrib -y

# psql --version
sudo service postgresql start
# sudo service postgresql status
# sudo systemctl enable postgresql # Для автозапуска

sudo -u postgres psql # Пользователь postgres
