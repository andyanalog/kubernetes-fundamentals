from flask import Flask, request, jsonify
import sqlite3
import uuid
import os
from datetime import datetime

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('/storage/jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id TEXT PRIMARY KEY,
                  input_filename TEXT,
                  output_filename TEXT,
                  operation TEXT,
                  status TEXT,
                  created_at TEXT,
                  updated_at TEXT,
                  message TEXT)''')
    conn.commit()
    conn.close()

@app.route('/jobs', methods=['POST'])
def create_job():
    data = request.json
    job_id = str(uuid.uuid4())
    
    conn = sqlite3.connect('/storage/jobs.db')
    c = conn.cursor()
    c.execute('''INSERT INTO jobs 
                 (id, input_filename, output_filename, operation, status, created_at)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (job_id, data['input_filename'], data['output_filename'],
               data['operation'], 'queued', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    return jsonify({'job_id': job_id}), 201

@app.route('/jobs/next', methods=['GET'])
def get_next_job():
    conn = sqlite3.connect('/storage/jobs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM jobs WHERE status = "queued" LIMIT 1')
    row = c.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'id': row[0],
            'input_filename': row[1],
            'output_filename': row[2],
            'operation': row[3],
            'resolution': '720x480'  # Default resolution
        })
    else:
        return jsonify({'message': 'No jobs available'}), 404

@app.route('/jobs/<job_id>/status', methods=['POST'])
def update_job_status(job_id):
    data = request.json
    
    conn = sqlite3.connect('/storage/jobs.db')
    c = conn.cursor()
    c.execute('''UPDATE jobs 
                 SET status = ?, updated_at = ?, message = ?
                 WHERE id = ?''',
              (data['status'], datetime.now().isoformat(),
               data.get('message', ''), job_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/jobs', methods=['GET'])
def list_jobs():
    conn = sqlite3.connect('/storage/jobs.db')
    c = conn.cursor()
    c.execute('SELECT * FROM jobs ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    jobs = []
    for row in rows:
        jobs.append({
            'id': row[0],
            'input_filename': row[1],
            'output_filename': row[2],
            'operation': row[3],
            'status': row[4],
            'created_at': row[5],
            'updated_at': row[6],
            'message': row[7]
        })
    
    return jsonify(jobs)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
