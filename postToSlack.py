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
from tqdm import tqdm
from bs4 import BeautifulSoup
from googletrans import Translator
translator = Translator()


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
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
        }
    url_name = "https://openaccess.thecvf.com/CVPR2020"
    url = requests.get(url_name, headers)
    soup = BeautifulSoup(url.content, "html.parser")
    elems = soup.find_all("dt")
    for elem in tqdm(elems):
        url = elem.next.next.attrs['href']
        ori_link = "https://openaccess.thecvf.com/"
        contents_url = ori_link + url
        paper_link = requests.get(contents_url, headers)
        paper_soup = BeautifulSoup(paper_link.content, "html.parser")
        title = paper_soup.find('div', id="papertitle").text
        abstract = paper_soup.find('div', id="abstract").text
        abstract_ja = translator.translate(abstract, src='en', dest='ja')
        abstract_ja = str(abstract_ja.text)
        pdf = paper_soup.find("dd").find("a").attrs['href'][6:]
        pdf_link = ori_link + pdf
        class_name = sort_class(abstract)

        attachments_title = []
        attachments_contents = []
        paper_title = {"title": title,
                "text": pdf_link}
        paper_contents = {"title": abstract,
                "text": abstract_ja}
        attachments_title.append(paper_title)
        attachments_contents.append(paper_contents)
        if class_name == "adver":
            slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
            slack.notify(attachments=attachments_title)
            slack.notify(attachments=attachments_contents)
        else:
            slack = slackweb.Slack(url="https://hooks.slack.com/services/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")
            slack.notify(attachments=attachments_title)
            slack.notify(attachments=attachments_contents)

        time.sleep(3600)


if __name__ == "__main__":
    main()
