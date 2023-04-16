import pytest
from src.converter import (
    _convert_header,
    _extract_infobox,
    _parse_infobox,
    covert_wikitext_to_markdown,
)


@pytest.mark.parametrize(
    "wikitext, expected_markdown",
    [
        ("=Level 1=", "# Level 1"),
        ("=**Level 1**=", "# Level 1"),
        ("==**Level 2**==", "## Level 2"),
        ("==Level 2==", "## Level 2"),
        ("===Level 3===", "### Level 3"),
        ("====Level 4====", "#### Level 4"),
        ("=====Level 5=====", "##### Level 5"),
    ],
)
def test_convert_headers(wikitext, expected_markdown):
    markdown = _convert_header(wikitext)

    assert markdown == expected_markdown


def test_identify_infobox():
    wikitext = """{{Infobox City
|title = Nicodranas
|image = [[File:Nicodranas_by_adragonswinging.jpg|thumb]]
|caption = {{art official caption|subject=[[Nicodranas]]|artist=adragonswinging|source=https://twitter.com/adragonswinging/status/1246492204975169543}}
<!-- General Information -->
|currentleader = [[Zhafe Uludan]]{{guide ref|EGtW|67}}
<!-- Societal Information -->
|population = 31,900 (in [[Time Line#EGTW|835 PD]]){{guide ref|EGtW|67}}
|races=
*68% [[Human]]
*13% [[Halfling]]
*8% [[Dwarf]]
*10% Others {{ this is another {{with a double nested}} }}
|affiliation = [[Clovis Concord]]
}} THIS IS NOT PART OF AN INFOBOX
    """
    infobox = _extract_infobox(wikitext)
    expected_infobox = """{{Infobox City
|title = Nicodranas
|image = [[File:Nicodranas_by_adragonswinging.jpg|thumb]]
|caption = {{art official caption|subject=[[Nicodranas]]|artist=adragonswinging|source=https://twitter.com/adragonswinging/status/1246492204975169543}}
<!-- General Information -->
|currentleader = [[Zhafe Uludan]]{{guide ref|EGtW|67}}
<!-- Societal Information -->
|population = 31,900 (in [[Time Line#EGTW|835 PD]]){{guide ref|EGtW|67}}
|races=
*68% [[Human]]
*13% [[Halfling]]
*8% [[Dwarf]]
*10% Others {{ this is another {{with a double nested}} }}
|affiliation = [[Clovis Concord]]
}}"""
    assert infobox == expected_infobox


def test_parse_infobox():
    infobox = """|plane = [[Material Plane]] ([[Exandria]])
|continent = [[Wildemount]]
|region = [[Menagerie Coast]]
|districts = 
*Restless Wharf
*Open Quay
*Opal Archways
*The Skew
|poi = 
*[[Mother's Lighthouse]]
*[[Wayfarer's Cove]]
*[[Tidepeak]]
*[[Lavish Chateau]]
*Marquis Demesne"""
    parsed_infobox = _parse_infobox(infobox)
    expected_infobox = """plane:: [[Material Plane]] ([[Exandria]])
continent:: [[Wildemount]]
region:: [[Menagerie Coast]]
districts:: Restless Wharf, Open Quay, Opal Archways, The Skew
poi:: [[Mother's Lighthouse]], [[Wayfarer's Cove]], [[Tidepeak]], [[Lavish Chateau]], Marquis Demesne"""
    assert parsed_infobox == expected_infobox


def test_convert_wikitext_page():
    with open("data/nicodranas.txt", "r") as f:
        wikitext = f.read()

    markdown = covert_wikitext_to_markdown(wikitext)

    assert markdown == ""
