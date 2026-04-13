import streamlit as st
import os
import zipfile
import json
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

# ------------------ Setup ------------------
load_dotenv()
os.environ['GOOGLE_API_KEY'] = os.getenv('gemini_key')

llm = ChatGoogleGenerativeAI(model='gemini-flash-lite-latest')

# ------------------ Transcript ------------------
def extract_transcript(link: str) -> str:
    loader = YoutubeLoader.from_youtube_url(link)
    docs = loader.load()
    return docs[0].page_content

# ------------------ Article Generator ------------------
system_message = """You are a professional technical article writer."""

human_message = """
Convert the following YouTube transcript into a professional article.

Rules:
- Ignore intro, ads, sponsors
- Focus only on technical content
- Use first-person tone
- Add headings, bullet points, code snippets
- End with summary

Transcript:
{transcript}
"""

article_prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("human", human_message)
])

base_summarizer = (
    RunnablePassthrough()
    | RunnableLambda(extract_transcript)
    | article_prompt
    | llm
    | StrOutputParser()
)

# ------------------ Long Summarizer ------------------
def get_text_chunks(text, chunk_size=5000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

# Agent setup
agent = create_agent(
    model=llm,
    tools=[],   # NO tools - summarization ONLY
    system_prompt=system_message,
    middleware=[
        SummarizationMiddleware(
            model=llm,
            trigger=("tokens", 1000),
            keep=("tokens", 200),
        ),
    ],
)

def recursive_summarize(text, agent=agent):
    chunks = get_text_chunks(text)
    running_summary = ""

    for chunk in chunks:
        response = agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"""
You are summarizing technical content.

Current summary:
{running_summary}

New content:
{chunk}

Follow CRITICAL INSTRUCTIONS:
- IGNORE intros, channel names, sponsors
- FOCUS ONLY on technical content
- Use professional tone, bold subheadings, numbered lists
- Include code snippets
- End with short summary
"""
                }
            ]
        })

        running_summary = response["messages"][-1].content

    return running_summary

long_summarizer = (
    RunnablePassthrough()
    | RunnableLambda(extract_transcript)
    | RunnableLambda(recursive_summarize)
)

def is_long(link):
    return len(extract_transcript(link)) > 1000

smart_summarizer = RunnableBranch(
    (RunnableLambda(is_long), long_summarizer),
    base_summarizer
)




# ------------------ Website Generator ------------------
web_system = """You are a Senior Frontend Web Developer with 10+ years experience in HTML5, CSS3, and modern JavaScript (ES6+).

Your task: Generate COMPLETE, PRODUCTION-READY frontend code based on user requirements.

MANDATORY OUTPUT FORMAT:
--html--
[html code here]
--html--

--css--
[css code here]
--css--

--js--
[javascript code here]
--js--
"""

web_human = """
Create a production-ready article webpage in the style of Medium/Dev.to/Hashnode/Substack.

Requirements:
- Mobile-first responsive design
- Clean typography
- Dark/light theme toggle
- SEO optimized
- Accessibility compliant

CONTENT TO USE: {article_content}
"""

web_dev_template = ChatPromptTemplate.from_messages([("system", web_system), ("human", web_human)])
webpage_chain = web_dev_template | llm | StrOutputParser()
# ------------------ Functions ------------------
def generate_article(url):
    try:
        article = smart_summarizer.invoke(url)
        return article, None
    except Exception as e:
        return None, str(e)

def generate_website(article):
    try:
        # Run the webpage_chain with the article content
        response = webpage_chain.invoke({"article_content": article})

        # Now parse the delimiters from the response
        html = response.split('--html--')[1].strip()
        css = response.split('--css--')[1].strip()
        js = response.split('--js--')[1].strip()

        return html, css, js
    except Exception as e:
        return None, None, None

# ------------------ Streamlit UI ------------------
st.title("🎥 YouTube → Website Generator")
st.write("Convert YouTube videos into article-style websites.")

url = st.text_input("Enter YouTube URL")

if st.button("Generate"):
    if not url:
        st.warning("Enter URL")
        st.stop()

    with st.spinner("Generating article..."):
        article, err = generate_article(url)

    if err or not article:
        st.error(f"Error generating article: {err}")
        st.stop()

    with st.spinner("Building website..."):
        html, css, js = generate_website(article)

    if not html:
        st.error("Website generation failed.")
        st.stop()

    os.makedirs("output", exist_ok=True)

    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    with open("output/style.css", "w", encoding="utf-8") as f:
        f.write(css)
    with open("output/script.js", "w", encoding="utf-8") as f:
        f.write(js)

    zip_path = "output/website.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        zipf.write("output/index.html", arcname="index.html")
        zipf.write("output/style.css", arcname="style.css")
        zipf.write("output/script.js", arcname="script.js")

    st.success("✅ Website Generated!")

    with open(zip_path, "rb") as f:
        st.download_button("📥 Download Website", data=f, file_name="website.zip")

    # Preview
    st.subheader("Preview")
    st.components.v1.html(html, height=600, scrolling=True)