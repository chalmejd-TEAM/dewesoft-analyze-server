from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

# Define an endpoint to handle the Python file requests
@app.route('/run_python', methods=['POST'])
def run_python():
    try:
        # Extract the 'script' and 'data' fields from the request JSON
        data = request.get_json()
        script_name = data.get("script")
        script_data = data.get("data")

        if script_name and script_data:
            # Pass the script name and data to the Python file
            result = execute_python_script(script_name, script_data)
            return jsonify({"status": "success", "result": result}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid input"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def execute_python_script(script_name, script_data):
    try:
        # Construct the command to run the Python script with arguments (you can adapt it)
        command = f"python {script_name}.py"
        result = subprocess.run(command, input=json.dumps(script_data), text=True, capture_output=True)

        if result.returncode == 0:
            return json.loads(result.stdout)  # Return the JSON output of the script
        else:
            return {"error": result.stderr}

    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)  # The server will be accessible locally
