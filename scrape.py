import json, requests, pprint, sys
import time


highWaterMark = 1575463332
failed = False
appendMode = False


if(not appendMode):
    playersFile = open("players.json", "w")
    gamesFile = open("games.json", "w")
    playersFile.write('[\n')
    gamesFile.write('[\n')
    playersFile.close()
    gamesFile.close()

playersFile = open("players.json", "a")
gamesFile = open("games.json", "a")
while(not failed):
    print('high water mark', highWaterMark)
    params = {
        'game':'aoe2de',
        'count':1000,
        'since':1575463332
    }
    x = requests.get('https://aoe2.net/api/matches', params)
    if(x.status_code != 200):
        failed = True
    else:
        #write x to file long term
        for each in json.loads(x.content):
            if(each['started'] > highWaterMark):
                highWaterMark = each['started']
            if(each['ranked'] ):#and len(each['players']) == 2):
                matchData = each
                playerData = each['players']
                for player in playerData:
                    player['match_uuid'] = each['match_uuid']
                    playersFile.write(json.dumps(player, indent=4))
                    playersFile.write(',')
                del matchData['players']
                gamesFile.write(json.dumps(matchData, indent=4))
                gamesFile.write(',')
    time.sleep(3)

playersFile.write('\n]')
gamesFile.write('\n]')
