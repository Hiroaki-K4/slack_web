"""
postToSlack.py
author: Hiroaki Kubo
time: 2020/07/19
license: ikuiku
"""
import re
import time
import slackweb
import requests
# from tqdm import tqdm
from bs4 import BeautifulSoup


def sort_class(abstract):
    """
    Sort paper class by using regular expression
    @param abstract: absract of paper
    """
    sentence = abstract
    adversarial_1 = re.search("adversarial attacks", sentence)
    adversarial_2 = re.search("Adversarial Attacks", sentence)
    adversarial_3 = re.search("adversarial examples", sentence)
    adversarial_4 = re.search("Adversarial Examples", sentence)
    adversarial_5 = re.search("adversarial robustness", sentence)
    adversarial_6 = re.search("Adversarial Robustness", sentence)
    adversarial_7 = re.search("adversarial noise", sentence)
    adversarial_8 = re.search("Adversarial Noise", sentence)
    if adversarial_1 != None or adversarial_2 != None or adversarial_3 != None or adversarial_4 != None or adversarial_5 != None or adversarial_6 != None or adversarial_7 != None or adversarial_8 != None:
        class_name = "adver"
        return class_name
    else:
        class_name = "other"
        return class_name


def main():
    """
    Main method
    """
    url_name = "https://openaccess.thecvf.com/CVPR2020"
    url = requests.get(url_name)
    soup = BeautifulSoup(url.content, "html.parser")
    elems = soup.find_all("dt")
    for elem in elems:
        url = elem.next.next.attrs['href']
        ori_link = "https://openaccess.thecvf.com/"
        contents_url = ori_link + url
        paper_link = requests.get(contents_url)
        paper_soup = BeautifulSoup(paper_link.content, "html.parser")
        title = paper_soup.find('div', id="papertitle").text
        abstract = paper_soup.find('div', id="abstract").text
        pdf = paper_soup.find("dd").find("a").attrs['href'][6:]
        pdf_link = ori_link + pdf
        class_name = sort_class(abstract)

        attachments = []
        attachment = {"title": abstract,
                "pretext": title,
                "text": pdf_link,
                "mrkdwn_in": ["text", "pretext"]}
        attachments.append(attachment)
        if class_name == "adver":
            slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
            slack.notify(attachments=attachments)
        else:
            slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
            slack.notify(attachments=attachments)

        time.sleep(7200)


if __name__ == "__main__":
    main()
