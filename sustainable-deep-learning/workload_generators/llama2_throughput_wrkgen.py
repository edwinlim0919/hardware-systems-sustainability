import json
import random
import argparse
import requests
import numpy as np
import time


# Sampling dataset prompts for throughput experiments
def sample_dataset_prompts(
    dataset_path: str,
    num_requests: int
):
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Filter out the conversations with less than 2 turns.
    dataset = [data for data in dataset if len(data["conversations"]) >= 2]
    # Only keep the first prompt of each conversation.
    dataset = [data["conversations"][0]["value"] for data in dataset]
    if num_requests < 1:
        num_requests = len(dataset)

    print('SAMPLED DATASET')
    sampled_dataset = random.sample(dataset, num_requests)
    print(sampled_dataset)

    return sampled_dataset


# Generate a slowly increasing amount of request rates according to a Poisson distribution
def generate_requests(
    sampled_dataset: List[str],
    requests_per_rate: int,         # requests
    start_rate: int,                # requests per minute
    end_rate: int,                  # requests per minute
    rate_increase: int              # requests per minute
):
    # for reproducability
    np.random.seed(42)
    curr_rate = start_rate

    while curr_rate < end_rate:
        # requests per minute converted to requests per second
        lambda_rate = curr_rate / 60

        # calculating arrival times
        inter_arrival_times = np.random.exponential(1 / lambda_rate, size=requests_per_rate)
        arrival_times = np.cumsum(inter_arrival_times)

        curr_rate += rate_increase


#shareGPT_file_path = 'ShareGPT_V3_unfiltered_cleaned_split.json'
#shareGPT_dataset_path = 'ShareGPT_V3_unfiltered_cleaned_split_top100.json'
#sample_dataset_prompts(shareGPT_dataset_path, 0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Throughput generation script for LLM inference experiments.')
    parser.add_argument(
        '--dataset-path',
        required=True,
        help='The path to the dataset file.'
    )
    parser.add_argument(
        '--num-requests',
        required=True,
        help='The number of requests to sample. Specify 0 or less to sample the entire dataset.'
    )
    args = parser.parse_args()

    sampled_dataset = sample_dataset_prompts(
        args.dataset_path,
        int(args.num_requests)
    )
