🚩 Kubernetes cluster

⬇️

🚩 Snapshot + Logs Collection (time-series and structured state)
- collecting all the information that LLM needs for analysis and diagnosing
- saving data in file or streaming direcly into LLM

⬇️

🚩 Split into two parallel flows:

1. LLM-based analysis

   - Receives snapshots/logs in windows
   - Tracks trends, compares past vs present
    - Uses prompt templating or attention for focusing on critical info
   - Can trigger deeper actions (alerts, RAG, etc.)

   ***fine tuning, BERT for anomaly detection***
  
2. Static (rule-based) analysis
    - Threshold checks (CPU > 90%, 5 restarts in 1 min, etc.)
    - Error pattern matching (BackOff, CrashLoop, etc.)
    - Optionally: thresholds tuned or suggested by LLM

    ***rolling window stats***

⬇️      

🚩 Hybrid Decision Logic
   - If either system flags an issue:
     - LLM is prompted for explanation and troubleshooting steps
     - Can trigger RAG-based answer on Kubernetes docs or team runbooks
     - Sends alert + possible fix to user (Slack/email/API/etc.)

     ***RAG adjustments and testing, HyDE, SPLADE***
