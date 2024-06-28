from typing import List, Optional
from config.db import job_description_collection
from models.job_models import JobDescription
from schemas.job_schemas import JobDescriptionCreate, JobDescriptionUpdate
from langchain import HuggingFaceHub
import os


os.environ['HUGGINGFACEHUB_API_TOKEN'] = "your apl key enter"

repo_id = "google/flan-t5-large"

llm = HuggingFaceHub(
    repo_id=repo_id, model_kwargs={"temperature": 0.5, "max_length": 200}
)

def jd_helper(jd) -> dict:
    return {
        "id": jd["id"],
        "prompt": jd["prompt"],
        "job_description": jd["job_description"]
    }

async def get_all_jds() -> List[JobDescription]:
    jds = await job_description_collection.find().to_list(1000)
    return [JobDescription(**jd_helper(jd)) for jd in jds]

async def get_jd(id: int) -> Optional[JobDescription]:
    jd = await job_description_collection.find_one({"id": id})
    if jd:
        return JobDescription(**jd_helper(jd))
    return None

async def create_jd(jd_data: JobDescriptionCreate) -> JobDescription:
    style = """
    This is a job description
    Please help me create a comprehensive and detailed job description using the following template:
    Company Name:
    Company Description:
    Experience:
    Skills:
    Qualification:
    Role Responsibilities:
    Good to Have:
    Populate each field according to the template
    """
    prompt = f"""Create a job description that is delimited by triple backticks 
    into a style that is {style}. 
    text: {jd_data.prompt}```"""
    
    response = llm(prompt)
    
    print(response)
    
    jd_text = response

    new_id = await job_description_collection.count_documents({}) + 1
    
    jd_dict = {
        "id": new_id,
        "prompt": jd_data.prompt,
        "job_description": jd_text
    }
    await job_description_collection.insert_one(jd_dict)
    return JobDescription(**jd_dict)

async def update_jd(id: int, jd_data: JobDescriptionUpdate) -> Optional[JobDescription]:
    jd = await job_description_collection.find_one({"id": id})
    if not jd:
        return None

    update_data = {}

    if jd_data.prompt:
        style = """
        This is a job description
        Please help me create a comprehensive and detailed job description using the following template:
        Company Name:
        Company Description:
        Experience:
        Skills:
        Qualification:
        Role Responsibilities:
        Good to Have:
        Populate each field according to the template
        """
        prompt = f"""Create a job description that is delimited by triple backticks 
        into a style that is {style}. 
        text: {jd_data.prompt}```"""
        
        response = llm(prompt)
        jd_text = response

        update_data["prompt"] = jd_data.prompt
        update_data["job_description"] = jd_text
    elif jd_data.job_description:
        update_data["job_description"] = jd_data.job_description

    if update_data:
        await job_description_collection.update_one({"id": id}, {"$set": update_data})
        jd = await job_description_collection.find_one({"id": id})
        return JobDescription(**jd_helper(jd))

    return JobDescription(**jd_helper(jd))

async def delete_jd(id: int) -> bool:
    result = await job_description_collection.delete_one({"id": id})
    return result.deleted_count > 0
