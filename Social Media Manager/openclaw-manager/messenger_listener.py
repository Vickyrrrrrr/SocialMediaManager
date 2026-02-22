import os
import json
import time
import requests
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

import sys

# Reconfigure stdout to handle UTF-8 characters (like 'mu' μ) on Windows terminals
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def detect_intent(text):
    """Uses LLM to map natural language to internal commands."""
    prompt = f"""
    Analyze the user's message and map it to one of these intents:
    1. CHECK: User wants to see the latest chip metrics, analyze the design, or status of a specific design (e.g., "check design", "how is my chip").
    2. CONFIRM: User wants to post the pending draft to X (e.g., "post it", "looks good confirm").
    3. LIST: User wants to know what designs are in the folder or an inventory of projects (e.g., "what designs do I have?", "list my projects", "show folder info").
    4. HELP: User asks for help or available commands.
    5. CHAT: General greeting or question.
    
    User message: "{text}"
    
    Respond ONLY with the intent name: CHECK, CONFIRM, LIST, HELP, or CHAT.
    """
    res = call_llm(prompt)
    if isinstance(res, dict) and "content" in res:
        intent = res["content"].strip().upper()
        if "CHECK" in intent: return "/check_latest"
        if "CONFIRM" in intent: return "/confirm"
        if "LIST" in intent: return "/list_designs"
        if "HELP" in intent: return "/help"
    return "/chat"

def trigger_list_designs():
    config_path = os.path.join(BASE_DIR, 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except:
        return "Error: Could not load config.json"
        
    base_designs_path = config.get("agentic_reports_path")
    if not base_designs_path:
        return "Error: agentic_reports_path not configured."

    report = "📁 **AgentIC Design Folder Status**\n\n"
    
    try:
        # Check if the folder exists
        if not os.path.exists(base_designs_path):
            return f"Error: Designs path not found: {base_designs_path}"
            
        designs = [d for d in os.listdir(base_designs_path) if os.path.isdir(os.path.join(base_designs_path, d))]
        
        if not designs:
            return "No designs found in the configured folder."
            
        for d in designs:
            runs_path = os.path.join(base_designs_path, d, 'runs')
            run_count = 0
            gds_ready = False
            
            if os.path.exists(runs_path):
                runs = [r for r in os.listdir(runs_path) if os.path.isdir(os.path.join(runs_path, r))]
                run_count = len(runs)
                
                # Check for GDS in any run (non-recursive for speed)
                for r in runs:
                    results_path = os.path.join(runs_path, r, 'results', 'signoff')
                    if os.path.exists(results_path):
                        if any(f.endswith('.gds') for f in os.listdir(results_path)):
                            gds_ready = True
                            break
            
            status_icon = "🟢" if gds_ready else "🟠"
            report += f"{status_icon} **{d}**: {run_count} runs found.\n"
            
        report += "\n💡 *Use /check_latest to analyze the newest completed run.*"
        return report
        
    except Exception as e:
        return f"Error listing designs: {e}"


# Load configurations
load_dotenv(os.path.join(BASE_DIR, ".env"))

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=BASE_DIR)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def call_llm(prompt, model="meta/llama-3.1-70b-instruct", json_mode=False):
    try:
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            return {"error": "NVIDIA_API_KEY not found in .env"}
            
        client = OpenAI(
          base_url = "https://integrate.api.nvidia.com/v1",
          api_key = api_key
        )

        # Build request body
        request_params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2 if json_mode else 1, # Lower temp for JSON reliability
            "top_p": 1,
            "max_tokens": 16384,
            "stream": True,
            "timeout": 30
        }
        
        # Add response format for JSON mode if supported by the model/endpoint
        if json_mode:
            request_params["response_format"] = {"type": "json_object"}
        
        # Only add thinking param for thinking models
        if "glm5" in model:
            request_params["extra_body"] = {"chat_template_kwargs": {"enable_thinking": True, "clear_thinking": False}}

        completion = client.chat.completions.create(**request_params)


        full_content = ""
        full_reasoning = ""
        
        for chunk in completion:
            if not getattr(chunk, "choices", None):
                continue
            if len(chunk.choices) == 0 or getattr(chunk.choices[0], "delta", None) is None:
                continue
            delta = chunk.choices[0].delta
            
            # Capture reasoning if available
            reasoning = getattr(delta, "reasoning_content", None)
            if reasoning:
                full_reasoning += reasoning
                
            # Capture final content
            if getattr(delta, "content", None) is not None:
                full_content += delta.content
        
        return {
            "content": full_content.strip(),
            "reasoning": full_reasoning.strip()
        }
    except Exception as e:
        return {"error": f"Error calling NVIDIA LLM: {e}"}



