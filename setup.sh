echo "Installing Pika...."
pip3 install pika
echo "Installing MongoDB...."
sudo apt update
sudo apt upgrade
sudo apt install mongodb
echo "Starting up MongoDB Service...."
sudo systemctl enable mongodb
sudo systemctl start mongodb
echo "Installing PyMongo...."
pip3 install 'pymongo==2.8'
