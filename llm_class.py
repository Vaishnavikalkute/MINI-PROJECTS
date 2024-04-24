import base64
import json
import os
from fastapi.encoders import jsonable_encoder
from openai import AsyncAzureOpenAI, OpenAI,AsyncOpenAI, AzureOpenAI 
from app.data import models
from app.core.config import settings
from app.data.database import get_db
from app.helpers.encryption_helper import decode_value_with_base64, encode_value_with_base64
from app.helpers.redis_helper import RedisHelper

redis_openai_key_prefix=os.environ.get("redis_key")

redis_workspace = RedisHelper(db=settings.REDIS_DB_WORKSPACE)

class LLMApis:
    #Define clients
    OPENAI = "openai"
    AZURE = "azure"


class LLMModels:
    # Define model version 
    GPT3_5 = "gpt-3.5-turbo"
    GPT3_5_16k = "gpt-3.5-turbo-16k"
    GPT_4_preview = "gpt-4-1106-preview"
    GPT_EMBEDDING_ADA_002="text-embedding-ada-002"
    """
    THE MODEL NAME VALUES ARE THE DEPLOYEMENT NAME IN AUZRE 
    For each openai model different deployement name is needed
    """
    AZURE_GPT_3_5_TURBO="gpt-35-turbo"
    AZURE_GPT_4_preview="gpt-4"
    AZURE_GPT_EMBEDDING_ADA_002="text-embedding-ada-002"

class LLMClient:
    """_summary_
    ***Base class***
    
    """
   
    def __init__(self, workspace_id):
        pass

    @staticmethod
    def create_client(workspace_id,client_type,call_type):
        if call_type=="sync":
            if client_type == LLMApis.OPENAI:
                return OpenaiLlmClient(workspace_id=workspace_id)
            elif client_type == LLMApis.AZURE:
                return AzureOpenaiLlmClient(workspace_id=workspace_id)
        elif call_type=="async":
            if client_type == LLMApis.OPENAI:
                return OpenaiLlmAsyncClient(workspace_id=workspace_id)
            elif client_type == LLMApis.AZURE:
                return AsyncAzureOpenaiLlmClient(workspace_id=workspace_id)
        
        else:
            raise ValueError(f"Unsupported client/call type: {client_type},{call_type}")

    def get_chat_completion(self, messages):
        raise NotImplementedError("get_chat_completion method must be implemented in subclasses.")
    
    def cache_llm_details(self,workspace_id):
        with next(get_db()) as db:
            llm_data=db.query(models.LLM_Details).filter(models.LLM_Details.workspace_id == workspace_id).first() 
            if (llm_data and llm_data.llm_key) :   
                try :
                    update_llm_data = jsonable_encoder(llm_data)
                    redis_workspace.add(f'{redis_openai_key_prefix}_{workspace_id}',json.dumps(update_llm_data))
                    return update_llm_data
                except Exception as e:
                    print(f"error:{e}")
            else:
                workspace_data=db.query(models.Workspaces).filter(models.Workspaces.id == workspace_id).first() 
                update_llm_data={
                    "llm_key": encode_value_with_base64(os.environ.get("OPEN_AI_KEY")) if workspace_data.llm_client_type==LLMApis.OPENAI else encode_value_with_base64(os.environ.get("AZURE_OPENAI_KEY")),
                    "llm_organization_key": encode_value_with_base64(os.environ.get("ORGANISATION_KEY")) if os.environ.get("ORGANISATION_KEY") else None,
                    "llm_endpoint": encode_value_with_base64(os.environ.get("AZURE_ENDPOINT")) if workspace_data.llm_client_type==LLMApis.AZURE else None
                }
                redis_workspace.add(f'{redis_openai_key_prefix}_{workspace_id}',json.dumps(update_llm_data))
                return update_llm_data

    def get_llm_details(self,workspace_id):
        """_summary_
        This function provide all the required data for openai client
        Args:
            workspace_id (_type_): int

        Returns:
            _type_: object of workspace credentials
        """
        try:
            workspace_data = redis_workspace.get(f'{redis_openai_key_prefix}_{workspace_id}')
            if not workspace_data:
                workspace_data = self.cache_llm_details(workspace_id)
            else:
                workspace_data = json.loads(workspace_data.decode('utf-8'))
            return workspace_data
        except Exception as e:
            print(f"Error retrieving workspace data: {e}")
            return None
    

