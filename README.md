# Errands

Errands is an advanced task scheduling and execution framework designed to offer robust workload management capabilities for your project.

## Table of Contents

1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Setup](#setup)
    - [Installation](#installation)
    - [Configuration](#configuration)
4. [Usage](#usage)
    - [Adding Errands](#adding-errands)

## Introduction

Errands stands out as a versatile project designed to offer a flexible and efficient framework for scheduling and executing tasks within the context of your project. The primary goal is to provide enhanced capabilities for managing a diverse range of workloads.

## Requirements

Running Errands requires the following dependencies:

- Python 3.x
- croniter>=2.0.1

## Setup

To integrate Errands into your project, follow these steps:

### Installation

```bash
pip install errands
```

### Configuration

Initiate the configuration by importing `ErrandsConfig` and initializing it with the `BASE_DIR` of your project. Use the `errand` decorator to mark the functions you wish to schedule.

```python
from errands.config import ErrandsConfig

BASE_DIR = "/path/to/your/project"
errands_config = ErrandsConfig(BASE_DIR)
```

## Usage

Effectively utilize Errands with the following guidelines:

### Adding Errands

Schedule functions as errands by decorating them with the `errand` decorator:

```python
from errands.executor import errand

@errand(cron_string="* * * * *", errand_type="SHORT")
def example_errand():
    # Errand logic here
```

### Running the Errands

The errands run indefinitely. You can set them up as daemon processes using tools like supervisord. Run the errands based on their queue, setting up different commands to process distinct queues after [configuration](#configuration).

```python
from errands.executor import LongErrandsExecutor, MediumErrandsExecutor, ShortErrandsExecutor

# Initialize the classes above separately to run the different queues

LongErrandsExecutor()

# or MediumErrandsExecutor() or ShortErrandsExecutor()
```
