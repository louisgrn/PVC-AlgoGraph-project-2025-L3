from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
import pvc_lib
import threading
import time
import json
import os
import tempfile

app = Flask(__name__)

# Global state
POINTS = []

# Algorithm configuration structure
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
    return render_template('index.html', points=POINTS)

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
    data = request.json
    selected_ids = data.get('algos', [])
    
    results = []
    threads = []
    
    def run_algo(algo_conf):
        start_time = time.time()
        # Call the algorithm function
        # Assuming signature is func(points) -> (path, length)
        # pvc.ppp signature is (points, Q=None, D=None)
        try:
            path, length = algo_conf['func'](POINTS)
            duration = time.time() - start_time
            results.append({
                "algo": algo_conf['name'],
                "path": path,
                "length": length,
                "time": duration
            })
        except Exception as e:
            print(f"Error running {algo_conf['name']}: {e}")

    for algo_id in selected_ids:
        algo_conf = next((a for a in ALGORITHMS if a['id'] == algo_id), None)
        if algo_conf:
            t = threading.Thread(target=run_algo, args=(algo_conf,))
            threads.append(t)
            t.start()
    
    for t in threads:
        t.join()
        
    return jsonify({"results": results})

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