# Child class below

class OpenaiLlmClient(LLMClient):

    def __init__(self, workspace_id):
        super().__init__(workspace_id)
        workspace_data = self.get_llm_details(workspace_id)
        self.client = OpenAI(api_key=decode_value_with_base64(workspace_data.get("llm_key")), organization=decode_value_with_base64(workspace_data.get("llm_organization_key")) if workspace_data.get("llm_organization_key") else None)


    def get_chat_completion(self, messages,model=LLMModels.GPT3_5, temperature=0.5):
        return self.client.chat.completions.create(messages=messages, model=model, temperature=temperature).choices[0].message
    
    def get_chatgpt_embeddings(self,input,model=LLMModels.GPT_EMBEDDING_ADA_002):
        return self.client.embeddings.create(input=input, model=model).data[0].embedding


class OpenaiLlmAsyncClient(LLMClient):

    def __init__(self, workspace_id):
        super().__init__(workspace_id)
        workspace_data = self.get_llm_details(workspace_id)
        self.async_client = AsyncOpenAI(api_key=decode_value_with_base64(workspace_data.get("llm_key")), organization=decode_value_with_base64(workspace_data.get("llm_organization_key")) if workspace_data.get("llm_organization_key") else None )

    async def get_chat_completion(self, messages,model=LLMModels.GPT3_5, temperature=0.5):
        completion= await self.async_client.chat.completions.create(messages=messages, model=model, temperature=temperature)
        return completion.choices[0].message.content
       
    async def get_chat_completion_with_stream(self, messages, model=LLMModels.GPT3_5, temperature=0.5, stream=False):
        completions = await self.async_client.chat.completions.create(messages=messages, model=model, temperature=temperature, stream=stream)
        async for response in completions:
            chuck_data={
                "id":response.id,
                "content": response.choices[0].delta.content
            }
            yield chuck_data

class AzureOpenaiLlmClient(LLMClient):
    def __init__(self,workspace_id):
        super().__init__(workspace_id)
        workspace_data = self.get_llm_details(workspace_id)
        self.client = AzureOpenAI(api_key=decode_value_with_base64(workspace_data.get("llm_key")), api_version="2024-02-01", azure_endpoint=decode_value_with_base64(workspace_data.get("llm_endpoint")))
 
    def get_chat_completion(self, messages, model=LLMModels.AZURE_GPT_3_5_TURBO, temperature=0.5):
        return self.client.chat.completions.create(messages=messages, model=model,temperature=temperature).choices[0].message
    
    def get_chatgpt_embeddings(self,input,model=LLMModels.AZURE_GPT_EMBEDDING_ADA_002):
        return self.client.embeddings.create(input=input, model=model).data[0].embedding

class AsyncAzureOpenaiLlmClient(LLMClient):
    def __init__(self,workspace_id):
        super().__init__(workspace_id)
        workspace_data = self.get_llm_details(workspace_id)
        self.async_client = AsyncAzureOpenAI(api_key=decode_value_with_base64(workspace_data.get("llm_key")), api_version="2024-02-01", azure_endpoint=decode_value_with_base64(workspace_data.get("llm_endpoint")))  
       
    async def get_chat_completion(self, messages, model=LLMModels.AZURE_GPT_3_5_TURBO, temperature=0.5):
        completion= await self.async_client.chat.completions.create(messages=messages, model=LLMModels.AZURE_GPT_3_5_TURBO, temperature=temperature)
        return completion.choices[0].message.content
    

    async def get_chat_completion_with_stream(self, messages, model=LLMModels.AZURE_GPT_3_5_TURBO, temperature=0.5, stream=True):
        completions = await self.async_client.chat.completions.create(messages=messages, model=model, temperature=temperature, stream=stream)
        
        async for response in completions:           
            chuck_data={
                "id":response.id,
                "content": response.choices[0].delta.content if response.choices else ""
            }
            yield chuck_data



