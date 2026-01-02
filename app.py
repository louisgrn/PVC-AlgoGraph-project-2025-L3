from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, session
from dotenv import load_dotenv
import pvc_lib
import threading
import multiprocessing
import time
import json
import os
import tempfile
import secrets

load_dotenv()

app = Flask(__name__)
# Generate a secret key for session management
# In production, always set SECRET_KEY environment variable
# The auto-generated key will change on restart, invalidating sessions
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Global state for process management (this can still be global)
CURRENT_PROCESSES = {}

# Server-side session storage to avoid cookie size limits
SERVER_SESSIONS = {}

# Helper functions for session management
def get_session_id():
    """Get or create a unique session ID for tracking processes."""
    if 'session_id' not in session:
        session['session_id'] = secrets.token_hex(16)
    return session['session_id']

def get_points():
    """Get points from the server-side session for the current user."""
    sid = get_session_id()
    if sid not in SERVER_SESSIONS:
        SERVER_SESSIONS[sid] = {'points': []}
    return SERVER_SESSIONS[sid].get('points', [])

def set_points(points):
    """Set points in the server-side session for the current user."""
    sid = get_session_id()
    if sid not in SERVER_SESSIONS:
        SERVER_SESSIONS[sid] = {}
    SERVER_SESSIONS[sid]['points'] = points

# Helper function for multiprocessing
def run_algo_process(algo_name, algo_func, points, queue):
    start_time = time.perf_counter()
    try:
        path, length = algo_func(points)
        duration = time.perf_counter() - start_time
        queue.put({
            "algo": algo_name,
            "path": path,
            "length": length,
            "time": duration
        })
    except Exception as e:
        print(f"Error running {algo_name}: {e}")
# Wrappers to handle distance matrix calculation and algorithm chaining
def wrapper_ppp(points):
    D = pvc_lib.calculer_matrice_distances(points)
    return pvc_lib.ppp(D)

def wrapper_optppp(points):
    D = pvc_lib.calculer_matrice_distances(points)
    return pvc_lib.optppp(D)

def wrapper_prim_mst(points):
    D = pvc_lib.calculer_matrice_distances(points)
    return pvc_lib.optPrim(D)

def wrapper_opt_opt_prim(points):
    D = pvc_lib.calculer_matrice_distances(points)
    return pvc_lib.optOptPrim(D)

# This allows easy addition/modification of algorithms
ALGORITHMS = [
    {
        "id": "ppp",
        "name": "Point le Plus Proche (PPP)",
        "func": wrapper_ppp
    },
    {
        "id": "optppp",
        "name": "PPP Optimisé (OptPPP)",
        "func": wrapper_optppp
    },
    {
        "id": "optprim",
        "name": "Parcour préfix ACM de Prim Optimisé (OptPrim)",
        "func": wrapper_prim_mst
    },
    {
        "id": "optoptprim",
        "name": "OptPrim + Décroisé (OptOptPrim)",
        "func": wrapper_opt_opt_prim
    }
]

@app.route('/')
def index():
    max_points = os.environ.get('MAX_RANDOM_POINTS')
    points = get_points()
    return render_template('index.html', points=points, max_points=max_points)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        # Use tempfile to save the uploaded file temporarily
        fd, path = tempfile.mkstemp()
        os.close(fd)  # Close the file descriptor, we only need the path
        try:
            file.save(path)
            # Use the existing function from pvc.py
            points = pvc_lib.lire_points_fichier(path)
            set_points(points)
        finally:
            # Clean up the temporary file
            if os.path.exists(path):
                os.remove(path)
    return redirect(url_for('index'))

@app.route('/add_point', methods=['POST'])
def add_point():
    try:
        x = float(request.form['x'])
        y = float(request.form['y'])
        points = get_points()
        points.append((x, y))
        set_points(points)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/generate', methods=['POST'])
def generate():
    try:
        n = int(request.form['n'])
        max_points = os.environ.get('MAX_RANDOM_POINTS')
        if max_points:
            max_points = int(max_points)
            if n > max_points:
                n = max_points
        
        points = pvc_lib.generer_points(n)
        set_points(points)
    except ValueError:
        pass
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear():
    set_points([])
    return redirect(url_for('index'))

@app.route('/solve')
def solve_page():
    points = get_points()
    return render_template('solve.html', points=points, algos=ALGORITHMS)

@app.route('/run_solve', methods=['POST'])
def run_solve():
    global CURRENT_PROCESSES
    data = request.json
    selected_ids = data.get('algos', [])
    
    # Get session-specific points and session ID
    points = get_points()
    sid = get_session_id()
    
    queue = multiprocessing.Queue()
    CURRENT_PROCESSES[sid] = []
    
    for algo_id in selected_ids:
        algo_conf = next((a for a in ALGORITHMS if a['id'] == algo_id), None)
        if algo_conf:
            p = multiprocessing.Process(
                target=run_algo_process, 
                args=(algo_conf['name'], algo_conf['func'], points, queue)
            )
            CURRENT_PROCESSES[sid].append(p)
            p.start()
    
    # Handle timeout
    timeout_env = os.environ.get('GLOBAL_TIMEOUT')
    timeout = int(timeout_env) if timeout_env else None
    
    start_wait = time.time()
    
    for p in CURRENT_PROCESSES[sid]:
        if timeout:
            elapsed = time.time() - start_wait
            remaining = timeout - elapsed
            if remaining < 0:
                remaining = 0
            p.join(remaining)
        else:
            p.join()
            
    # Terminate any still running (due to timeout)
    for p in CURRENT_PROCESSES[sid]:
        if p.is_alive():
            p.terminate()
            
    CURRENT_PROCESSES[sid] = []
    
    results = []
    while not queue.empty():
        results.append(queue.get())
        
    return jsonify({"results": results})

@app.route('/stop_solve', methods=['POST'])
def stop_solve():
    sid = get_session_id()
    if sid in CURRENT_PROCESSES:
        for p in CURRENT_PROCESSES[sid]:
            if p.is_alive():
                p.terminate()
        CURRENT_PROCESSES[sid] = []
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
