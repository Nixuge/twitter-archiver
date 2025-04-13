from datetime import datetime
import re
import pytz

CET = pytz.timezone('CET')

def get_formatted_cet_time():
    date_utc = datetime.now(tz=pytz.utc)
    date_cet = date_utc.astimezone(CET)
    formatted_cet_time = date_cet.strftime("%Y-%m-%d %Hh%M CET")
    return formatted_cet_time

def format_url_universal_binbows(url: str) -> str:
    pattern = r"\?tag=(\d*)$"
    match = re.search(pattern, url)
    if not match:
        return url.replace("?", "QUESTION_MARK")
    
    transformed_url = url.replace(match.group(0), "")

    # Find the extension and place it at the end
    main_part, extension = transformed_url.rsplit('.', 1)

    url_tag_fixed = f"{main_part}-tag={match.group(1)}.{extension}"

    return url_tag_fixed.replace("?", "QUESTION_MARK")