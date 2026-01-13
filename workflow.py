from agents import WebScraper, Summarizer, Mailer

AGENTS = {
    "WebScraper": WebScraper,
    "Summarizer": Summarizer,
    "Mailer": Mailer
}

def run_workflow(steps):
    """
    Run workflow from YAML steps
    
    Expected format:
    - agent: WebScraper
      task: "Fetch AI news"
    """
    data = None
    logs = []

    for i, step in enumerate(steps):
        agent_name = step.get("agent", "")
        task = step.get("task", "")
        
        if agent_name in AGENTS:
            agent = AGENTS[agent_name]()
            
            if data:
                data = agent.run(task, data)
            else:
                data = agent.run(task)
            
            logs.append(f"✅ Step {i+1}: {agent_name} → {task}")
        else:
            logs.append(f"❌ Step {i+1}: Unknown agent '{agent_name}'")

    return data, logs