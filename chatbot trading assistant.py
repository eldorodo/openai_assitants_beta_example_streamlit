#https://medium.com/generative-ai/building-a-streamlit-q-a-app-using-openais-assistant-api-8193f718e7ed
#https://platform.openai.com/docs/assistants/overview
#https://github.com/openai/openai-cookbook/blob/main/examples/Assistants_API_overview_python.ipynb
#https://cookbook.openai.com/examples/assistants_api_overview_python
#https://www.youtube.com/watch?v=vQhEiR2bNY8&t=187s

import streamlit as st
import openai
from streamlit_chat import message
from openai import OpenAI
import json
import os
import requests
import time


def get_alpha_vantage_ohlcv(symbol):
    """
    Get OLHC (Open, Low, High, Close) information for a given symbol from Alpha Vantage.

    Parameters:
    - symbol: The stock or cryptocurrency symbol (e.g., 'AAPL', 'MSFT', 'BTC', etc.).
    - interval: The time interval for the data (default is '1min').
    - api_key: Your Alpha Vantage API key.

    Returns:
    - ohlcv_data: List of dictionaries containing OLHC information.
    """

    base_url = 'https://www.alphavantage.co/query'
    function = 'TIME_SERIES_INTRADAY'
    with open("Alpha_vantage_key.txt", 'r') as file:
          api_key = file.read().strip()
    
    # Construct the API request URL
    params = {
        'function': function,
        'symbol': symbol,
        'interval': '1min',
        'apikey': api_key,
    }

    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        data = response.json()

        # Check if the request was successful
        if 'Time Series (1min)' in data:
            # Extract OLHC data from the response
            ohlcv_data = [
                {
                    'timestamp': timestamp,
                    'open': float(data['Time Series (1min)'][timestamp]['1. open']),
                    'high': float(data['Time Series (1min)'][timestamp]['2. high']),
                    'low': float(data['Time Series (1min)'][timestamp]['3. low']),
                    'close': float(data['Time Series (1min)'][timestamp]['4. close']),
                }
                for timestamp in data['Time Series (1min)']
            ]
            o = ""
            for key, val in ohlcv_data[0].items():
                 o += str(key) + " " + str(val)
                 o += "\n"
            return o
        else:
            print(f"Error: {data['Error Message']}")
            return None

    except requests.RequestException as e:
        print(f"Error making Alpha Vantage API request: {e}")
        return None

tools =[{
    "type": "function",
    "function": {
        "name": "get_alpha_vantage_ohlcv",
        "description": "Get Open, Low, High, Close (OLHC) information for a given symbol from Alpha Vantage.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "The stock or cryptocurrency symbol (e.g., 'AAPL', 'MSFT', 'BTC', etc.)",
                },
            },
            "required": ["symbol"],
        },
    },
},
{"type": "code_interpreter"},
{"type": "retrieval"}
]

with open("Openai_key2.txt", 'r') as file:
    secret_key = file.read().strip()
client = OpenAI(api_key=secret_key)

openai.api_key = secret_key


# Upload files with an "assistants" purpose
file1 = client.files.create(
  file=open("Nagarro Annual Report 2022.pdf", "rb"),
  purpose='assistants'
)
file2 = client.files.create(
  file=open("Hariram_Subramanian Gopal_Resume.pdf", "rb"),
  purpose='assistants'
)

assitant_id_path = 'assitant_id.txt'
assistant_id = ""

# Check if the file exists
if os.path.exists(assitant_id_path):
    # If the file exists, read the ID from the file
    with open(assitant_id_path, 'r') as file:
        assistant_id = file.read().strip()
else:
    # If the file doesn't exist, generate a new ID and save it to the file
    assistant = client.beta.assistants.create(
  	instructions=
      '''

	You are a highly intelligent assistant specializing in finance and business. Your capabilities include code interpretation and function calling, particularly for retrieving real-time stock prices for companies on an intra-day basis.

	Additionally, you have access to knowledge retrieval from one annual report of Nagarro.

	When engaging in conversations, tailor your responses to meet the chat requirements. Provide insightful answers to user quejupyterries related to finance, business, and stock market activities. Use your access to code interpretation to assist users with programming-related tasks or inquiries.

	Always maintain a professional and informative tone, leveraging your expertise in the financial domain to deliver valuable insights to the users ''',
  	
	model="gpt-4-1106-preview",
  	tools=tools,
    file_ids=[file1.id, file2.id]
	)
    assistant_id = assistant.id
    with open(assitant_id_path, 'w') as file:
      file.write(assistant.id)
      
