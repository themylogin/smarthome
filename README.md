_Умный дом — грязный дом,_  
_Зато компьютер тихий в нём!_  

Installation notes
==================

python-keybinder
----------------

Debian/Ubuntu package is built without `gobject-introspection` support, so you should do it yourself:
```bash
sudo apt-get install gnome-common gtk-doc-tools python-gobject-2-dev python-gtk2-dev libgirepository1.0-dev
git clone git@github.com:engla/keybinder.git
cd keybinder
./autogen.sh --prefix=/usr
make
sudo make install
```
