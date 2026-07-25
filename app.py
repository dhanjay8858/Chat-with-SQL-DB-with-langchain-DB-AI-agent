import streamlit as st
import sqlite3
import os

from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain.agents.agent_types import AgentType



load_dotenv()

st.title("Langchain: Chat with SQL Database")


LOCALDB='USE_LOCALDB'
MYSQLDB='USE_MYSQLDB'


radio_option=['Use SQLite3 DataBase(student.db)','Connect to MYSLQ DataBase']

selected_option= st.sidebar.radio("Choose the DB you want to Chat with",options=radio_option)


if selected_option==radio_option[1]:
    db_url=MYSQLDB
    mysql_host=st.sidebar.text_input("Provide MYSQL Hostname",value="localhost")
    mysql_user=st.sidebar.text_input("Provide MYSQL Username",value="root")
    mysql_password=st.sidebar.text_input("provide MYSQL Password",type="password")
    mysql_db=st.sidebar.text_input("Provide MYSQL  Database Name")

else:
    db_url=LOCALDB


groq_api_key=st.sidebar.text_input("Provide with the groq API Key :",type="password")


if  not groq_api_key:
    st.info("Please Provide groq API Key to continue")
    st.stop()

model = ChatGroq(
    model="llama-3.3-70b-versatile",
    streaming=True,
    api_key=groq_api_key
)

@st.cache_resource(ttl=7200)
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()

        engine = create_engine(f"sqlite:///{dbfilepath}")

        return SQLDatabase(engine)
    
    elif db_uri == MYSQLDB:

        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please Provide all MySQL connection Details")
            st.stop()

        encoded_password = quote_plus(mysql_password)

        connection_str = (
            f"mysql+mysqlconnector://"
            f"{mysql_user}:{encoded_password}"
            f"@{mysql_host}/{mysql_db}"
        )

        try:
            db = SQLDatabase(create_engine(connection_str))
            st.success("Successfully Connected To MYSQL Database !")
            return db

        except Exception as e:
            st.error(f"Failed to connect to Mysql: {e}")
            st.stop()



if db_url==MYSQLDB:
    db=configure_db(db_url,mysql_host,mysql_user,mysql_password,mysql_db)

else:
    db=configure_db(db_url)


# SQL AGENT

toolkit=SQLDatabaseToolkit(db=db,llm=model)

agent=create_sql_agent(llm=model,toolkit=toolkit,verbose=True,agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "How can I help you?"
        }
    ]

for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(
    placeholder="Ask anything from the database..."
)

if user_query:
    st.session_state["messages"].append(
        {
            "role": "user",
            "content": user_query
        }
    )

    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(
            st.container()
        )

        response = agent.invoke(
            {"input": user_query},
            {"callbacks": [streamlit_callback]}
        )
        answer = response["output"]

        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.write(answer)


    


