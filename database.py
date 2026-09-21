import os
import psycopg2


connection = psycopg2.connect(
    os.environ["DATABASE_URL"]
)

cursor = connection.cursor()



cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")



cursor.execute("""
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    subject TEXT NOT NULL,
    note_type TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
)
""")



cursor.execute("""
ALTER TABLE notes
ADD COLUMN IF NOT EXISTS user_id INTEGER
""")




cursor.execute("""
DO $$
BEGIN

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'notes_user_id_fkey'
    ) THEN

        ALTER TABLE notes
        ADD CONSTRAINT notes_user_id_fkey
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE;

    END IF;

END
$$
""")


connection.commit()

cursor.close()
connection.close()

print("PostgreSQL database and tables created/updated successfully!")
