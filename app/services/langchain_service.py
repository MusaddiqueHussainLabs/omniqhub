import os
import getpass
from typing import List

from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain import hub
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import PromptTemplate, HumanMessagePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.schema.document import Document
from langchain_core.messages import AIMessage, HumanMessage
# from langchain_text_splitters import CharacterTextSplitter

from langchain_community.document_loaders import AzureBlobStorageContainerLoader
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.models.conversations_response import SupportingContentRecord, SupportingImageRecord, ApproachResponse
from app.schemas.conversations_schema import Conversations, RequestModel, ResponseModel, ChatResponseModel, LineListOutputParser
from app.models.prompts import template, contextualize_q_system_prompt, qa_system_prompt, generate_queries_prompt

from dotenv import load_dotenv
load_dotenv(override=True)

vector_store_address: str = os.environ["AZURE_SEARCH_ENDPOINT"]
vector_store_password: str = os.environ["AZURE_SEARCH_ADMIN_KEY"]

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass("Provide your Google API key here")

# print(os.environ["GOOGLE_API_KEY"])
    
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

index_name: str = os.environ["AZURE_SEARCH_ENDPOINT_INDEX_NAME"]
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

# Retrieve and generate using the relevant snippets of the blog.
retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.5})
prompt = hub.pull("rlm/rag-prompt")
llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

class LangchainService:
    def __init__(self):
        pass

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_chat_response(self, request: RequestModel):

        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser(pydantic_object=ChatResponseModel)

        # custom_rag_prompt = PromptTemplate.from_template(template)
        custom_rag_prompt = PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: self.format_docs(x["context"])))
            | custom_rag_prompt
            | llm
            | parser
        )

        rag_chain_with_source = RunnableParallel(
            {"context": retriever, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_from_docs)

        result = rag_chain_with_source.invoke(request.lastUserQuestion)
        # print(result)

        return result
    
    def get_chat_response_with_history(self, request: RequestModel):
        
        self.request = request

        # contextualize_query = self.get_contextualize_query()
        # print(contextualize_query)

        # Set up a parser + inject instructions into the prompt template.
        parser = JsonOutputParser(pydantic_object=ChatResponseModel)

         # custom_rag_prompt = PromptTemplate.from_template(template)
        custom_rag_prompt = PromptTemplate(
            template=template,
            input_variables=["question"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        rag_chain_with_history = (
            RunnablePassthrough.assign(
                context=self.contextualized_question | retriever | self.format_docs
            )
            | custom_rag_prompt
            | llm
            | parser
        )

        rag_chain_with_source = RunnableParallel(
            {"context": retriever, "question": RunnablePassthrough()}
        ).assign(answer=rag_chain_with_history)


        # result = rag_chain_with_source.invoke({"question": request.lastUserQuestion, "chat_history": self.prepare_chat_history(request=request)})
        result = rag_chain_with_source.invoke(request.lastUserQuestion)
        # print(result)

        return result
    
    def generate_queries(self, question: str) -> List[str]:

        output_parser = LineListOutputParser()

        prompt = ChatPromptTemplate.from_template(generate_queries_prompt)

        chain = (
            {"context": retriever | self.format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | output_parser
        )

        response = chain.invoke(question)
        return response
                
    def get_data_points_response(self, documents):

        supporting_content = []

        for doc in documents:

            path = doc.metadata['source']
            pdf_name = os.path.basename(path)
        
            support_record = SupportingContentRecord(title=pdf_name, content=doc.page_content)

            supporting_content.append(support_record.model_copy())

        return supporting_content
    
    def get_source_doc_list(self, documents):

        doc_name = set()

        for doc in documents:

            path = doc.metadata['source']
            pdf_name = os.path.basename(path)
        
            doc_name.add(pdf_name)

        return list(doc_name)
    
    def get_contextualize_query(self):

        contextualize_q_chain = self.get_contextualize_q_chain()

        contextualize_query =   contextualize_q_chain.invoke(
                                    {
                                        "chat_history": self.prepare_chat_history(),
                                        "question": self.request.lastUserQuestion,
                                    }
                                )
        
        return contextualize_query
    
    def get_contextualize_q_chain(self):

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )

        contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()

        return contextualize_q_chain
    
    def prepare_chat_history(self):

        chat_history = []

        for history in self.request.history:

            human_message = HumanMessage(content=history.user)
            ai_message = AIMessage(content=history.bot if history.bot is not None else "")

            chat_history.append(human_message.copy())
            chat_history.append(ai_message.copy())
        
        return chat_history
    
    def contextualized_question(self, input: dict):
        if input.get("chat_history"):
            return self.get_contextualize_query()
        else:
            return input["question"]