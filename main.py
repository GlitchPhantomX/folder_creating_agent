import os
import platform
from dotenv import load_dotenv
from agents import Runner, Agent, OpenAIChatCompletionsModel, AsyncOpenAI
from agents.run import RunConfig
import chainlit as cl
from typing import cast
from agents.tool import function_tool

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

@function_tool
def create_folder(folder_name: str) -> str:
    """Creates a folder in the current working directory"""
    try:
        current_dir = os.getcwd()
        folder_path = os.path.join(current_dir, folder_name)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            if os.path.isdir(folder_path):
                return f"✅ Successfully created folder at:\n{folder_path}"
            return f"❌ Error: Folder creation failed (permissions issue?)"
        return f"⚠️ Folder already exists at:\n{folder_path}"
    except Exception as e:
        return f"❌ Error creating folder: {str(e)}"

@function_tool
def create_file(file_path: str, content: str = "") -> str:
    """Creates a file at specified path relative to current directory"""
    try:
        current_dir = os.getcwd()
        full_path = os.path.join(current_dir, file_path)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(content)
        
        if os.path.exists(full_path):
            return f"✅ Successfully created file at:\n{full_path}"
        return f"❌ Error: File creation failed (permissions issue?)"
    except Exception as e:
        return f"❌ Error creating file: {str(e)}"

@function_tool
def generate_code(instruction: str) -> str:
    """Generates code based on user instruction"""
    return f"CODE_REQUEST:{instruction}"

@function_tool
def list_files(folder_path: str = "") -> str:
    """Lists files in a directory (default: current directory)"""
    try:
        base_path = os.getcwd()
        target_path = os.path.join(base_path, folder_path) if folder_path else base_path
        
        if not os.path.exists(target_path):
            return f"❌ Error: Path not found - {target_path}"
            
        files = []
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            files.append(f"{'📁' if os.path.isdir(item_path) else '📄'} {item}")
        
        return "Files in directory:\n" + "\n".join(files) if files else "Directory is empty"
    except Exception as e:
        return f"❌ Error listing files: {str(e)}"

@cl.on_chat_start
async def start():
    external_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=external_client
    )
    config = RunConfig(
        model=model,
        model_provider=external_client,
        tracing_disabled=True
    )
    
    cl.user_session.set("chat_history", [])
    cl.user_session.set("config", config)
    
    agent = Agent(
        name="FileCoderPro",
        instructions="""You are an advanced file management assistant that can:
1. Create and manage folders/files in the current directory
2. Generate code for applications
3. List directory contents
Always verify operations and provide detailed status reports. and use emojis for better user experience.""",
        model=model,
        tools=[create_folder, create_file, generate_code, list_files]
    )
    
    cl.user_session.set("agent", agent)
    await cl.Message(content=f"🚀 Welcome to FileCoder Pro! Working in directory: {os.getcwd()}\nI can create files/folders here, generate code, and manage your files. How can I help?").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="🔍 Processing your request...")
    await msg.send()

    agent: Agent = cast(Agent, cl.user_session.get("agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    
    history = cl.user_session.get("chat_history") or []
    history.append({"role": "user", "content": message.content})

    try:
        result = Runner.run_sync(agent, history, run_config=config)
        response_content = result.final_output
        
        if response_content.startswith("CODE_REQUEST:"):
            code_request = response_content.split(":", 1)[1].strip()
            code_response = await agent.model.run([{"role": "user", "content": f"Generate complete, production-ready code for: {code_request}. Include all necessary files and instructions."}])
            generated_code = code_response.choices[0].message.content
            
            response_content = f"""💻 Code Generated for '{code_request}':
            
{generated_code}

Reply with 'save this as filename.js' to store it."""
        
        if "❌ Error" in response_content:
            msg.content = f"❌ {response_content}"
        elif "✅" in response_content:
            msg.content = f"✅ {response_content}"
        else:
            msg.content = response_content
            
        await msg.update()
        history.append({"role": "assistant", "content": response_content})
        cl.user_session.set("chat_history", history)
        
    except Exception as e:
        msg.content = f"🔥 Critical Error: {str(e)}\n\nPlease check the console for details."
        await msg.update()
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    current_dir = os.getcwd()
    print(f"Debug: Current working directory is {current_dir}")
    print(f"Debug: Directory contents: {os.listdir(current_dir)}")