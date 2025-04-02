import gradio as gr

def respond(message, history):
    return f"Echo: {message}"

demo = gr.ChatInterface(
    respond,
    title="Test Bot",
    description="Simple echo bot"
)

if __name__ == "__main__":
    demo.launch() 