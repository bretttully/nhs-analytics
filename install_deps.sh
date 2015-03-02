#!/bin/bash
sudo apt-get update
sudo apt-get upgrade

# easy installation of python packages
sudo apt-get install python-pip

# scientific python libraries
sudo pip install numpy scipy matplotlib

# for working with excel documents
sudo pip install xlrd

# for working with DataFrame's
sudo pip install pandas

# to enable saving to HDF5
sudo apt-get install hdf5-dev
sudo pip install cython numexpr tables

# for doing some ML
sudo pip install scikit-learn
