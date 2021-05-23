import csv, config, dotaScraper, time


scraper = dotaScraper.dotaScraper(matchesCount=10000, threads=10, api_key=config.API_KEY)

data = scraper.GetData()


with open(str(int(time.time())) + ".csv","w+", newline='') as dataFile:
    csvWriter = csv.writer(dataFile,delimiter=',')
    csvWriter.writerow(["RadiantWin", "Hero1", "Hero2", "Hero3", "Hero4", "Hero5", "Hero6", "Hero7", "Hero8", "Hero9", "Hero10"])
    csvWriter.writerows(data)



#https://dev.dota2.com/forum/dota-2/spectating/replays/webapi/60177-things-you-should-know-before-starting?t=58317
#https://dev.dota2.com/forum/dota-2/spectating/replays/webapi/48733-dota-2-match-history-webapi