def trigger_check_flow():
    print("Triggering AgentIC Check Flow...")
    
    config_path = os.path.join(BASE_DIR, 'config.json')
    pending_path = os.path.join(BASE_DIR, 'data/public_metrics/pending_post.txt')
    
    # 1. Extract Metrics
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        return f"Error loading config.json: {e}"
    
    designs_path = config.get("agentic_reports_path")
    if not designs_path:
        return "Error: agentic_reports_path not configured in config.json"
        
    model = config.get("default_model", "z-ai/glm5")
    print(f"Using model: {model}")
    
    extract_output = run_command(f"python extract_metrics.py \"{designs_path}\"")
    print(f"Extraction Output: {extract_output}")
    
    if "No completed GDS runs found" in extract_output:
        return "No completed GDS runs found in the designs folder."

    # 2. Prepare Prompt from SKILL.md and metrics
    try:
        skill_path = os.path.join(BASE_DIR, 'skills/agentic_pr/SKILL.md')
        metrics_path = os.path.join(BASE_DIR, 'data/public_metrics/latest.json')
        
        print(f"Loading metrics from: {metrics_path}")
        with open(skill_path, 'r', encoding='utf-8') as f:
            skill_content = f.read()

        with open(metrics_path, 'r', encoding='utf-8') as f:
            latest_metrics = f.read()
        data = json.loads(latest_metrics)
        
        prompt = f"""
        Analyze these hardware benchmarks and respond in STRICT JSON format.
        
        Benchmarks:
        {latest_metrics}
        
        Industry Standards & Commercial Correlation:
        - Refer to Sky130 and Cadence/Synopsys targets.
        
        Output Schema:
        {{
            "recommendation": "string",
            "readiness_score": "string (e.g. 85%)",
            "correlation": "string (comparison vs commercial tools)",
            "comparison": "string (comparison vs standards)",
            "post_text": "string (X post max 280 chars)"
        }}
        """
        
        print(f"Analyzing with {model}...")
        llm_data = call_llm(prompt, model=model, json_mode=True)
        
        if "error" in llm_data:
            return llm_data["error"]

        # Parse JSON response
        try:
            content = llm_data.get("content", "{}")
            if isinstance(content, str):
                res = json.loads(content)
            else:
                res = content
        except:
            return "AI returned invalid JSON. Retrying..."

        recommendation = res.get("recommendation", "N/A")
        readiness_score = res.get("readiness_score", "0%")
        correlation = res.get("correlation", "N/A")
        comparison_summary = res.get("comparison", "N/A")
        post_text = res.get("post_text", "")
        
        reasoning = llm_data.get("reasoning", "")
        
        # Save to Database
        from database_manager import save_pending_post
        save_pending_post(data.get('design_name', 'Unknown'), post_text, readiness_score)
            
        report = f"🛡️ **Physical Readiness Report: {data.get('design_name', 'Unknown')}**\n\n"
        report += f"✅ **Readiness Score:** `{readiness_score}`\n"
        report += f"🏗️ **Commercial Correlation:** {correlation}\n\n"
        
        report += f"📊 **Benchmark Summary:**\n"
        report += f"- Area: {data.get('area_mm2')} mm²\n"
        report += f"- Power: {data.get('power_mw')} mW\n"
        report += f"- Timing: {data.get('slack_ns')} ns slack\n\n"
        
        if reasoning:
            report += f"🧠 **AI Thinking:**\n_{reasoning[:300]}..._\n\n"
            
        report += f"🏁 **Vs. Industry Standard:**\n{comparison_summary[:300]}\n\n"
        report += f"🎯 **Final Verdict:** {recommendation}\n\n"
        report += f"📝 **Draft Post for X:**\n`{post_text}`\n\n"
        report += "🚀 Reply with 'Confirm' to publish."
        
        return report

        
    except Exception as e:
        return f"Error in check logic: {e}"

