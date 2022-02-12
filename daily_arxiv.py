import datetime
import requests
import json
import arxiv
import os

def get_authors(authors, first_author = False):
    output = str()
    if first_author == False:
        output = ",".join(str(author) for author in authors)
    else:
        output = authors[0]

    return output


def sort_papers(papers):
    output = dict()
    keys   = list(papers.keys())
    keys.sort(reverse=True)
    for key in keys:
        output[key] = papers[key]
    return output

def get_daily_papers(topic, query="object detection", max_results=3):
    content = dict()

    search_engine = arxiv.Search(
            query       = query,
            max_results = max_results,
            sort_by     = arxiv.SortCriterion.SubmittedDate
            )

    for result in search_engine.results():
        paper_id    = result.get_short_id()
        paper_title = result.title
        paper_url   = result.entry_id

        paper_abstract = result.summary.replace("\n", " ")
        paper_authors  = get_authors(result.authors)
        paper_first_author = get_authors(result.authors, first_author = True)

        primary_category   = result.primary_category

        publish_time       = result.published.date()


        print("Time = ", publish_time,
              " title = ", paper_title,
              " author = ", paper_first_author)

        ver_pos = paper_id.find('v')
        if ver_pos == -1:
            paper_key = paper_id
        else:
            paper_key = paper_id[0:ver_pos]

        content[paper_key] = f"|**{publish_time}**|**{paper_title}**|{paper_first_author} et.al.|[{paper_id}]({paper_url})|\n"

    data = {topic:content}

    return data


def update_json_file(filename, data_all):
    with open(filename, "r") as f:
        content = f.read();
        if not content:
            m = {}
        else:
            m = json.loads(content)


    json_data = m.copy()

    for data in data_all:
        for keyword in data.keys():
            papers = data[keyword]

            if keyword in json_data.keys():
                json_data[keyword].update(papers)
            else:
                json_data[keyword] = papers

    with open(filename, "w") as f:
        json.dump(json_data, f)

def json_to_md(filename):

    DateNow = datetime.date.today()
    DateNow = str(DateNow)
    DateNow = DateNow.replace('-', '.')

    with open(filename, "r") as f:
        content = f.read()
        if not content:
            data = {}
        else:
            data = json.loads(content)

    md_filename = "README.md"

    with open(md_filename, "w+") as f:
        pass

    with open(md_filename, "a+") as f:
        f.write("## Updated on " + DateNow + "\n\n")

        for keyword in data.keys():
            day_content = data[keyword]
            if not day_content:
                continue

            f.write(f"## {keyword}\n\n")
            f.write("|Publish Date|Title|Authors|PDF|\n" + "|---|---|---|---|\n")

            day_content = sort_papers(day_content)

            for _, v in day_content.items():
                if v is not None:
                    f.write(v)

            f.write(f"\n")

    print("finished")


if __name__ == "__main__":
    data_collector = []

    keywords = dict()
    keywords["object detection"] = "object detection"
    keywords["meta learning"] = "meta learning"
    keywords["reinforcement learning"] = "reinforcement learning"
    keywords["few-shot learning"] = "few-shot learning"
    keywords["transformer"] = "transformer"
    keywords["attention mechanism"] = "attention mechanism"

    for topic, keyword in keywords.items():
        print("Keyword: " + topic)
        data = get_daily_papers(topic, query = keyword, max_results = 6)
        data_collector.append(data)
        print("\n")


    json_file = "arxiv-daily.json"
    if ~os.path.exists(json_file):
        with open(json_file, 'w') as a:
            print("create " + json_file)


    update_json_file(json_file, data_collector)

    json_to_md(json_file)

