"""
Data Loading/transforming scripts
"""

created = models.Topic.objects.all().values_list('name', flat=True)

names = [n for n in names if n not in created]
# for data in topics:
for name in names:
    print("-"*20)
    print(name)
    if name in created:
        print("!Exists!")
        continue

    data = ntc.create_topic_from_wiki(name)

    if not data:
        continue

    matches = ntc.check_topic_duplicates(data)

    if matches:
        print(f"{matches.count()} matches found: {matches}")
        continue

    topic = ntc.create_topic(data)

    print("!Created!")
    print(topic)

