import base64
import argparse
from time import sleep
from pathlib import Path

from tqdm import tqdm
from numpy import random
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from sklearn.metrics import classification_report, confusion_matrix

import seaborn as sns
import matplotlib.pyplot as plt
import json


def send_image(llm: ChatOpenAI, img_path: Path, prompt: str):
    with open(img_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode("UTF-8")
    
    messages = [
        HumanMessage(content=[
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_encoded_data}"},
            {"type": "text", "text": prompt}
        ]),
    ]

    successfull_answer = False

    while not successfull_answer:
        try:
            sleep_time = random.randint(10, 15)
            sleep(sleep_time)
            response = llm.invoke(messages)
        except Exception as ex:
            print(ex)
            continue
        else:
            successfull_answer = True

    return response.content


def process_folder(llm: ChatOpenAI, folder_path: Path, prompt: str) -> dict:
    # Go through all images in folder_path and send them to openrouter
    ans_dict = dict()

    imgs_list = list(folder_path.rglob('*.jpg'))

    for img_path in tqdm(imgs_list, desc='Processing images'):
        ans_dict[img_path] = send_image(llm, img_path, prompt)

    return ans_dict


def main(model_name: str, short_model_name: str, pass_key: str, prompt_file_path: str):
    llm = ChatOpenAI(model=model_name, temperature=0.6, openai_api_key=pass_key, openai_api_base="https://openrouter.ai/api/v1")

    with open(prompt_file_path) as file:
        prompt = '\n'.join(file.readlines())

    raw_data_answers = process_folder(llm, Path('raw_data'), prompt)
    normal_rooms_answers = process_folder(llm, Path('normal_rooms'), prompt)

    pred_vals = [int('yes' in val.lower()) for val in raw_data_answers.values()] + [int('yes' not in val.lower()) for val in normal_rooms_answers.values()]
    true_vals = [1] * len(raw_data_answers) + [0] * len(normal_rooms_answers)

    cls_report = classification_report(true_vals, pred_vals)

    print(cls_report)
    
    plt.figure(figsize=(10, 10))
    plt.title(f'Confusion Matrix for {short_model_name}')
    sns.heatmap(confusion_matrix(true_vals, pred_vals), annot=True, cmap='Blues')
    plt.xlabel('Predicted Labels')
    plt.ylabel('True Labels')

    # Save metrics and plots to disk
    with open(f'results/{short_model_name}__metrics.txt', 'w') as f:
        f.write(cls_report)

    plt.savefig(f'results/{short_model_name}__confusion_matrix.png')

    # Save model answers to disk
   
    with open(f'results/{short_model_name}__answers.json', 'w') as f:
        raw_data_answers.update(normal_rooms_answers)

        raw_data_answers = {str(key): val for key, val in raw_data_answers.items()}

        json.dump(raw_data_answers, f)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_name', type=str, required=True)
    parser.add_argument('--pass_key', type=str, required=True)
    parser.add_argument('--prompt_file_path', type=str, required=True)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    main(args.model_name, args.model_name.split('/')[-1], args.pass_key, args.prompt_file_path)
