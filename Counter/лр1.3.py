import psycopg2
import random
import threading
from tqdm import tqdm
from datetime import datetime
import random

DB_CONFIG = {
    "dbname": "counter",
    "user": "postgres",
    "password": "1111",
    "host": "localhost",
    "port": "5432",
}

def get_counter():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT SUM(counter) FROM user_counter;")
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] or 0  


def reset():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("UPDATE user_counter SET counter = 0, version = 0;")
    conn.commit()
    cur.close()
    conn.close()

def start(method_name, method_func):
    reset()
    print("----------------------------------")
    print(f"{method_name} is running")

    start_time = datetime.now()
    threads = [threading.Thread(target=method_func) for _ in range(10)]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    end_time = datetime.now()

    print(f"Time: {end_time - start_time}")
    print(f"Counter value: {get_counter()}")




def lost_update():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for _ in range(10_000):
        random_id = random.randint(1, 100_000)
        cur.execute("SELECT counter FROM user_counter WHERE user_id = %s;", (random_id,))
        counter = cur.fetchone()[0] + 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = %s;", (counter, random_id))
        conn.commit()
    cur.close()
    conn.close()


    
def in_place_update():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for _ in range(10_000):
        random_id = random.randint(1, 100_000)
        cur.execute("UPDATE user_counter SET counter = counter + 1 WHERE user_id = %s;", (random_id,))
        conn.commit()
    cur.close()
    conn.close()

def row_level_locking():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for _ in range(10_000):
        random_id = random.randint(1, 100_000)
        cur.execute("SELECT counter FROM user_counter WHERE user_id = %s FOR UPDATE;", (random_id,))
        counter = cur.fetchone()[0] + 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = %s;", (counter, random_id))
        conn.commit()
    cur.close()
    conn.close()


def optimistic_concurrency_control():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    for _ in range(10_000):
        while True:
            random_id = random.randint(1, 100_000)
            cur.execute("SELECT counter, version FROM user_counter WHERE user_id = %s;", (random_id,))
            counter, version = cur.fetchone()
            counter += 1
            cur.execute(
                "UPDATE user_counter SET counter = %s, version = %s WHERE user_id = %s AND version = %s;", 
                (counter, version + 1, random_id, version)
            )
            if cur.rowcount > 0:
                conn.commit()
                break
    cur.close()
    conn.close()






conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Створення таблиці
cur.execute("""
    DROP TABLE IF EXISTS user_counter;
    CREATE TABLE user_counter (
        user_id SERIAL PRIMARY KEY,
        counter INTEGER NOT NULL DEFAULT 0,
        version INTEGER NOT NULL DEFAULT 0
    );
""")
conn.commit()

# Масове додавання 100 000 рядків
for _ in tqdm(range(100_000)):
    cur.execute("INSERT INTO user_counter (counter, version) VALUES (0, 0);")
conn.commit()

cur.close()
conn.close()


start("Lost-update", lost_update)
start("In-place update", in_place_update)
start("Row-level locking", row_level_locking)
start("Optimistic concurrency control", optimistic_concurrency_control)



# ================================

results = []

for name, func in [
    ("Lost-update", lost_update),
    ("In-place update", in_place_update),
    ("Row-level locking", row_level_locking),
    ("Optimistic concurrency control", optimistic_concurrency_control),
]:
    reset()
    print(f"{name} is running")
    start = datetime.now()
    threads = [threading.Thread(target=func) for _ in range(10)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    end = datetime.now()
    final = get_counter()
    results.append((name, end - start, final))
import matplotlib.pyplot as plt

# Розділяємо дані з твого списку results
names = [r[0] for r in results]
times = [r[1].total_seconds() for r in results]  # час у секундах
counters = [r[2] for r in results]
expected = 10_000 * 10
lost_updates = [expected - c for c in counters]

# Побудова графіків
plt.figure(figsize=(14, 6))

# Графік часу виконання
plt.subplot(1, 2, 1)
plt.bar(names, times, color="skyblue")
plt.title("Час виконання (секунди)")
plt.ylabel("Секунди")
plt.xticks(rotation=15)

# Графік втрат оновлень
plt.subplot(1, 2, 2)
plt.bar(names, lost_updates, color="salmon")
plt.title("Втрачені оновлення")
plt.ylabel("Кількість")
plt.xticks(rotation=15)

plt.tight_layout()
plt.show()