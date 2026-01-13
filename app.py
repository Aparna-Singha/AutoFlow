import yaml
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from workflow import run_workflow

app = Flask(__name__)
CORS(app)

# ===== Home Page (UI) =====
@app.route("/")
def home():
    return render_template("index.html")

# ===== Run from File Upload (Original) =====
@app.route("/run-file", methods=["POST"])
def run_file():
    try:
        file = request.files["file"]
        data = yaml.safe_load(file)
        output, logs = run_workflow(data["workflow"])
        return jsonify({
            "success": True,
            "output": output, 
            "logs": logs
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

# ===== Run from UI =====
@app.route("/run", methods=["POST"])
def run():
    try:
        data = request.json
        yaml_content = data.get('yaml', '')
        
        # Parse YAML string
        parsed = yaml.safe_load(yaml_content)
        
        # Get workflow steps
        workflow_data = parsed.get("workflow", [])
        
        # Run workflow
        output, logs = run_workflow(workflow_data)
        
        # Format output for UI
        formatted_output = format_output_for_ui(output, logs)
        
        return jsonify({
            "success": True,
            "result": formatted_output,
            "output": output,
            "logs": logs
        })
        
    except yaml.YAMLError as e:
        return jsonify({
            "success": False,
            "error": f"Invalid YAML format: {str(e)}"
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

def format_output_for_ui(output, logs):
    """Format output nicely for UI display"""
    result_parts = []
    
    result_parts.append("🚀 Workflow Execution")
    result_parts.append("=" * 40)
    
    # Add logs
    result_parts.append("\n📋 Steps Completed:")
    for log in logs:
        result_parts.append(f"   {log}")
    
    # Add output
    result_parts.append("\n" + "-" * 40)
    result_parts.append("📄 Final Output:")
    result_parts.append("-" * 40 + "\n")
    result_parts.append(str(output))
    
    result_parts.append("\n" + "=" * 40)
    result_parts.append("✅ Done!")
    
    return "\n".join(result_parts)

if __name__ == "__main__":
    app.run(debug=True, port=5000)