import re


def _convert_header(wikitext):
    # Regular expression to match wikitext headers
    header_regex = r"^(={1,6})(.*?)\1"

    # Replace wikitext headers with markdown headers, and remove any *
    markdown = re.sub(
        header_regex,
        lambda m: "- " + "#" * len(m.group(1)) + " " + m.group(2).replace("*", ""),
        wikitext,
        flags=re.MULTILINE,
    )

    return markdown


def _extract_infobox(wikitext: str) -> str | None:
    """Extract the first Infobox in the input string

    Args:
        wikitext (str): Text with Wikitext format

    Returns:
        str: Infobox, if any, None otherwise
    """
    start_idx = wikitext.find("{{Infobox")
    if start_idx == -1:
        return None, wikitext
    end_idx = start_idx + len("{{Infobox")
    count = 1
    while count > 0 and end_idx < len(wikitext):
        if (
            wikitext[end_idx] == "{"
            and end_idx < len(wikitext) - 1
            and wikitext[end_idx + 1] == "{"
        ):
            count += 1
            end_idx += 2
        elif (
            wikitext[end_idx] == "}"
            and end_idx < len(wikitext) - 1
            and wikitext[end_idx + 1] == "}"
        ):
            count -= 1
            end_idx += 2
        else:
            end_idx += 1
    if count == 0:
        return wikitext[start_idx:end_idx], wikitext[end_idx:]
    else:
        return None, wikitext


def _parse_infobox(infobox):
    # Split the input string into lines
    lines = infobox.split("\n")

    # Initialize a list to hold the output lines
    output_lines = []

    # Flag when lists are being iterated

    multiline_buffer = []

    # Loop over the lines
    for line in lines:
        line = line.strip()
        # If the line starts with "|", add it to the output unchanged
        if line.startswith("|"):
            if multiline_buffer:
                output_lines[-1] = output_lines[-1] + " " + ", ".join(multiline_buffer)
                multiline_buffer = []
            output_lines.append(line[1::].replace(" =", "::"))
        # If the line starts with "*", replace it with a comma
        elif line.startswith("*"):
            multiline_buffer.append(line[1:])

    if multiline_buffer:
        output_lines[-1] = output_lines[-1] + " " + ", ".join(multiline_buffer)
    # Join the output lines into a single string
    output_string = "\n".join(output_lines)

    # Return the output string
    return output_string + "\n"


def _convert_list_items(wikitext):
    output = re.sub(r"^\* ", "\t- ", wikitext, flags=re.MULTILINE)
    return output


def _remove_empty_lines(wikitext):
    output = "\n".join(filter(lambda x: x, wikitext.split("\n")))
    return output


def _itemize_everything(wikitext):
    output = "\n".join(
        [
            x
            if x.startswith("-") or x.startswith("\t-") or not x.startswith("|")
            else f"- {x}"
            for x in wikitext.split("\n")
        ]
    )
    return output


def covert_wikitext_to_markdown(wikitext):

    infobox, wikitext = _extract_infobox(wikitext)

    # Remove any HTML comments
    wikitext = re.sub(r"<!--.*?-->", "", wikitext, flags=re.DOTALL)

    # # Replace any templates with their contents
    wikitext = re.sub(r"{{.*?}}", "", wikitext, flags=re.DOTALL)

    # Replace any bold text with Logseq-compatible markdown
    wikitext = re.sub(r"'''(.*?)'''", r"**\1**", wikitext)

    # Replace any italicized text with Logseq-compatible markdown
    wikitext = re.sub(r"''(.*?)''", r"*\1*", wikitext)

    infobox = _parse_infobox(infobox)
    wikitext = _convert_header(wikitext)
    wikitext = _convert_list_items(wikitext)
    wikitext = _remove_empty_lines(wikitext)
    wikitext = _convert_tables(wikitext)
    markdown = _itemize_everything(wikitext)
    return infobox + markdown


def _convert_table(table):
    table_text = table.group(0)
    header_pattern = r"^!.*?([a-zA-Z]+)\W*$"
    row_pattern = "|-\n"

    # Split the table into header and rows
    rows = table_text.split(row_pattern)[1:]
    headers = re.findall(header_pattern, table_text, re.MULTILINE)
    n_columns = len(headers)

    # Extract the cell contents from each row and build a Markdown table
    markdown_table = "| " + " | ".join(headers) + " |\n"
    markdown_table += "|-" + "|-".join(["" for _ in range(len(headers))]) + "|\n"
    for row in rows:
        fields = row.split("||")
        fields = list(filter(lambda x: x, re.split(r"\|(?![^\[]*\])", row)))[:n_columns]
        fields = [field.strip() for field in fields]
        markdown_table += "| " + " | ".join(fields).strip() + " |\n"

    return markdown_table + "\n"

    # text = filter(lambda x: x.startswith("| "), text.split("\n"))
    # text = map(lambda x: x.replace("| ", "- "), text)
    # text = "\n".join(text)
    # return text


def _convert_tables(wikitext):
    pattern = r"\{\|\s*class=\"wikitable sortable\"[\s\S]*?\|\}"
    output = re.sub(
        pattern,
        _convert_table,
        wikitext,
        flags=re.DOTALL,
    )
    return output


# def convert_wikitext_to_logseq_markdown(wikitext):
#     # Remove any HTML comments
#     wikitext = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL)

#     # Replace any templates with their contents
#     wikitext = re.sub(r'{{.*?}}', '', wikitext, flags=re.DOTALL)

