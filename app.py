from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from dotenv import load_dotenv
import pvc_lib
import threading
import multiprocessing
import time
import json
import os
import tempfile

load_dotenv()

app = Flask(__name__)

# Global state
POINTS = []
CURRENT_PROCESSES = []

# Helper function for multiprocessing
def run_algo_process(algo_name, algo_func, points, queue):
    start_time = time.time()
    try:
        path, length = algo_func(points)
        duration = time.time() - start_time
        queue.put({
            "algo": algo_name,
            "path": path,
            "length": length,
            "time": duration
        })
    except Exception as e:
        print(f"Error running {algo_name}: {e}")
# This allows easy addition/modification of algorithms
ALGORITHMS = [
    {
        "id": "ppp",
        "name": "Point le Plus Proche (PPP)",
        "func": pvc_lib.ppp
    }
    # Add more algorithms here
]

@app.route('/')
def index():
    max_points = os.environ.get('MAX_RANDOM_POINTS')
    return render_template('index.html', points=POINTS, max_points=max_points)

@app.route('/upload', methods=['POST'])
def upload():
    global POINTS
    file = request.files['file']
    if file:
        # Use tempfile to save the uploaded file temporarily
        fd, path = tempfile.mkstemp()
        os.close(fd)  # Close the file descriptor, we only need the path
        try:
            file.save(path)
            # Use the existing function from pvc.py
            POINTS = pvc_lib.lire_points_fichier(path)
        finally:
            # Clean up the temporary file
            if os.path.exists(path):
                os.remove(path)
    return redirect(url_for('index'))

@app.route('/add_point', methods=['POST'])
def add_point():
    global POINTS
    try:
        x = float(request.form['x'])
        y = float(request.form['y'])
        POINTS.append((x, y))
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate():
    global POINTS
    try:
        n = int(request.form['n'])
        max_points = os.environ.get('MAX_RANDOM_POINTS')
        if max_points:
            max_points = int(max_points)
            if n > max_points:
                n = max_points
        
        POINTS = pvc_lib.generer_points(n)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear():
    global POINTS
    POINTS = []
    return redirect(url_for('index'))

@app.route('/solve')
def solve_page():
    return render_template('solve.html', points=POINTS, algos=ALGORITHMS)

@app.route('/run_solve', methods=['POST'])
def run_solve():
    global CURRENT_PROCESSES
    data = request.json
    selected_ids = data.get('algos', [])
    
    queue = multiprocessing.Queue()
    CURRENT_PROCESSES = []
    
    for algo_id in selected_ids:
        algo_conf = next((a for a in ALGORITHMS if a['id'] == algo_id), None)
        if algo_conf:
            p = multiprocessing.Process(
                target=run_algo_process, 
                args=(algo_conf['name'], algo_conf['func'], POINTS, queue)
            )
            CURRENT_PROCESSES.append(p)
            p.start()
    
    # Handle timeout
    timeout_env = os.environ.get('GLOBAL_TIMEOUT')
    timeout = int(timeout_env) if timeout_env else None
    
    start_wait = time.time()
    
    for p in CURRENT_PROCESSES:
        if timeout:
            elapsed = time.time() - start_wait
            remaining = timeout - elapsed
            if remaining < 0:
                remaining = 0
            p.join(remaining)
        else:
            p.join()
            
    # Terminate any still running (due to timeout)
    for p in CURRENT_PROCESSES:
        if p.is_alive():
            p.terminate()
            
    CURRENT_PROCESSES = []
    
    results = []
    while not queue.empty():
        results.append(queue.get())
        
    return jsonify({"results": results})

@app.route('/stop_solve', methods=['POST'])
def stop_solve():
    global CURRENT_PROCESSES
    for p in CURRENT_PROCESSES:
        if p.is_alive():
            p.terminate()
    CURRENT_PROCESSES = []
    return jsonify({"status": "stopped"})

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/rapport')
def rapport():
    return render_template('rapport.html')

@app.route('/rapport/pdf')
def rapport_pdf():
    return send_from_directory('rapport', 'rapport.pdf')

if __name__ == '__main__':
    app.run(debug=True)
