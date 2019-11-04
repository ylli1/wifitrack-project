# wifitrack-project
## Preprocess：
　　split -l 100000 Campus_Analytics_Hashed_201805-201806.json split  
　　sudo nohup python3 -u PerMacPerFile.py &  
　　sudo nohup python3 -u PerMinutePerFile.py &
## Mac address type classification:
　　sudo nohup python3 -u ClassifyDevice.py &
## Start the server:
　　python3 app.py
