import os
from supabase import create_client
from .config import settings

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def upload_image(report_id: str, file):
    # file: UploadFile from FastAPI
    file_ext = os.path.splitext(file.filename)[1]
    storage_path = f"{report_id}/{file.filename}"
    await file.seek(0)
    contents = await file.read()
    print(f"Uploading file: {file.filename}, size: {len(contents)} bytes")
    # Guess content type
    import mimetypes
    content_type = mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
    # Enable upsert so repeated filenames don't fail
    try:
        res = supabase.storage.from_('complaint-images').upload(
            storage_path,
            contents,
            # storage3 expects camelCase keys and string 'true' for upsert
            file_options={"contentType": content_type, "upsert": "true"}
        )
    except Exception as e:
        raise Exception(f"Supabase storage upload exception: {e}")
    # Check for error attribute or fallback to truthy check
    if hasattr(res, 'error') and res.error:
        raise Exception(f"Supabase storage upload failed: {res.error}")
    # Get public URL (handle different possible return types)
    public_url = supabase.storage.from_('complaint-images').get_public_url(storage_path)
    if hasattr(public_url, 'public_url'):
        return public_url.public_url
    elif hasattr(public_url, 'data') and isinstance(public_url.data, dict) and 'publicUrl' in public_url.data:
        return public_url.data['publicUrl']
    else:
        return str(public_url)