#     # Replace any bold text with Logseq-compatible markdown
#     wikitext = re.sub(r"'''(.*?)'''", r'**\1**', wikitext)

#     # Replace any italicized text with Logseq-compatible markdown
#     wikitext = re.sub(r"''(.*?)''", r'*\1*', wikitext)

#     # Replace any headers with Logseq-compatible markdown
#     wikitext = re.sub(r'==(.*?)==', r'# \1', wikitext)

#     # Replace any links with Logseq-compatible markdown
#     wikitext = re.sub(r'\[\[(.*?)\|(.*?)\]\]', r'[\2](\1)', wikitext)
#     wikitext = re.sub(r'\[\[(.*?)\]\]', r'[[\1]]', wikitext)

#     # Remove any remaining HTML tags
#     wikitext = re.sub(r'<.*?>', '', wikitext, flags=re.DOTALL)

#     # Add line breaks after each paragraph
#     wikitext = re.sub(r'\n\n', '\n\n<br>\n\n', wikitext)

#     # Return the final Logseq-compatible markdown text
#     return wikitext

# def convert_wikitext_to_logseq_md(wikitext):
#     # Remove tables, which aren't supported in Logseq
#     wikitext = re.sub(r'{\|[\s\S]*?\|}', '', wikitext)
#     # Remove comments
#     wikitext = re.sub(r'<!--[\s\S]*?-->', '', wikitext)
#     # Convert headings
#     wikitext = re.sub(r'(?m)^(=+)(.*?)\1?$', r'\1 \2 \1', wikitext)
#     # Convert bold and italic
#     wikitext = re.sub(r"'''(.*?)'''", r'**\1**', wikitext)
#     wikitext = re.sub(r"''(.*?)''", r'*\1*', wikitext)
#     # Convert links
#     wikitext = re.sub(r'\[\[([^\]|]*)(\|([^\]]*))?\]\]', r'[\3](\1)', wikitext)
#     # Convert properties
#     wikitext = re.sub(r'^\|(.*?)\s*=\s*(.*?)$', r'\1:: \2', wikitext, flags=re.M)
#     # Convert bullets and numbering
#     wikitext = re.sub(r'^\*+(.*)$', r'-\1', wikitext, flags=re.M)
#     wikitext = re.sub(r'^(#+)(.*)$', r'\1 \2', wikitext, flags=re.M)
#     # Remove empty lines at the beginning and end of the text
#     wikitext = wikitext.strip()
#     return wikitext

# def wikitext_to_markdown(wikitext):
#     # Remove HTML comments
#     wikitext = re.sub(r"<!--.*?-->", "", wikitext, flags=re.DOTALL)

#     # Remove section headings
#     wikitext = re.sub(r"==+.*?==+", "", wikitext)

#     # Convert bold and italic tags to markdown
#     wikitext = re.sub(r"'''''(.*?)'''''", r"**_\1_**", wikitext)
#     wikitext = re.sub(r"''(.*?)''", r"_\1_", wikitext)
#     wikitext = re.sub(r"'''(.*?)'''", r"**\1**", wikitext)

#     # Convert bullet points and numbered lists to markdown
#     wikitext = re.sub(r"\n\s*\*", r"\n- ", wikitext)
#     wikitext = re.sub(r"\n\s*#", r"\n1. ", wikitext)

#     # Convert internal links to markdown
#     wikitext = re.sub(r"\[\[([^\|\]]+)\]\]", r"[[\1]]", wikitext)
#     wikitext = re.sub(r"\[\[([^\]]+)\|([^\]]+)\]\]", r"[[\1|\2]]", wikitext)

#     # Convert external links to markdown
#     wikitext = re.sub(r"\[(http.*?) (.*?)\]", r"[\2](\1)", wikitext)

#     # Remove extra newlines
#     wikitext = re.sub(r"\n{3,}", r"\n\n", wikitext)

#     return wikitext

# import re

# def convert_wikitext_to_markdown(wikitext):
#     # Convert headings
#     wikitext = re.sub("=+ (.+?) =+", r"# \1", wikitext)
#     wikitext = re.sub("=+([^=]+)=+", r"## \1", wikitext)
#     wikitext = re.sub("=([^=]+)=+", r"### \1", wikitext)

#     # Convert bold and italic text
#     wikitext = re.sub("'''''(.+?)'''''", r"***\1***", wikitext)
#     wikitext = re.sub("'''(.+?)'''", r"**\1**", wikitext)
#     wikitext = re.sub("''(.+?)''", r"*\1*", wikitext)

#     # Convert lists
#     wikitext = re.sub("\n#+\s?(.*)", r"\n\1", wikitext)
#     wikitext = re.sub("\n\*+\s?(.*)", r"\n- \1", wikitext)

#     # Convert links
#     # First, we need to remove any instances of double-bracket links that
#     # are already in the text so they don't get converted twice.
#     # We'll replace them with a placeholder string to add them back in later.
#     placeholders = {}
#     def replace_link(match):
#         link_text = match.group(1)
#         placeholder = f"__LINK_PLACEHOLDER_{len(placeholders)}__"
#         placeholders[placeholder] = link_text
#         return placeholder
#     wikitext = re.sub("\[\[(.+?)\]\]", replace_link, wikitext)

#     # Now we can convert any remaining links
#     wikitext = re.sub("\[(.+?)\s(.+?)\]", r"[\2](\1)", wikitext)

#     # Add back in any double-bracket links we removed earlier
#     for placeholder, link_text in placeholders.items():
#         wikitext = wikitext.replace(placeholder, f"[[{link_text}]]")

#     return wikitext
