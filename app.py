from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the folder if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/run_python", methods=["POST"])
def run_python():
    try:
        # Check if the file is part of the request
        if "file" not in request.files:
            return jsonify({"status": "error", "message": "No file uploaded"}), 400

        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return jsonify({"status": "error", "message": "No file selected"}), 400

        # Save the file to the upload directory
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
        uploaded_file.save(file_path)

        # Execute the Python script using the uploaded file
        result = execute_python_script("loadChannelList", file_path)
        return jsonify({"status": "success", "result": result}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def execute_python_script(script_name, file_path):
    try:
        # Construct the command to run the Python script with the file as an argument
        command = f"python {script_name}.py {file_path}"
        result = subprocess.run(command, text=True, capture_output=True)

        if result.returncode == 0:
            return {"output": result.stdout}  # Return the script output
        else:
            return {"error": result.stderr}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # The server will be accessible locally
