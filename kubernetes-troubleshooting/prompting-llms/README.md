# Kubernetes Troubleshooting with LLMs

This project implements a system for using Large Language Models (LLMs) to assist with Kubernetes troubleshooting. The system works in multiple stages:

1. **Documentation Retrieval**: The LLM finds relevant Kubernetes documentation excerpts based on error logs and cluster events.
2. **Error Explanation**: Uses the documentation excerpts and error logs to provide a comprehensive explanation and solution.

## Project Structure

- `main_run.py`: Main script for the documentation retrieval stage
- `error_explanation_run.py`: Script for the error explanation stage
- `prompts/`: Contains prompt templates for different stages and approaches
- `results/`: Output directory for all model results
- `data_preprocessing.py`: Handles preprocessing of Kubernetes error data
- `LLM_executor.py`: Interface for different LLM models

## Running the System

### Stage 1: Documentation Retrieval
