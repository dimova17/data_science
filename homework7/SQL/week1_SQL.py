import psycopg2
import psycopg2.extras
from pprint import pprint as pp
from tabulate import tabulate

conn = psycopg2.connect("host=localhost port=5432 dbname=odscourse user=postgres password=secret")
cursor = conn.cursor() # cursor_factory=psycopg2.extras.DictCursor)


def fetch_all(cursor):
    colnames = [desc[0] for desc in cursor.description]
    records = cursor.fetchall()
    return [{colname:value for colname, value in zip(colnames, record)} for record in records]


cursor.execute("SELECT * FROM heart_disease LIMIT 5")
records = cursor.fetchall()
print(records)

cursor.execute(
    """
    SELECT cardio, COUNT(*)
        FROM heart_disease
        GROUP BY cardio
    """
)
print('Распределение целевого признака: ')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute(
    """
    SELECT gender, AVG(height), COUNT(gender)
        FROM heart_disease
        GROUP BY gender
    """
)
print('Средний рост по различным значениям пола и количество мужчин и женщин: ')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute("SELECT gender, AVG(alco) FROM heart_disease GROUP BY gender ")
print('2. Кто в среднем реже указывает, что употребляет алкоголь: мужчины или женщины? ')
print(tabulate(fetch_all(cursor), "keys", "psql"))


cursor.execute(
    """
    SELECT ROUND(((SELECT AVG(smoke) FROM heart_disease WHERE gender=2) / 
    (SELECT AVG(smoke) FROM heart_disease WHERE gender=1)::numeric), 2)
        FROM heart_disease LIMIT 1;
    """
)
print('3. Во сколько раз процент курящих среди мужчин больше, чем процент курящих среди женщин?')
print(tabulate(fetch_all(cursor), "keys", "psql"))

cursor.execute("SELECT AVG(age) FROM heart_disease")
print('4.В чём измеряется возраст, и на сколько месяцев отличаются медианные значения возраста курящих и некурящих?')
print('Возраст, вероятно, указан в днях: ')
print(tabulate(fetch_all(cursor), "keys", "psql"))

# Добавляем функцию нахождения медианы
cursor.execute("""
      CREATE OR REPLACE FUNCTION _final_median(NUMERIC[])
        RETURNS NUMERIC AS
      $$
      SELECT AVG(val)
        FROM (
      SELECT val
        FROM unnest($1) val
        ORDER BY 1
        LIMIT  2 - MOD(array_upper($1, 1), 2)
        OFFSET CEIL(array_upper($1, 1) / 2.0) - 1
       ) sub;
      $$
      LANGUAGE 'sql' IMMUTABLE;

      CREATE AGGREGATE median(NUMERIC) (
        SFUNC=array_append,
        STYPE=NUMERIC[],
        FINALFUNC=_final_median,
        INITCOND='{}'
)
""")

cursor.execute(
    """
    SELECT DISTINCT ROUND((SELECT median(age)/30 FROM heart_disease WHERE smoke = 0) -
      (SELECT median(age)/30 FROM heart_disease WHERE smoke = 1))
      FROM heart_disease
"""
)
print('Разница в месяцах: ')
print(tabulate(fetch_all(cursor), "keys", "psql"))

# ДОбавляем возраст в годах
cursor.execute("""
    ALTER TABLE heart_disease
    ADD COLUMN IF NOT EXISTS years INTEGER;
    UPDATE heart_disease SET years = round(age/365.25)
""")

"""Отберите курящих мужчин от 60 до 64 лет включительно:
1 - с верхним артериальным давлением строго меньше 120 мм рт.ст. и концентрацией холестерина = 4 ммоль/л, 
2 - с верхним артериальным давлением от 160(включительно) до 180 мм рт.ст.(не включительно) и концентрацией холестерина = 8 ммоль/л.
"""

cursor.execute("""
    SELECT (SELECT avg(cardio) FROM heart_disease 
      WHERE gender = 2 AND smoke = 1 AND ap_hi >= 160 
      AND ap_hi < 180 AND cholesterol = 3 AND years >= 60 AND years <= 64 ) /
    (SELECT avg(cardio) FROM heart_disease 
      WHERE gender = 2 AND smoke = 1 AND ap_hi < 120 AND cholesterol = 1 AND years >= 60 AND years <= 64)
    FROM heart_disease LIMIT 1;

""")
print('5.Во сколько раз отличаются доли больных людей в двух подвыборках?')
print(tabulate(fetch_all(cursor), "keys", "psql"))


""" 6.Построить новый признак - Индекс массы тела. Нормальными считаются значения от 18.5 до 25.
    Выбрать верные утверждения:
     1) Медианный BMI по выборке превышает норму
     2)У женщин в среднем BMI ниже, чем у мужчин
     3)У здоровых в среднем BMI выше, чем у больных
     4) В сегменте здоровых и непьющих мужчин в среднем BMI ближе к норме, чем в сегменте здоровых и непьющих женщин
     """

cursor.execute("""
    ALTER TABLE heart_disease
    ADD COLUMN IF NOT EXISTS  BMI INTEGER;
    UPDATE heart_disease SET BMI  = weight / (height / 100)^ 2
""")

cursor.execute("""
    SELECT median(BMI) FROM heart_disease; 
    SELECT (SELECT AVG(BMI) FROM heart_disease WHERE gender=1), (SELECT AVG(BMI) FROM heart_disease WHERE gender=2)
    FROM heart_disease LIMIT 1; 
    SELECT (SELECT AVG(BMI) FROM heart_disease WHERE cardio=0), (SELECT AVG(BMI) FROM heart_disease WHERE cardio=1)
    FROM heart_disease LIMIT 1; 
    SELECT (SELECT AVG(BMI) FROM heart_disease WHERE gender=1 AND alco=0 AND cardio = 0),
       (SELECT AVG(BMI) FROM heart_disease WHERE gender=2 AND alco=0 AND cardio = 0)
       FROM heart_disease LIMIT 1; 
""")
print(tabulate(fetch_all(cursor), "keys", "psql"))


"""Отфильтруйте следующие сегменты пациентов (считаем это ошибками в данных):
- указанное нижнее значение артериального давления строго выше верхнего;
- рост строго меньше 2.5%-перцентили или строго больше 97.5%-перцентили;
- вес строго меньше 2.5%-перцентили или строго больше 97.5%-перцентили.

Сколько процентов данных мы выбросили?"""

cursor.execute("""
        SELECT DISTINCT 100 - (
    (SELECT COUNT(*) FROM heart_disease
    WHERE ap_lo <= ap_hi 
    AND height >= (SELECT PERCENTILE_DISC(0.025) WITHIN GROUP (ORDER BY height) FROM heart_disease) 
     AND height <= (SELECT PERCENTILE_DISC(0.975) WITHIN GROUP (ORDER BY height) FROM heart_disease)
     AND weight >= (SELECT PERCENTILE_DISC(0.025) WITHIN GROUP (ORDER BY weight) FROM heart_disease)
     AND weight <= (SELECT PERCENTILE_DISC(0.975) WITHIN GROUP (ORDER BY weight) FROM heart_disease))* 100)
     / (SELECT COUNT(*) FROM heart_disease)
     FROM heart_disease
 """)
print('7.Сколько процентов данных мы выбросили после фильтрования?')
print(tabulate(fetch_all(cursor), "keys", "psql"))
