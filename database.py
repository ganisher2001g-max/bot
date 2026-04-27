import sqlite3

conn = sqlite3.connect('academy.db')
cursor = conn.cursor()

# 1. Eskilarni o'chirib yuboramiz
cursor.execute("DELETE FROM lessons")

# 2. Yangi darslarni qo'shamiz
# Bu yerga o'sha videolarning haqiqiy linklarini qo'ying
darslar = [
    ('wifi', 'Ezviz kamerasini sozlash', 'https://youtube.com/playlist?list=PL_JB_UjrBokcKCOexjG2wrv2ypBsmqoUj&si=rTNPNcacGa-gmpKV'),
    ('wifi', 'Xitoy 360 (No Name) kamerasini sozlash', 'https://youtu.be/CZlIAsPsFEw?si=k4vKU3FqcHDz-0Y6')
]

cursor.executemany("INSERT INTO lessons (category, title, url) VALUES (?, ?, ?)", darslar)

conn.commit()
conn.close()
print("Sklad yangilandi: Ezviz va Xitoy 360 darslari qo'shildi!")