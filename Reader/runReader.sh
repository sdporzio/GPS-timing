source /home/lhep/Anaconda/etc/profile.d/conda.sh
conda activate gps
unbuffer python /home/lhep/GPS-timing/Reader/reader.py 2>&1 | tee /home/lhep/GPS-timing/Reader/Log/log.log