import logging
from hotpot_retrieval_qa.retrieval import Retrieval

logger = logging.getLogger(__name__)


class RetrieverService:
    _instance = None
    _retriever = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the retriever"""
        if self._retriever is None:
            self._retriever = Retrieval()
            logger.info("Retriever initialized")

    def get_retriever(self):
        """Get the retriever instance"""
        return self._retriever
