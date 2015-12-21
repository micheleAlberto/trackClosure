FROM ubuntu:14.04
MAINTAINER Michele Alberto <robbyetor@gmail.com>

#openMvg & openCV Dependencies
RUN apt-get update && apt-get install -y \
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
RUN pip install ipython ipdb seaborn scipy

# Clone the openvMVG repo 
RUN cd /opt  && \
    git clone https://github.com/openMVG/openMVG.git && \
    cd openMVG && \
    git submodule update --init --recursive


# Build
RUN mkdir /opt/openMVG_Build && \
    mkdir /opt/openMVG_Build/install &&\
    cd /opt/openMVG_Build && \
    cmake -DCMAKE_BUILD_TYPE=RELEASE \
        -DCMAKE_INSTALL_PREFIX="/opt/openMVG_Build/install" \
        -DOpenMVG_BUILD_TESTS=ON \
        -DOpenMVG_BUILD_EXAMPLES=ON . /opt/openMVG/src/ && \
    make -j8 && \
    cd /opt/openMVG_Build && \
    make test && \
    make install


WORKDIR /opt/

#docker run -i  \
#    -v /home/michele/dataset/mepComo/data/images:/opt/images \
#    -v /home/michele/dataset/mepComo/data/nuovo:/opt/data \ 
#    -t track_closure

#python -m trackClosure.apps.descriptionMatching images
#python -m trackClosure.apps.tracking images

CMD git clone https://github.com/micheleAlberto/trackClosure.git && \
    cd trackClosure && \
    python setup.py install && \
    bash



