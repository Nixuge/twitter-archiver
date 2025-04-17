from datetime import datetime
import re
import traceback
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

def ddhhmmss_to_ss(dd: int = 0, hh: int = 0, mm: int = 0, ss: int = 0):
    return ss + mm * 60 + hh * 3600 + dd * 86400

class Err:
    name: str
    content: dict | list | str
    extension: str
    
    # Usually the extension is either json or txt, mostly json tho.
    def __init__(self, name: str, content: dict | list | str, extension: str = "json") -> None:
        self.name = name if name is not None else "Empty..."
        self.content = content if name is not None else "Empty..."
        self.extension = extension
    
    @classmethod
    def from_exception(cls, excp: Exception):
        # Thanks https://stackoverflow.com/a/37135014
        stack = traceback.extract_stack()[:-3] + traceback.extract_tb(excp.__traceback__)  # add limit=?? 
        pretty = traceback.format_list(stack)
        return cls("Python Exception", ''.join(pretty) + '\n  {} {}'.format(excp.__class__,excp), "txt")