# 1. בחר Image בסיסי של אובונטו (גרסת LTS יציבה)
FROM ubuntu:22.04

# הגדרת סביבה למניעת דיאלוגים אינטראקטיביים במהלך התקנות
ENV DEBIAN_FRONTEND=noninteractive

# עדכון מאגרי החבילות והתקנת פייתון
RUN apt-get update && \
    apt-get install -y python3 python3-pip

# יצירת תיקיית לוגים וקובץ לוג בנתיב הנכון
RUN mkdir -p /var/logs && touch /var/logs/log.txt

# יצירת קובץ טוקן עם התוכן הנדרש
RUN echo 'admin_token=4_2-d2l133r-m4-J8a13aG9-43-15Hk_3-H9-M43M_4_' > /etc/token.txt

# הגדרת ספריית העבודה בתוך הקונטיינר
WORKDIR /app

# העתקת קובץ הדרישות והתקנת התלויות של פייתון
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# העתקת כל קבצי האפליקציה
COPY . .

# הפקודה שתרוץ כשהקונטיינר יופעל
CMD ["python3", "backend.py"]
