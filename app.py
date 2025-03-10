from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(String)
    user_password = Column(String)
    
connection_string = f"mysql+pymysql://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}@sql12.freesqldatabase.com:3306/sql12765026"

st.set_page_config(page_title="Streamlit Chat")
st.title("Chatbot")

engine = create_engine(connection_string)
Session = sessionmaker(bind=engine)

if "setup_complete" not in st.session_state:
    st.session_state["setup_complete"] = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "messages" not in st.session_state:
        st.session_state.messages = []
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False
if "login_success" not in st.session_state:
    st.session_state["login_success"] = True
    
def complete_setup():
    if st.session_state["name"]:
        st.session_state.setup_complete = True
def show_login_form(is_login: bool):
    st.session_state.show_login = is_login

def login(userId, password):
        userIdLower = userId.lower()
        with Session() as session:
            try:
                result = session.query(User).filter(User.user_id == userIdLower).all()
                for user in result:
                    if user.user_password == password:
                        st.session_state.name = user.name
                        st.session_state.login_success = True
                        
                if st.session_state.login_success:
                    st.write("Successfully logged!!")
                else:
                    st.write("Incorrect userId/password!!")
            except Exception as e:
                st.error(f"Error occurred: {e}")
            finally:
                session.close()
            
def register(name, userId, password):
        userIdLower = userId.lower()
        with Session() as session:
            try:
                result = session.query(User).filter(User.user_id == userIdLower).all()
                if len(result) > 0:
                    st.write(f"User Id '{userId}' already registered!!!")
                    show_login_form(True)
                else:
                    user = User(name = name, 
                                user_id = userIdLower,
                                user_password = password
                            )
                    session.add(user)
                    session.commit()
                    st.write('Registered successfully!!!')
                    show_login_form(True)
                    
            except Exception as e:
                st.error(f"Error occurred: {e}")
            finally:
                session.close()

if not st.session_state.login_success and st.session_state.show_login:
    st.title("Login with userId")
    userId = st.text_input(label = "User Id", key = 'userid_login', max_chars = 40, placeholder = "Enter your user id")
    password = st.text_input(label = "Password", key = 'pass_login', type = "password", max_chars = 40, placeholder = "Enter your password")

    st.button("Login", key = 'login', on_click=login, args=(userId, password), disabled=(userId == '' or password == ''))
    st.button("Signup", key='showSignup', on_click=show_login_form, args=(False,))
    
elif not st.session_state.login_success and not st.session_state.show_login:
    st.title("Register")
    name = st.text_input(label = "Name", key = 'name_register', max_chars = 40, placeholder = "Enter your name")
    userId = st.text_input(label = "User Id", key = 'userid_register', max_chars = 40, placeholder = "Enter your user id")
    password = st.text_input(label = "Password", key = 'pass_register', type = "password", max_chars = 40, placeholder = "Enter your password")
    st.button("Signup", key = 'signup', on_click=register, args=(name, userId, password), disabled=(userId == '' or password == '' or name == ''))
    st.button("Login", key='showLogin', on_click=show_login_form, args=(True,)) 
    
if not st.session_state.setup_complete \
    and st.session_state.login_success:

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
        placeholder="Choose one",
        index=5
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
                        f"Respond as bullet points in not more than 5")
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