import requests, csv, concurrent.futures, threading, sys, time

class dotaScraper:
    __getDetails = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/'
    __getHistory = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/'
    __threadLock = threading.Lock()
    __matchListCount = 0
    __progressActive = True

    def __init__(self, matchesCount, threads, api_key):
        self.matchesCount = matchesCount
        self.threads = threads
        self.api_key = api_key


    def __findMatches(self):
        matchesFound = []
        nextStartMatchID = 0

        while len(matchesFound) <= self.matchesCount:
            params = dict(key=self.api_key, skill=3)
            if nextStartMatchID != 0:
                params['start_at_match_id'] = nextStartMatchID
                nextStartMatchID = 0

            resp = requests.get(url=self.__getHistory, params=params)
            data = resp.json()

            try:
                for match in data['result']['matches']:
                    if match['lobby_type'] == 7:
                        if nextStartMatchID == 0:
                            nextStartMatchID = match['match_id'] - 50
                        matchesFound.append(match['match_id'])
                        sys.stdout.write("\rMatchFound: " + str(match['match_id']) + " - Progress:" + str(len(matchesFound)) + "/" + str(self.matchesCount))
                        sys.stdout.flush()


            except KeyError:
                if nextStartMatchID == 0:
                    nextStartMatchID = match['match_id'] - 50
                continue

        sys.stdout.write("\n")
        return matchesFound


    def __create_chunks(self, matchesFound):
        chunkSize = int(len(matchesFound) / self.threads)
        for i in range(0, len(matchesFound), chunkSize):
            yield matchesFound[i:i + chunkSize]

    def __get_match_details(self, matchPool):
        fails = 0
        requestCount = 0
        dataset = []
        for match in matchPool:
            resp = requests.get(url=self.__getDetails, params=dict(match_id=match, key=self.api_key))
            requestCount = requestCount + 1
            if resp.status_code != 200:
                time.sleep(1)
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
                time.sleep(1)
                continue

            dataset.append(matchData)
            with self.__threadLock:
                self.__matchListCount += 1
            time.sleep(0.1)
        return dataset

    def __progress(self, count):
        self.__progressActive = True
        print("\nGetting Match Data for (%d) Matches with (%d) Threads....\n" % (count, self.threads))
        while self.__progressActive:
            percent = float(self.__matchListCount) * 100 / count
            arrow = '-' * int(percent / 100 * 40 - 1) + '>'
            spaces = ' ' * (40 - len(arrow))

            print('\rProgress: [%s%s] %d %% - [%d/%d]' % (arrow, spaces, percent, self.__matchListCount, count), end="")
            time.sleep(1)


    def GetData(self):
        self.__matchListCount = 0

        print("Finding Valid Matches...\n")

        match_ids = self.__findMatches()
        chunks = list(self.__create_chunks(match_ids))


        progress = threading.Thread(target=self.__progress, args=(len(match_ids),))
        progress.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            results = executor.map(self.__get_match_details, chunks)
            data = []

            for value in results:
                data = data + value

            self.__progressActive = False

            with self.__threadLock:
                print(self.__matchListCount)

            print(data)
            print(len(data))

        return data