thread_id_path = 'thread_id.txt'
thread_id = ""

# Check if the file exists
if os.path.exists(thread_id_path):
    # If the file exists, read the ID from the file
    with open(thread_id_path, 'r') as file:
        thread_id = file.read().strip()
else:
      thread = client.beta.threads.create()
      thread_id = thread.id
      with open(thread_id_path, 'w') as file:
      	file.write(thread_id)

def submit_message(assistant_id, user_message):
    client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

#def a_new_run(user_input):
    #thread = client.beta.threads.create()
    #run = submit_message(assistant_id, thread_id, user_input)
    #return run

# Waiting in a loop
def wait_on_run(run):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run
         

st.title("Assistant GPT - Knowledge retrival, Function calling and Code Interpreter")

#st.header("What are Assistant API?")

#st.image("What are Assitant API.png", caption="Assistant API components", use_column_width=True)

st.markdown(
    """
    **OpenAI Assistants API Overview:**

    1. **Assistants:** Purpose-built AI with customizable instructions for specific actions.

    2. **Tools:** Access OpenAI-hosted tools or build custom ones using Function calling.

    3. **Threads:** Conversation sessions storing Messages, simplifying AI application development.

    4. **Messages:** Role-based content in threads, supporting knowledge retrieval.

    **How Assistants Work (Beta):**

    - Designed for versatile AI assistant development.
    - Beta with ongoing functionality additions.
    - Customizable personality and capabilities.
    - Access multiple tools simultaneously.
    - Persistent Threads for efficient message history management.
    - Ability to create and access files in various formats.

    **Object Architecture:**

    - Assistant: AI using OpenAI models and tools.
    - Thread: Conversation session storing messages.
    - Message: Role-based content, including text, images, and files.
    - Run: Assistant invocation on a Thread, performing tasks.
    - Run Step: Detailed steps taken during a Run for introspection.

    **Creating Assistants:**

    - Use OpenAI's latest models for optimal results.
    - Specify model and customize with instructions, tools, and file_ids parameters.
    - Instructions guide personality and goals.
    - Tools parameter provides access to up to 128 tools.
    - File_ids parameter grants tools access to files.

    """
)

st.image("Assitant_api.png", caption="Assistant API Overview", use_column_width=True)

st.header("Live assitant Chat bot")

st.markdown(
     """

     **OpenAI Assistants API Overview:**
    You are a highly intelligent assistant specializing in finance and business. Your capabilities include code interpretation and function calling, particularly for retrieving real-time stock prices for companies on an intra-day basis.

    Additionally, you have access to knowledge retrieval from one annual report of Nagarro.

    When engaging in conversations, tailor your responses to meet the chat requirements. Provide insightful answers to user quejupyterries related to finance, business, and stock market activities. Use your access to code interpretation to assist users with programming-related tasks or inquiries.

    Always maintain a professional and informative tone, leveraging your expertise in the financial domain to deliver 

"""

)

st.image("Nagarro annual report.png", caption="Nagarro annual report 2022", use_column_width=True)

st.image("Alpha vantage OHLC data.png", caption="Alpha vantage OHLC data", use_column_width=True)


if 'user_input' not in st.session_state:
	st.session_state['user_input'] = []

if 'openai_response' not in st.session_state:
	st.session_state['openai_response'] = []

def get_text():
	input_text = st.text_input("Chat here", key="input")
	return input_text

user_input = get_text()


if user_input:
     print(user_input)
     run = submit_message(assistant_id, user_input)
     run = wait_on_run(run)
     if (run.status == 'requires_action'):
        # Extract single tool call
        tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
        name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        output = get_alpha_vantage_ohlcv(arguments["symbol"])
        run = client.beta.threads.runs.submit_tool_outputs(
             thread_id=thread_id,
                run_id=run.id,
                    tool_outputs=[
        	{
            "tool_call_id": tool_call.id,
            "output": json.dumps(output),
        	}
    		],
			)
        run = wait_on_run(run)
     response = client.beta.threads.messages.list(thread_id=thread_id, order="asc")
     output = response.data[-1].content[0].text.value
     
	 # Store the output
     st.session_state.openai_response.append(user_input)
     st.session_state.user_input.append(output)

message_history = st.empty()

if st.session_state['user_input']:
	for i in range(len(st.session_state['user_input']) - 1, -1, -1):
		# This function displays user input
		message(st.session_state["user_input"][i], 
				key=str(i),avatar_style="icons")
		# This function displays OpenAI response
		message(st.session_state['openai_response'][i], 
				avatar_style="miniavs",is_user=True,
				key=str(i) + 'data_by_user')
