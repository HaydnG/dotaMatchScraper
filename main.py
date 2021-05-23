import requests, csv, concurrent.futures
import threading,config
threadLock = threading.Lock()

matchListCount = 0

threads = 10
matches = 2000

def divide_chunks(list, n):
    for i in range(0, len(list), n):
        yield list[i:i + n]


getDetails = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/'
getHistory = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/'
token = config.API_KEY

def GetMatchDetails(matchPool):
    global matchListCount
    fails = 0
    requestCount = 0
    dataset = []
    for match in matchPool:
        resp = requests.get(url=getDetails, params=dict(match_id=match, key=token))
        requestCount = requestCount + 1
        if resp.status_code != 200:
            fails = fails + 1
            if fails > 10:
                break
            continue

        data = resp.json()

        try:
            if data['result']['lobby_type'] != 7:
                continue
            if data['result']['duration'] < 600:
                continue

            matchData = []
            matchData.append(int(data['result']['radiant_win']))

            for player in data['result']['players']:
                matchData.append(player['hero_id'])
        except KeyError:
            continue

        dataset.append(matchData)
        with threadLock:
            matchListCount += 1
            if matchListCount % 10 == 0:
                print(matchListCount)
    return dataset



matchesFound = []
nextStartMatchID = 0

while len(matchesFound) <= matches:
    params = dict(key=token, skill=3)
    if nextStartMatchID != 0:
        params['start_at_match_id'] = nextStartMatchID
        nextStartMatchID = 0

    resp = requests.get(url=getHistory, params=params)
    data = resp.json()

    try:
        for match in data['result']['matches']:
            if match['lobby_type'] == 7:
                if nextStartMatchID == 0:
                    nextStartMatchID = match['match_id'] - 50
                matchesFound.append(match['match_id'])
                print("MatchFound: " + str(match['match_id']))
    except KeyError:
        if nextStartMatchID == 0:
            nextStartMatchID = match['match_id'] - 50
        continue


chunks = list(divide_chunks(matchesFound, int(len(matchesFound) / threads)))
print("Getting Match Details")
with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    results = executor.map(GetMatchDetails, chunks)
    data = []

    for value in results:
        data = data + value

    with threadLock:
        print(matchListCount)

    print(data)
    print(len(data))









with open("data.csv","w+", newline='') as dataFile:
    csvWriter = csv.writer(dataFile,delimiter=',')
    csvWriter.writerows(data)


#https://realpython.com/intro-to-python-threading/