import streamlit as st
from openai import OpenAI
import json
import os

DB_FILE = 'db.json'


def main():
    import streamlit as st
    st.title("EtikBot")
    st.subheader("En plats att diskutera etiska frågeställningar kring ditt arbete")

    client = OpenAI(api_key="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")

    # List of models
    models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]

    # Create a select box for the models
    st.session_state["openai_model"] = st.sidebar.selectbox("Select OpenAI model", models, index=0)

    # Sidebar with links
    st.sidebar.header("Resurser:")

    st.sidebar.markdown("Här är en samling länkar till resurser där du kan läsa mer om etik för forskning och studentarbeten")

    st.sidebar.markdown("[God forskningssed 2024](https://www.vr.se/analys/rapporter/vara-rapporter/2024-10-02-god-forskningssed-2024.html)")

    st.sidebar.markdown("[Etikprövning – så går det till (med mallar för samtyckesblanketter)](https://etikprovningsmyndigheten.se/for-forskare/sa-gar-det-till/)")

    st.sidebar.markdown("[AoIR Ethical Guidelines 3.0](https://aoir.org/reports/ethics3.pdf)")

    st.sidebar.markdown("[Refero - Guide till akademisk integritet och referenshantering](https://ub.lnu.se/guider/refero/#/)")

    st.sidebar.markdown("[The Integrity Games - Utforska etiska scenarior](https://integgame.eu/)")

    # Load chat history from db.json
    with open(DB_FILE, 'r') as file:
        db = json.load(file)
    st.session_state.messages = db.get('chat_history', [])

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Hur kan jag hjälpa dig idag?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": "system","content": "You are an AI Ethics Bot that provides thoughtful and balanced responses to ethical dilemmas posed by Humanities students in a Swedish context. Your responses should use information from Etikprövningsmyndigheten and the Association of Internet Researchers guidelines. Also consider legal frameworks such as GDPR."}
                    ] + [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Store chat history to db.json
        db['chat_history'] = st.session_state.messages
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)

    # Add a "Clear Chat" button to the sidebar
    if st.sidebar.button('Radera chat'):
        # Clear chat history in db.json
        db['chat_history'] = []
        with open(DB_FILE, 'w') as file:
            json.dump(db, file)
        # Clear chat messages in session state
        st.session_state.messages = []
        st.rerun()


if __name__ == '__main__':

    if 'openai_api_key' in st.session_state and st.session_state.openai_api_key:
        main()

    else:

        # if the DB_FILE not exists, create it
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, 'w') as file:
                db = {
                    'openai_api_keys': [],
                    'chat_history': []
                }
                json.dump(db, file)
        # load the database
        else:
            with open(DB_FILE, 'r') as file:
                db = json.load(file)

        # display the selectbox from db['openai_api_keys']
        selected_key = st.selectbox(
            label="Existing OpenAI API Keys",
            options=db['openai_api_keys']
        )

        # a text input box for entering a new key
        new_key = st.text_input(
            label="New OpenAI API Key",
            type="password"
        )

        login = st.button("Login")

        # if new_key is given, add it to db['openai_api_keys']
        # if new_key is not given, use the selected_key
        if login:
            if new_key:
                db['openai_api_keys'].append(new_key)
                with open(DB_FILE, 'w') as file:
                    json.dump(db, file)
                st.success("Key saved successfully.")
                st.session_state['openai_api_key'] = new_key
                st.rerun()
            else:
                if selected_key:
                    st.success(f"Logged in with key '{selected_key}'")
                    st.session_state['openai_api_key'] = selected_key
                    st.rerun()
                else:
                    st.error("API Key is required to login")
