import gradio as gr

# Simple function that doesn't use any ML
def echo(message):
    return message

# Create an interface
demo = gr.Interface(
    fn=echo,
    inputs="text",
    outputs="text",
    title="Echo Test",
    description="This is a minimal test to see if the app can start"
)

# Launch
if __name__ == "__main__":
    print("Starting minimal app...")
    demo.launch() 