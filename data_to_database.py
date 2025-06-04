import sqlite3
import re
from datetime import datetime

# ====================== Helper Functions ======================

def pad_value(value, pad_char, length):
    return value.zfill(length)

# ====================== DTG Utility ======================

class DTG:
    @staticmethod
    def string_to_dtg(date_str):
        try:
            return int(datetime.strptime(date_str, "%d%H%M:%SZ %b %Y").timestamp() * 1000)
        except ValueError:
            return -1

# ====================== Line Processing ======================

def process_line(line):
    line = line.strip()
    line = re.sub(r"  +", " ", line)

    try:
        parts = line.split()
        MM, DD, YY = parts[0].split("/")
        HH, MN, SS = parts[1].split(":")
        NS, LT_DEG, LT_MIN = parts[2], parts[3], parts[4]
        EW, LG_DEG, LG_MIN = parts[5], parts[6], parts[7]
        ALT, SPD, CSE, _ = parts[8], parts[9], parts[10], parts[11]

        lat = (1.0 if NS == "N" else -1.0) * (float(LT_DEG) + float(LT_MIN) / 60.0)
        lng = (1.0 if EW == "E" else -1.0) * (float(LG_DEG) + float(LG_MIN) / 60.0)
        spd = float(SPD)
        cse = float(CSE)

        # Format date string
        MM = pad_value(MM, "0", 2)
        DD = pad_value(DD, "0", 2)
        HH = pad_value(HH, "0", 2)
        MN = pad_value(MN, "0", 2)
        SS = pad_value(SS, "0", 2)
        YY = pad_value(YY, "0", 2)

        dtg_str = f"{DD}{HH}{MN}:{SS}Z {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][int(MM)-1]} 20{YY}"
        dtg = DTG.string_to_dtg(dtg_str)
        if dtg == -1:
            dtg = int(datetime.now().timestamp() * 1000)

        return {
            "timestamp": dtg,
            "latitude_deg": float(LT_DEG),
            "latitude_min": float(LT_MIN),
            "longitude_deg": float(LG_DEG),
            "longitude_min": float(LG_MIN),
            "speed": spd,
            "course": cse
        }

    except Exception as e:
        print(f"Error processing line: {e}")
        return None

# ====================== Database Operations ======================

def create_database(db_path='nav_data.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS nav (
            timestamp TEXT,
            latitude_deg REAL,
            latitude_min REAL,
            longitude_deg REAL,
            longitude_min REAL,
            speed REAL,
            course REAL
        )
    """)
    conn.commit()
    conn.close()

def insert_data(parsed_data, db_path='nav_data.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for nav in parsed_data:
        c.execute("""
            INSERT INTO nav (timestamp, latitude_deg, latitude_min, longitude_deg, longitude_min, speed, course)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nav['timestamp'],
            nav['latitude_deg'],
            nav['latitude_min'],
            nav['longitude_deg'],
            nav['longitude_min'],
            nav['speed'],
            nav['course']
        ))
    conn.commit()
    conn.close()

def fetch_all_data(db_path='nav_data.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM nav")
    rows = c.fetchall()
    conn.close()
    return rows

def print_parsed_rows(rows):
    for row in rows:
        try:
            readable_ts = datetime.fromtimestamp(int(row[0]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            print(f"{readable_ts}, Lat: {row[1]}° {row[2]}' "
                  f"Lon: {row[3]}° {row[4]}', Speed: {row[5]} knots, Course: {row[6]}°")
        except Exception as e:
            print(f"Error printing row {row}: {e}")


# ====================== Main Execution ======================

def main():
    raw_data = """
    01/23/08 19:59:32  N  33 08.885 W 120 13.550  00000 14.8 304.9 000
    01/23/08 19:59:33  N  33 08.887 W 120 13.553  00000 14.8 304.9 000
    01/23/08 19:59:34  N  33 08.889 W 120 13.558  00000 14.8 304.9 000
    01/23/08 19:59:35  N  33 08.892 W 120 13.562  00000 14.8 304.9 000
    """.strip().splitlines()

    parsed_data = [process_line(line) for line in raw_data if process_line(line)]

    create_database()
    insert_data(parsed_data)

    rows = fetch_all_data()
    print_parsed_rows(rows)

# ====================== Run Script ======================

if __name__ == "__main__":
    main()
