from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat")
st.title("Chatbot")

if "setup_complete" not in st.session_state:
    st.session_state["setup_complete"] = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "messages" not in st.session_state:
        st.session_state.messages = []
    
def complete_setup():
    if st.session_state["name"]:
        st.session_state.setup_complete = True
    
if not st.session_state.setup_complete:

    st.subheader('Personal information', divider='rainbow')
    
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "standard" not in st.session_state:
        st.session_state["standard"] = None
    if "subject" not in st.session_state:
        st.session_state["subject"] = None

    st.session_state["name"] = st.text_input(label = "Name", max_chars = 50, value = st.session_state["name"], placeholder = "Enter your name")
    st.session_state["standard"] = st.selectbox(
        "Choose your standard",
        options=["First", "Second", "Third", "Fourth", "Fifth",
            "Sixth", "Seventh", "Eighth", "Ninth", "Tenth",
            "Eleventh", "Twelfth"],
        placeholder="Choose one"
    )
    st.session_state["subject"] = st.selectbox(
        "Choose your subject",
        options=["Mathematics", "English", "History", "Geography", "Science"],
        placeholder="Choose one"
    )

    #st.write(f"**Your Name**: {st.session_state["name"]}")
    #st.write(f"**Your Standard**: {st.session_state["standard"]}")
    #st.write(f"**Your Subject**: {st.session_state["subject"]}")

    if st.button("Start interaction", on_click=complete_setup):
        if st.session_state.setup_complete:
            st.write("Setup complete. Starting interaction with chat bot...")
        else:
            st.write("Enter your name")
if st.session_state.setup_complete:
    st.info(
        """
        Start by introducing yourself.
        """,
        icon = "🧑‍🎓"
    )
    
    client = OpenAI(api_key=st.secrets['OPEN_API_KEY'])

    if "openai_model" not in st.session_state:
        st.session_state.openai_model = 'gpt-4o-mini'
        
    if not st.session_state.messages:
        st.session_state.messages = [{
            "role":"system", 
            "content": (f"You are a subject matter expert of {st.session_state['subject']} "
                        f"for {st.session_state['standard']} standard and answers the questions precisely "
                        f"for the student with name {st.session_state['name']}."
                        f"Respond as bullet points")
            }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    if st.session_state.user_message_count <= 5:
        if prompt := st.chat_input("Your question:", max_chars = 200):
            st.session_state.messages.append({"role":"user", "content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        if st.session_state.user_message_count <= 5:
            with st.chat_message("assistant"):
                streamResp = client.chat.completions.create(
                    model = st.session_state["openai_model"],
                    messages = [
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream = True,
                    max_tokens = 256
                )
                response = st.write_stream(streamResp)
            st.session_state.messages.append({"role":"assistant", "content":response})
            
        st.session_state.user_message_count += 1
    else:
        st.write("User message limit reached max of 5")
        if st.button("Restart interaction", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")