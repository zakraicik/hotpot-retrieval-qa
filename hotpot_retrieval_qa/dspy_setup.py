import dspy
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()


def setup_dspy():

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logging.error("Set ANTHROPIC_API_KEY environment variable")
        return False

    lm = dspy.LM(
        model="openai/LFM2-700M",  # Add openai/ prefix
        api_base="http://localhost:8080/v1",  # Note the /v1 suffix
        api_key="not-needed",  # Can be any string for local server
        max_tokens=800,
        temperature=0.0,
    )

    dspy.configure(lm=lm)
    logging.info("✅ DSPy configured")
    return True
