# SmokiesGuide — AI Visitor Guide (Streamlit)
A safety-first chatbot for Great Smoky Mountains National Park (GSMNP).

## Local
pip install -r requirements.txt
# set your key
export OPENAI_API_KEY=sk-...
streamlit run app.py

## Deploy on Streamlit Cloud
- Push to GitHub, create new Streamlit app
- In Secrets, add OPENAI_API_KEY
- Deploy and share the public URL with your class