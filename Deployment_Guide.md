# Deployment Guide: Customer Support 24/7 Chatbot

This guide provides instructions for deploying your Streamlit chatbot permanently. Since your app relies on **Ollama** and the **llama3** model, deployment requires an environment that can run both the Python application and the Ollama service.

---

## 🛠 Option 1: Deployment via Docker (Recommended)

Using Docker is the most reliable method for Virtual Private Servers (VPS) such as AWS EC2, DigitalOcean Droplets, or Google Compute Engine.

### Steps:
1.  **Install Docker** on your server.
2.  **Upload the files**: Copy `chatbot_app.py`, `requirements.txt`, and `Dockerfile` to a directory on your server.
3.  **Build the Image**:
    ```bash
    docker build -t customer-support-chatbot .
    ```
4.  **Run the Container**:
    ```bash
    docker run -d -p 8501:8501 customer-support-chatbot
    ```
5.  **Access your app**: Open your browser and navigate to `http://your-server-ip:8501`.

---

## ☁️ Option 2: Streamlit Community Cloud (Free & Easy)

Streamlit Community Cloud is excellent for hosting, but it does not natively support background services like Ollama. To use this option, you must:

1.  **Modify the code**: Update the app to use a hosted LLM API (e.g., OpenAI, Anthropic, or Groq) instead of a local Ollama instance.
2.  **Push your code**: Upload your project to a GitHub repository.
3.  **Deploy**: Connect the repository to [Streamlit Cloud](https://share.streamlit.io/).

---

## 💻 Option 3: Local Permanent Deployment

To keep the chatbot running permanently on your own local machine:

1.  **Install Ollama**: Download from [ollama.com](https://ollama.com).
2.  **Pull the model**: 
    ```bash
    ollama pull llama3
    ```
3.  **Set up a Python Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```
4.  **Run with Nohup**: (Keeps the app running after closing the terminal)
    ```bash
    nohup streamlit run chatbot_app.py &
    ```

---

## ⚠️ Important Considerations

* **Hardware Requirements**: Running `llama3` locally requires significant RAM (minimum 8GB, 16GB+ recommended) and ideally a dedicated GPU for acceptable response times.
* **API Alternatives**: For production environments with high traffic, consider switching from a local Ollama instance to a cloud-based API (e.g., **Groq**). Groq offers high speed and a generous free tier, ensuring better stability and performance for end-users.
