import re
from pathlib import Path


def get_voice_name(file_path):
    with open(file_path, 'r') as file:
        file_content = file.read()
        pattern = r"\"ShortName\":\"([^\"]+)\""
        match = re.search(pattern, file_content)
        if match:
            voice_name = match.group(1)
            voice_name = voice_name.split("-")[-1]
            # voice_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', voice_name)
            # return voice_name.replace("Neural", "").strip()
            return voice_name
        else:
            raise Exception


def generate_voice_configurations(base_folder):
    voice_configurations = {}

    base_path = Path(base_folder)
    subfolders = [subfolder for subfolder in base_path.iterdir() if subfolder.is_dir()]

    for subfolder in subfolders:
        voice_configurations[subfolder.name] = {}

        files = [file for file in subfolder.glob("*.txt") if file.is_file()]

        for file in files:
            voice_name = get_voice_name(str(file))
            voice_configurations[subfolder.name][voice_name] = file

    return voice_configurations


def modify_ssml(ssml_string, new_text):
    pattern1 = r"<prosody([^>]*)>.*?<\/prosody>"
    pattern2 = r"<mstts:express-as([^>]*)>.*?<\/mstts:express-as>"
    pattern3 = r"<s />.*?<s />"
    pattern4 = r"<voice([^>]*)>.*?</voice>"

    match1 = re.search(pattern1, ssml_string)
    match2 = re.search(pattern2, ssml_string)
    match3 = re.search(pattern3, ssml_string)
    match4 = re.search(pattern4, ssml_string)
    if match1:
        return re.sub(pattern1, f"<prosody\\1>{new_text}</prosody>", ssml_string)
    elif match2:
        return re.sub(pattern2, f"<mstts:express-as\\1>{new_text}</mstts:express-as>", ssml_string)
    elif match3:
        return re.sub(pattern3, f"<s />{new_text}<s />", ssml_string)
    elif match4:
        return re.sub(pattern4, f"<voice\\1>{new_text}</voice>", ssml_string)


def improve_pronunciation(text, target_lang_code):
    x_weak_break = '-<break strength="x-weak"/>'
    # Replace mobile numbers with spaces between them with dashes
    text = re.sub(r'\b1\s\d{3}\s\d{3}\s\d{4}\b',
                  lambda match: match.group().replace(" ", '-'),
                  text)
    if target_lang_code == "fr":
        text = re.sub(r'\bTélésanté\b', 'Téléssanté ', text)

        # text = re.sub(r'\b1-\d{3}-\d{3}-\d{4}\b',
        #               lambda match: match.group().replace("-", f',{x_weak_break}'),
        #               text)
        # Input text
        #########

        # Step 1: Find and extract phone number patterns
        matches = re.findall(r'\b(\d)-?(\d{3})-?(\d{3})-?(\d{4})\b|\b(\d) (\d{3}) (\d{3}) (\d{4})\b', text)

        # Step 2: Combine the digits to form a single number without spaces or dashes
        numbers = [''.join(match[:4]) if match[0] else ''.join(match[4:]) for match in matches]

        # Step 3: Format the resulting numbers with breaks
        formatted_numbers = '<break strength="x-weak"/> ,'.join(list(' '.join(numbers)))


        # Replace the phone numbers in the original text with the formatted version
        text = re.sub(r'\b(\d)-?(\d{3})-?(\d{3})-?(\d{4})\b|\b(\d) (\d{3}) (\d{3}) (\d{4})\b', formatted_numbers, text)

###################
        text = re.sub(r'\b911\b', f'{x_weak_break} 9,{x_weak_break}1, {x_weak_break}1', text)
    else:
        text = re.sub(r'\b911\b', '9-1-1', text)

    # Regular expression to match URLs
    url_pattern = r'((?:http://|https://|www\.)\S+|(?:\w+\.\w+/\S+))'

    # Find all URL matches in the text
    urls = re.findall(url_pattern, text)

    # Replace each URL with the enhanced format and add a comma after the URL
    for url in urls:
        enhanced_url = re.sub(r'/', ',/', url)
        text = text.replace(url, enhanced_url + ",")

    # Replace "WSIB" with "W S IB"
    text = text.replace("WSIB", "W S IB")
    text = text.replace("wsib", "W S IB")

    return text
