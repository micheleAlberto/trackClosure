#installare dipendenze di openMVG e openCV
```
apt-get update && apt-get install -y \
  build-essential \
  cmake \
  graphviz \
  git \
  gcc-4.8 \ 
  gcc-4.8-multilib \  
  libpng-dev \
  libjpeg-dev \
  libtiff-dev \
  libxxf86vm1 \
  libxxf86vm-dev \
  libxi-dev \
  libxrandr-dev \
  python-dev \  
  python-pip \
  python-virtualenv\
  python-numpy \
  python-scipy \
  python-matplotlib \
  ipython\
  python-opencv \
  python-matplotlib \
  python-pandas \
```
#installare utilità python 
```
pip install ipython ipdb seaborn scipy sklearn
```
#installare openMVG
In questo esempio openMvg viene installato in /opt
```
cd /opt  
git clone https://github.com/openMVG/openMVG.git
cd openMVG 
git submodule update --init --recursive

mkdir openMVG_Build
mkdir openMVG_Build/install
cd openMVG_Build
cmake -DCMAKE_BUILD_TYPE=RELEASE \
        -DCMAKE_INSTALL_PREFIX="/opt/openMVG_Build/install" \
        -DOpenMVG_BUILD_TESTS=ON \
        -DOpenMVG_BUILD_EXAMPLES=ON . /opt/openMVG/src/
make -j8 
make test
make install
cd ..
cd ..
```
#installare TrackClosure
```
git clone https://github.com/micheleAlberto/trackClosure.git
cd trackClosure
python setup.py install
cd ..
```


