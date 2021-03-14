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


def createPlayerData(conn):
    conn.execute("""
        CREATE TABLE playerData(
            player_match_id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id,
            steam_id,
            name,
            clan,
            country,
            slot,
            slot_type,
            rating,
            rating_change,
            games,
            wins,
            streak,
            drops,
            color,
            team,
            civ,
            won,
            match_uuid,
            FOREIGN KEY(match_uuid) REFERENCES matchData(match_uuid),
            UNIQUE(profile_id, slot, match_uuid)
    );
                 """)

def createMatchData(conn):
    conn.execute("""
    CREATE TABLE matchData(
      match_id,
      lobby_id,
      match_uuid,
      version,
      name,
      num_players,
      num_slots,
      average_rating,
      cheats,
      full_tech_tree,
      ending_age,
      expansion,
      game_type,
      has_custom_content,
      has_password,
      lock_speed,
      lock_teams,
      map_size,
      map_type,
      pop,
      ranked,
      leaderboard_id,
      rating_type,
      resources,
      rms,
      scenario,
      server,
      shared_exploration,
      speed,
      starting_age,
      team_together,
      team_positions,
      treaty_length,
      turbo,
      victory,
      victory_time,
      visibility,
      opened,
      started,
      finished,
      PRIMARY KEY(match_uuid)
    );
    """)


if __name__ == '__main__':
    db_path = ("./database/pythonsqlite.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    createMatchData(conn)
    conn.execute('CREATE UNIQUE INDEX ix_match_uuid_matchData ON matchData (match_uuid);')
    conn.execute('CREATE INDEX ix_match_started_matchData ON matchData (started);')
    conn.execute('CREATE INDEX ix_num_players_matchData ON matchData (num_players);')
    conn.execute('CREATE INDEX ix_ranked_matchData ON matchData (ranked);')
    conn.execute('create index ix_match_rank_one_v_one_matchData_index on matchData(match_uuid, num_players, ranked)')
    conn.execute('create index ix_match_rank_one_v_one_2_matchData_index on matchData(num_players, ranked)')
    conn.execute('create index ix_match_uuid_rank_one_v_one_2_matchData_index on matchData(num_players, match_uuid)')


    createPlayerData(conn)
    conn.execute('CREATE INDEX ix_match_uuid_playerData ON playerData (match_uuid);')
    conn.execute('CREATE INDEX ix_name_playerData ON playerData (name);')
    conn.execute('CREATE INDEX ix_profile_id_playerData ON playerData (profile_id);')
    conn.execute('CREATE INDEX ix_rating_playerData ON playerData (rating);')
    conn.execute('CREATE INDEX ix_rating_matchid_playerData ON playerData (rating, match_uuid);')
    conn.execute('CREATE INDEX ix_rating_player_data_index ON playerData (rating, profile_id);')
    cursor = conn.execute('select * from matchData')
    print('columns', list(map(lambda x: x[0], cursor.description)))
    cursor = conn.execute('select * from playerData')
    print('columns', list(map(lambda x: x[0], cursor.description)))
    conn.commit()
    conn.close()
