# docker run -it -v C:\\Users\\ansel\\OneDrive\\Documents\\Serval:/mnt/Serval continuumio/miniconda3 /bin/bash
conda env create -f sim.yml
conda activate satSim
apt-get update
apt-get install -y g++
pip install fastlogging