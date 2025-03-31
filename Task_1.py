import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Take only YYYY-MM-DD HH:MM:SS
cursor.execute("UPDATE leads SET created_at = substr(created_at, 1, 19);")
cursor.execute("UPDATE leads SET updated_at = substr(updated_at, 1, 19);")

conn.commit()

# 1.1. The number of created leads per week grouped by course type
query1 = """
SELECT 
    CAST(strftime('%W', (created_at)) AS INTEGER) AS week,
    courses.type,
    COUNT(user_id) AS leads_count
FROM leads
JOIN courses ON courses.id = leads.course_id
GROUP BY week, courses.type
ORDER BY week;
"""
cursor.execute(query1)
results1 = cursor.fetchall()
print("Task 1.1: The number of created leads per week grouped by course type")
for row in results1:
    print(row)

print("\n")

# 1.2. The number of WON flex leads per country created from 01.01.2024
query2 = """
SELECT 
    domains.country_name,
    COUNT(leads.id) AS won_flex_leads_count
FROM domains
JOIN users ON users.domain_id = domains.id
JOIN leads ON leads.user_id = users.id
JOIN courses ON courses.id = leads.course_id 
WHERE leads.status = 'WON'
    AND courses.type = 'FLEX'
    AND (leads.created_at) >= '2024-01-01'
GROUP BY domains.country_name;
"""
cursor.execute(query2)
results2 = cursor.fetchall()
print("Task 1.2: The number of WON flex leads per country created from 01.01.2024")
for row in results2:
    print(row)

print("\n")

# 1.3. User email, lead id and lost reason for users who have lost flex leads from 01.07.2024
query3 = """
SELECT DISTINCT
    users.email,
    leads.id AS lead_id,
    leads.lost_reason
FROM users
JOIN leads ON leads.user_id = users.id
JOIN courses ON courses.id = leads.course_id 
WHERE leads.status = 'LOST'
  AND courses.type = 'FLEX'
  AND (leads.updated_at) >= '2024-07-01'
ORDER BY users.email, leads.lost_reason, leads.id;
"""
cursor.execute(query3)
results3 = cursor.fetchall()
print("Task 1.3: User email, lead id and lost reason for users who have lost flex leads from 01.07.2024")
for row in results3:
    print(row)

conn.close()
