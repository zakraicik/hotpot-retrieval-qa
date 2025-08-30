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
        model="anthropic/claude-3-7-sonnet-20250219", api_key=api_key, max_tokens=1500
    )
    dspy.configure(lm=lm)
    logging.info("✅ DSPy configured")
    return True
