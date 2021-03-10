import json, requests, pprint, sys, os, time
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

def progress(status, remaining, total):
    print('\r', end='')                     # use '\r' to go back
    print(f'{"{:.2%}".format(float(total-remaining)/total)} backed up...', end='', flush=True)

def insertBatch(curs, playerData, matchData):
    #playerData
    playerDataKeys = ','.join(list(playerData[0]))
    playerQuestionMarks = ','.join('?' for each in list(playerData[0]))
    playerDataValues = [tuple(dic.values()) for dic in playerData]

    #matchData
    matchDataKeys = ','.join(list(matchData[0]))
    matchQuestionMarks = ','.join('?' for each in list(matchData[0]))
    matchDataValues = [tuple(dic.values()) for dic in matchData]

    try:
        curs.executemany("INSERT INTO matchData("+matchDataKeys+") VALUES (" + matchQuestionMarks + ")", matchDataValues)
        curs.executemany("INSERT INTO playerData("+playerDataKeys+") VALUES (" + playerQuestionMarks + ")", playerDataValues)
    except:
        #print('Entire batch failed, inserting individually')
        for each in matchDataValues:
            try:
                curs.executemany("INSERT INTO matchData("+matchDataKeys+") VALUES (" + matchQuestionMarks + ")", [each])
            except:
                #print("failed to insert ", each)
                pass
        for each in playerDataValues:
            try:
                curs.executemany("INSERT INTO playerData("+playerDataKeys+") VALUES (" + playerQuestionMarks + ")", [each])
            except:
                #print("failed to insert ", each)
                pass
def backUp(db_path, conn):
    #create backup of DB file
    print('Backing up', db_path)
    backup_db_path = (db_path + ".bak")
    conn = sqlite3.connect(db_path)
    if os.path.exists(backup_db_path):
        os.rename(backup_db_path, backup_db_path+'_old') #remove last db dump to an "old version"
    bck = sqlite3.connect(backup_db_path)
    with bck:
        conn.backup(bck, pages=1, progress=progress)
    bck.close()
    print('[Done]')


def saveDataFiles():
    print('Fetching Data Files...', end='')
    data = requests.get('https://aoe2.net/api/strings?game=aoe2de&language=en').json()
    civFile = open("./dataFiles.json", "w")
    civFile.write(json.dumps(data, indent=4))
    print('[Done]')

if __name__ == '__main__':
    #TODO set high water mark to select max(xxx)
    stop = False
    db_path = ("./database/pythonsqlite.db")
    conn = sqlite3.connect(db_path)
    backUp(db_path, conn)
    saveDataFiles()
    print('Getting High Water Mark...', end='')
    c = conn.cursor()
    HIGH_WATER_MARK = c.execute('select max(started) as highWaterMark from matchData md').fetchone()[0] or 0
    STARTING_HIGH_WATER_MARK = HIGH_WATER_MARK
    EPOCH_TIME_AT_START = int(time.time())
    print('[Done]')
    print('Starting Scrape. Current Epoch Time:', EPOCH_TIME_AT_START)
    while(not stop):
        #If starting at zero, set start to high water mark
        if(HIGH_WATER_MARK != 0 and STARTING_HIGH_WATER_MARK == 0):
            STARTING_HIGH_WATER_MARK = HIGH_WATER_MARK
        PERCENT_FINISHED = float(HIGH_WATER_MARK - STARTING_HIGH_WATER_MARK) / ((int(time.time()) - STARTING_HIGH_WATER_MARK) or 1)
        print('\r', end='')
        print(f'{HIGH_WATER_MARK} {"{:.2%}".format(PERCENT_FINISHED)} scraped...', end='', flush=True)

        #scraping params
        params = {
            'game':'aoe2de',
            'count':1000,
            'since':HIGH_WATER_MARK
        }
        x = requests.get('https://aoe2.net/api/matches', params)
        if(x.status_code != 200):
            stop = True
        else:
            #write x to file long term
            playerBatch = []
            matchBatch = []
            data = json.loads(x.content)
            if(len(data) == 0):
                stop = True
            for each in data:
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
                stop = True
        time.sleep(.5)
    print('[Done]')
    conn.close()
    print('Database Is Up To Date')

