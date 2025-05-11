import logging
from dotenv import load_dotenv
from ..config import settings
from typing import Tuple, Dict, Any
from langchain_cohere import CohereRerank
from langchain_core.prompts import PromptTemplate
from src.utils.vector_store import VectorStoreService
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import ContextualCompressionRetriever
from src.db.db_connection import get_chat_history, save_chat_history                    
            
class RAGChain:
    def __init__(self):
        self._configure_logging()
        load_dotenv()
        self.logger = logging.getLogger(__name__)

    def _configure_logging(self) -> None:    
        """
        Configure logging for the application.

        This function sets up basic logging for the application by calling
        logging.basicConfig(). The logging level is set to INFO, and the
        logging format is set to '%(asctime)s - %(levelname)s: %(message)s'.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s: %(message)s'
        )

    def __create_retriever_chain(self, vector_store_id: str) -> Tuple[ConversationalRetrievalChain, Any]:
        """
        Create a ConversationalRetrievalChain with a custom prompt template and
        Cohere reranker.

        This function creates a ConversationalRetrievalChain that uses a custom
        prompt template and a Cohere reranker to reorder the retrieved
        the vector store loaded from the given vector store ID.

        Args:
            vector_store_id (str): The ID of the vector store.

        Returns:
            Tuple[ConversationalRetrievalChain, Any]: A tuple containing the
                created ConversationalRetrievalChain and the Weaviate client.
        """


        try:
            # Load vector store and Weaviate client
            vectorstore, weaviate_client = VectorStoreService().load_vector_db(vector_store_id=vector_store_id)
            
            # Create Prompt template
            template = """
            You are a helpful and knowledgeable AI assistant designed to answer questions based on your knowledge and uploaded documents using a Retrieval-Augmented Generation (RAG) system.

            Your goal is to deliver clear, accurate, and concise responses in markdown format (highly structured).

            ---

            ### **📚 Document Context**:
            {context}

            ---

            ### **❓User Question**:
            {question}

            ---

            ### **🧠 Instructions**:
            - Answer in markdown based on the context.
            - If context is irrelevant, say so and use general knowledge.
            - If the context contains sufficient information, respond using that information and your knowledge.
            - Format your response in **markdown** (use bullet points, headings, etc., where applicable).
            - If the context does **not** contain relevant information:
            1. Clearly state: *"The retrieved context does not provide relevant information."*
            2. Then, offer a response based on general knowledge, or suggest the user provide more details or documents.

            Keep your tone professional and easy to understand.
            """

            
            create_prompt_template = PromptTemplate(
                input_variables=["context", "question"],
                template=template
            )
            
            # Initialize LLM
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                api_key=settings.GOOGLE_API_KEY
            )

            # Create base retriever
            self.logger.info("✅ Creating base retriever...")
            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 10, "fetch_k": 10},
                alpha=0.5
            )
            self.logger.info("Base retriever created successfully.")

            # Initialize reranker
            reranker = CohereRerank(
                cohere_api_key=settings.COHERE_API_KEY,
                model="rerank-english-v3.0"
            )

            # Create compression retriever
            compression_retriever = ContextualCompressionRetriever(
                base_compressor=reranker,
                base_retriever=retriever
            )
            
            # 🔁 Add conversation memory
            memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            
            # Create conversational chain
            chain = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=compression_retriever,
                return_source_documents=True,
                memory=memory,
                combine_docs_chain_kwargs={
                    "prompt": create_prompt_template,
                    "document_variable_name": "context"
                }
            )
            self.logger.info("🚀 Retriever chain created successfully.")
            return chain, weaviate_client

        except Exception as e:
            self.logger.error(f"❌ Failed to create retriever chain: {str(e)}")
            raise

    def get_response(self, question: str, vector_store_id: str, user_name: str, project_name: str) -> Dict[str, Any]:
        """
        Generate a response to a question using the RAG system.

        Args:
            question (str): The user's question.
            vector_store_id (str): The ID of the vector store.
            user_name (str): The name of the user.
            project_name (str): The name of the project.

        Returns:
            Dict[str, Any]: The response containing the answer and metadata.

        Raises:
            Exception: If response generation fails.
        """
        try:
            # Fetch chat history
            self.logger.info("📚 Fetching chat history...")
            chat_history = get_chat_history(vector_id=vector_store_id)
            chat_history_list = [
                (entry["user_query"], entry["chatbot_answer"])
                for entry in chat_history
            ]
            self.logger.info("📂 Chat history fetched successfully.")

        except Exception as e:
            self.logger.error(f"❌ Failed to fetch chat history: {str(e)}")
            chat_history = []
            chat_history_list = []

        # Create retriever chain
        retriever_chain, weaviate_client = self.__create_retriever_chain(vector_store_id)

        try:
            # Generate response
            self.logger.info("🔗 Generating response...")
            response = retriever_chain.invoke({
                "question": question,
                "chat_history": chat_history_list
            })

            # Save chat history
            self.logger.info("📂 Saving chat history...")
            result = response["answer"].replace("```markdown", "").replace("```", "")
            chat_history.append({
                "user_query": question,
                "chatbot_answer": result
            })
            save_chat_history(chat_history=chat_history, user_name=user_name,
                              project_name=project_name, vector_id=vector_store_id)
            self.logger.info("🚀 Chat history saved successfully.")

            return response

        finally:
            # Ensure Weaviate client is closed
            self.logger.info("🆑 Closing Weaviate client...")
            weaviate_client.close()
            

RAG_Chain = RAGChain()