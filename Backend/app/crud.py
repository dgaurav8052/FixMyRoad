from .storage import upload_image
from .config import settings
from supabase import create_client

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

import random
from postgrest.exceptions import APIError
import uuid

def _get_next_sequential_id():
    """Generate the next sequential integer ID starting from 1.

    This uses a lightweight approach with a dedicated Supabase table `ReportCounters`
    having a single row with column `next_id`. If the table/row doesn't exist,
    it initializes at 1.
    """
    # Try to select the counter row (assume id=1)
    try:
        # Some client versions return dict, others return list for single()
        res = supabase.table("ReportCounters").select("id,next_id").eq("id", 1).single().execute()
        data = res.data
        next_id = None
        if isinstance(data, dict) and "next_id" in data:
            next_id = int(data["next_id"])
        elif isinstance(data, list) and data and "next_id" in data[0]:
            next_id = int(data[0]["next_id"])
        if next_id is None:
            supabase.table("ReportCounters").insert({"id": 1, "next_id": 2}).execute()
            return 1
    except Exception:
        # Best-effort initialization if select fails
        try:
            supabase.table("ReportCounters").insert({"id": 1, "next_id": 2}).execute()
            return 1
        except Exception:
            # As a last resort, fall back to 1 (non-atomic)
            return 1

    # Increment and persist
    updated = supabase.table("ReportCounters").update({"next_id": next_id + 1}).eq("id", 1).execute()
    # Ignore update validation; return the current id
    return next_id

def _bump_counter_to_at_least(min_next_id: int) -> None:
    try:
        # Set next_id to at least min_next_id
        res = supabase.table("ReportCounters").select("id,next_id").eq("id", 1).single().execute()
        data = res.data
        current = None
        if isinstance(data, dict) and "next_id" in data:
            current = int(data["next_id"])
        elif isinstance(data, list) and data and "next_id" in data[0]:
            current = int(data[0]["next_id"])
        if current is None:
            supabase.table("ReportCounters").insert({"id": 1, "next_id": min_next_id}).execute()
        elif current < min_next_id:
            supabase.table("ReportCounters").update({"next_id": min_next_id}).eq("id", 1).execute()
    except Exception:
        # Best-effort; ignore if fails
        pass

async def create_report(name, contact_details, issue_category, discription, manual_location_input, files):
    from datetime import datetime
    # Get sequential integer report id starting from 1
    report_id = _get_next_sequential_id()
    submitted_at = datetime.utcnow().date().isoformat()
    updated_at = submitted_at
    # Insert into Reports table
    report_data = {
        "report_id": report_id,
        "name": name,
        "contact_details": contact_details,
        "issue_category": issue_category,
        "discription": discription,
        "manual_location_input": manual_location_input,
        "status": "submitted",
        "submitted_at": submitted_at,
        "updated_at": updated_at
    }
    try:
        res = supabase.table("Reports").insert(report_data).execute()
    except APIError as e:
        # Handle duplicate key on report_id by recalculating next id from current max
        if getattr(e, 'code', None) == '23505' or 'duplicate key value' in str(e):
            # Find current max report_id
            max_res = supabase.table("Reports").select("report_id").order("report_id", desc=True).limit(1).execute()
            max_id = 0
            if max_res.data:
                # handle dict or list
                if isinstance(max_res.data, list) and len(max_res.data) > 0 and 'report_id' in max_res.data[0]:
                    max_id = int(max_res.data[0]['report_id'])
                elif isinstance(max_res.data, dict) and 'report_id' in max_res.data:
                    max_id = int(max_res.data['report_id'])
            report_id = max_id + 1
            _bump_counter_to_at_least(report_id + 1)
            report_data['report_id'] = report_id
            res = supabase.table("Reports").insert(report_data).execute()
        else:
            raise
    if not res.data:
        raise Exception(f"Supabase insert failed: {getattr(res, 'error', res)}")
    # Upload images and insert into complaints_image
    inserted_first_image = False
    for file in files:
        await file.seek(0)
        if not file.filename:
            continue
        contents = await file.read()
        if not contents:
            continue
        await file.seek(0)
        image_url = await upload_image(str(report_id), file)
        if inserted_first_image:
            # Table schema enforces unique(report_id); skip additional images
            continue
        image_id = str(uuid.uuid4())
        img_data = {
            "image_id": image_id,
            "report_id": report_id,
            "image_url": image_url,
            "uploaded_at": submitted_at
        }
        img_res = supabase.table("complaint_images").insert(img_data).execute()
        if not getattr(img_res, 'data', None):
            raise Exception(f"Supabase image insert failed: {getattr(img_res, 'error', img_res)}")
        inserted_first_image = True
    return {"report_id": report_id}
