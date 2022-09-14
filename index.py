#!/usr/bin/env python
# encoding: utf-8
import os
import json
from flask import Flask, request, jsonify, abort, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'files'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

@app.route('/', methods=['GET'])
def get_and_return():
    return jsonify({"check":"value"})

@app.route('/user', methods=['GET'])
def query_records():
    name = request.args.get('name')
    print(name)
    with open('data.txt', 'r') as f:
        try:
            contents = f.read()
            print(contents)
            records = json.loads(contents)
        except json.decoder.JSONDecodeError:
            return jsonify({'status': 400, 'error': 'Data not loaded properly'}) 

        for record in records:
            if record['username'] == name:
                return jsonify(record), 200
    return jsonify({status: 400, 'error': 'user does not exist'}), 400

@app.route('/register-user', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    with open('data.txt', 'r') as f:
        data = f.read()
    if not data:
        records = [record]
    else:
        records = json.loads(data)
        for rec in records: 
            if record['username'] == rec['username']:
                return jsonify({"error": "user already exists"}),400
        records.append(record)
        print(records)
    with open('data.txt', 'w') as f:
        f.write(json.dumps(records, indent=2))
    return jsonify(record), 200

@app.route('/update-profile', methods=['PUT'])
def update_record():
    request_data = json.loads(request.data)
    new_records = []
    with open('data.txt', 'r') as f:
        data = f.read()
    if not data:
        return jsonify({"error": "user does not exist"}),400
    else: 
        records = json.loads(data)
    for record in records:
        if record['username'] == request_data['username']:
            record['fname'] = request_data['fname']
            record['lname'] = request_data['lname']
            record['email'] = request_data['email']
        else: 
            return jsonify({"error": "user does not exist"}),400
        new_records.append(record)
        
    with open('data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(request_data), 200
    
@app.route('/', methods=['DELETE'])
def delte_record():
    record = json.loads(request.data)
    new_records = []
    with open('data.txt', 'r') as f:
        data = f.read()
        records = json.loads(data)
        for r in records:
            if r['name'] == record['name']:
                continue
            new_records.append(r)
    with open('data.txt', 'w') as f:
        f.write(json.dumps(new_records, indent=2))
    return jsonify(record)

@app.route('/uploader/<string:username>', methods = ['GET', 'POST'])
def upload_file(username):
   if request.method == 'POST':
        # check if the post request has the file part
        print(username)

        if 'file' not in request.files:
            return ({"error": "No file in request"}), 400
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return ({"error": "No filename"}), 400
        if file:
            new_records = []
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            with open('data.txt', 'r') as f:
                data = f.read()
                records = json.loads(data)
            for record in records:
                if record['username'] == username:
                    record['filename'] = filename
                new_records.append(record)
            with open('data.txt', 'w') as f:
                f.write(json.dumps(new_records, indent=2))
            return ({"message": "upload success"}), 200

@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, path=filename)

app.run(debug=True)


