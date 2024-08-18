import re
from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URI=''
COLLECTION_NAME=''
DATABASE_NAME=''

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
media_collection = db[COLLECTION_NAME]

async def if_file(query: str, file_type: str = None) -> bool:
    """Check if the given query has any matching result in the database."""

    query = query.strip()
    
    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_\(\)])' + query + r'(\b|[\.\+\-_\(\[\,\]\)])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_\(\[\,\]\)]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error:
        raise ValueError("Invalid regex pattern")

    filter_criteria = {'$or': [{'file_name': regex}, {'caption': regex}]}
    if file_type:
        filter_criteria['file_type'] = file_type

    # Check if any document matches the query
    result = await media_collection.find_one(filter_criteria)
    
    return bool(result)
