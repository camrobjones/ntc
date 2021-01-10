"""
Testing data for NTC
"""


def topic_data():

    data_clean = {
        "name": "Mahatma Gandhi",
        "description": """Mohandas Karamchand Gandhi (/ˈɡɑːndi, ˈɡændi/;[2] 2 October 1869 – 30 January 1948) was an Indian lawyer,[3] anti-colonial nationalist,[4] and political ethicist,[5] who employed nonviolent resistance to lead the successful campaign for India's independence from British rule,[6] and in turn inspired movements for civil rights and freedom across the world. The honorific Mahātmā (Sanskrit: "great-souled", "venerable"), first applied to him in 1914 in South Africa, is now used throughout the world.[7][8]""",
        "category": "PER",
        "profile": 1,
        "url": "https://en.wikipedia.org/wiki/Mahatma_Gandhi",
        "tags": []
    }

    data_error = {
        "name": "Llanfairpwll-gwyngyllgogerychwyrndrob-wllllantysiliogogogoch",
        "description": "-" * 1001,
        "category": "Village",
        "profile": 1,
        "url": "gobbltygook",
        "tags": []
    }

    return {
        "clean": data_clean,
        "error": data_error
    }