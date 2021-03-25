while true
do
    sleep 6000
    cp /home/lhep/GPS-timing/Reader/Log/currentLog.log /home/lhep/GPS-timing/Reader/Log/backupLog.log 
    cp /home/lhep/GPS-timing/Reader/Log/emptyLog.log /home/lhep/GPS-timing/Reader/Log/currentLog.log 
done