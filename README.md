# raspberry-mesh
![](https://github.com/janttari/raspberry-mesh/raw/master/doc/mesh%20kaavio.png)

Asennus: 

    sudo raspi-config # --> Localisation Options --> Change WLAN Country
    sudo apt update && sudo apt install -y batctl
    cd ~
    git clone https://github.com/janttari/raspberry-mesh.git


Suorita gateway:

    cd ~/raspberry-mesh
    ./meshgateway

Suorita client:

    cd ~/raspberry-mesh
    ./meshclient

