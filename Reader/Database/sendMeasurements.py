import subprocess

db_url = "http://130.92.128.162"
db_port = 8086
db_name = "slowcontrol"

def SendMeasurement(varName,value):
    post = f'{varName} value={value}'
    subprocess.call(["curl", "-i", "-XPOST", db_url+":"+str(db_port)+"/write?db="+db_name,"--data-binary", post],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)