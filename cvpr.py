"""
cvpr.py
author: Hiroaki Kubo
time: 2020/07/30
license: ikuiku
"""
import os
import re
import time
import tempfile
import requests
import slackweb
from bs4 import BeautifulSoup
from tqdm import tqdm
from googletrans import Translator
from google.cloud import storage
translator = Translator()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=''



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
    with tempfile.TemporaryDirectory() as temp_path:
        write_path = temp_path + '/cvpr.txt'
        client = storage.Client()
        bucket_name = "penguin-first"
        bucket = client.get_bucket(bucket_name)
        blob = bucket.get_blob('cvpr.txt')
        blob.download_to_filename(write_path)
        with open(write_path) as f:
            l_strip = [s.strip() for s in f.readlines()]

    if l_strip[0] == '0616':
        url_name = "https://openaccess.thecvf.com/CVPR2020?day=2020-06-16"
    if l_strip[0] == '0617':
        url_name = "https://openaccess.thecvf.com/CVPR2020?day=2020-06-17"
    if l_strip[0] == '0618':
        url_name = "https://openaccess.thecvf.com/CVPR2020?day=2020-06-18"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0"
        }
    url = requests.get(url_name, headers)
    soup = BeautifulSoup(url.content, "html.parser")
    elems = soup.find_all("dt")

    date = l_strip[0]
    min_number = int(l_strip[1])
    max_number = min_number + 15
    total_number = len(elems)
    if max_number >= total_number:
        max_number = total_number
        date = int(l_strip[0][3]) + 1
        date = l_strip[0][:3] + str(date)
    
    for elem in tqdm(elems[min_number:max_number]):
        url = elem.next.next.attrs['href']
        # url = url.replace('html', 'papers')
        # url = url.replace('.papers', '.html')
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

        time.sleep(2)

    text_list = [date, str(max_number)]
    with tempfile.TemporaryDirectory() as temp_path:
        write_path = temp_path + '/cvpr.txt'
        with open(write_path, mode='w') as f:
            f.write('\n'.join(text_list))
        client = storage.Client()
        bucket_name = "penguin-first"
        bucket = client.get_bucket(bucket_name)
        blob = bucket.blob('cvpr.txt')
        blob.upload_from_filename(filename=write_path)


if __name__ == '__main__':
    main()