def trigger_confirm_post():
    from database_manager import get_latest_pending_post, mark_post_published
    
    pending = get_latest_pending_post()
    if not pending:
        return "Nothing to confirm. Please run a design check first."
        
    post_text, design_name = pending
    
    # Post to X
    post_script = os.path.join(BASE_DIR, 'skills/agentic_pr/post_to_x.py')
    post_output = subprocess.check_output(f'python "{post_script}" "{post_text}"', shell=True).decode()
    
    # Mark as published
    mark_post_published(post_text)
    
    return f"🚀 **Successfully posted to X!**\n\n{post_output}"

# --- Tool Registry for the Agentic Brain ---
TOOLS = {
    "list_designs": {
        "func": trigger_list_designs,
        "desc": "List all chip designs in the AgentIC folder and their status."
    },
    "check_metrics": {
        "func": trigger_check_flow,
        "desc": "Analyze the latest hardware metrics and compare with industry standards."
    },
    "confirm_post": {
        "func": trigger_confirm_post,
        "desc": "Post the generated draft to X (Twitter) after user approval."
    }
}

def run_agentic_loop(user_input):
    """The 'Brain' of the bot. Decides which tools to use to solve a request."""
    tools_desc = "\n".join([f"- {name}: {info['desc']}" for name, info in TOOLS.items()])
    
    prompt = f"""
    You are the AgentIC PR Manager brain. You help the user manage their silicon designs.
    
    Available Tools:
    {tools_desc}
    - CHAT: Just talk to the user.
    
    User Request: "{user_input}"
    
    Your Task:
    1. Read the request.
    2. If it requires a tool, output 'CALL: <tool_name>'.
    3. If it is just a question or greeting, output 'REPLY: <your response>'.
    
    Constraint: Respond ONLY with 'CALL: name' or 'REPLY: message'.
    """
    
    # Use LLM to decide
    res = call_llm(prompt)
    content = res.get("content", "").strip()
    
    if content.startswith("CALL:"):
        tool_name = content.replace("CALL:", "").strip()
        if tool_name in TOOLS:
            print(f"Agentic Brain decided to call: {tool_name}")
            return TOOLS[tool_name]["func"]()
        else:
            return f"I tried to use a tool called {tool_name}, but I don't know how to use it yet!"
            
    if content.startswith("REPLY:"):
        return content.replace("REPLY:", "").strip()
        
    # Fallback to general chat
    chat_res = call_llm(f"You are a professional hardware engineering agent. Reply to: {user_input}")
    return chat_res.get("content", "I'm thinking... can you repeat that?")

# --- Flask Webhook Server ---
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/telegram', methods=['POST'])
def telegram_webhook():
    update = request.get_json()
    if not update:
        return jsonify({"status": "error", "message": "No data received"}), 400

    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    user_id = str(message.get("from", {}).get("id"))
    text = message.get("text", "")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    auth_user = os.getenv("TELEGRAM_AUTHORIZED_USER_ID")
    
    if auth_user and user_id != auth_user:
        print(f"Unauthorized attempt from user ID: {user_id}")
        return jsonify({"status": "unauthorized"}), 200

    print(f"Received message: {text}")

    # Agentic Brain Integration
    if text and not text.startswith("/"):
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": "🧠 *Thinking...*", "parse_mode": "Markdown"})
        
        response_text = run_agentic_loop(text)
        
        try:
            r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                              json={"chat_id": chat_id, "text": response_text, "parse_mode": "Markdown"})
            if not r.json().get("ok"):
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                              json={"chat_id": chat_id, "text": response_text})
        except Exception as e:
            print(f"Error sending agent response: {e}")
        return jsonify({"status": "ok"}), 200

    # Command Handling
    response_text = ""
    if text == "/start":
        response_text = "👋 Welcome to the AgentIC Autonomous PR Agent!\n\nI have my own brain now. Just tell me what you need in plain English!"
    elif text == "/help":
        response_text = "📖 **I am an Autonomous Agent**\n\nI use tools to help you:\n- **List Designs**: Scans your WSL folder.\n- **Check Metrics**: Analyzes benchmarks.\n- **Confirm Post**: Publishes to X."
    elif text == "/check_latest":
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": "🔍 **Scanning OpenLane designs...**", "parse_mode": "Markdown"})
        response_text = trigger_check_flow()
    elif text == "/confirm":
        response_text = trigger_confirm_post()
    elif text == "/list_designs":
        response_text = trigger_list_designs()

    if response_text:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": response_text, "parse_mode": "Markdown"})

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    from database_manager import init_db
    init_db()
    
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Enterprise Bot Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port)
