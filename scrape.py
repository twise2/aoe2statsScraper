import json, requests, pprint, sys
import time
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def insertBatch(curs, playerData, matchData):
    #playerData
    playerDataKeys = ','.join(list(playerData[0]))
    playerQuestionMarks = ','.join('?' for each in list(playerData[0]))
    playerDataValues = [tuple(dic.values()) for dic in playerData]

    #matchData
    matchDataKeys = ','.join(list(matchData[0]))
    matchQuestionMarks = ','.join('?' for each in list(matchData[0]))
    matchDataValues = [tuple(dic.values()) for dic in matchData]

    #print('playerDataKeys', playerDataKeys)
    #print('playerQuestionMarks', playerQuestionMarks)
    #for value in playerDataValues:
    #    print('values', value)
    #insert the data
    curs.executemany("INSERT INTO playerData("+playerDataKeys+") VALUES (" + playerQuestionMarks + ")", playerDataValues)
    curs.executemany("INSERT INTO matchData("+matchDataKeys+") VALUES (" + matchQuestionMarks + ")", matchDataValues)


if __name__ == '__main__':
    #TODO set high water mark to select max(xxx)
    stop = False
    db_path = ("./database/pythonsqlite.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    HIGH_WATER_MARK = c.execute('select max(started) as highWaterMark from matchData md').fetchone()[0]

    data = requests.get('https://aoe2.net/api/strings?game=aoe2de&language=en').json()
    civFile = open("./dataFiles.json", "w")
    civFile.write(json.dumps(data, indent=4))

    while(not stop):
        print('High Water Mark', HIGH_WATER_MARK)
        params = {
            'game':'aoe2de',
            'count':10000,
            'since':HIGH_WATER_MARK
        }
        x = requests.get('https://aoe2.net/api/matches', params)
        if(x.status_code != 200):
            stop = True
        else:
            #write x to file long term
            playerBatch = []
            matchBatch = []
            for each in json.loads(x.content):
                if(each['started'] > HIGH_WATER_MARK):
                    newHighWaterMark = each['started']
                matchData = each
                playerData = each['players']
                for player in playerData:
                    player['match_uuid'] = each['match_uuid']
                    playerBatch.append(player)
                del matchData['players']
                matchBatch.append(matchData)
            insertBatch(c,playerBatch,matchBatch)
            conn.commit()
            if(newHighWaterMark > HIGH_WATER_MARK):
                HIGH_WATER_MARK = newHighWaterMark
            else:
                failed = True
        time.sleep(.5)
    conn.close()

