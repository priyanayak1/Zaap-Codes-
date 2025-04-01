# Zaap-Codes-
Capstone Project 

Priya, Ava, Amanda, Zeus

if it shows "no module found requests" 

to run the program on mac:
terminal to Zaap-Codes-
python3 -m venv venv
source venv/bin/activate

### To install Psycopg 3

```pip3 install "psycopg[binary,pool]"```

### Using Chatbot

We are using Google Cloud's Gemini's AI API for the chatbot. In order to run it you need to make sure you install the correct library and save API token to an environment variable.

```pip3 install google-genai```
```export GEMINI_API_KEY=<token goes here!>```

You can set a temporary key or you can save it in your bash/zsh profile.

MacOS:
```~/.zprofile << export GEMINI_API_KEY=<token goes here!>```

Bash:
```~/.bash_profile << export GEMINI_API_KEY=<token goes here!>```

Gemini's documentation:
[https://ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs)