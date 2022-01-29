# Human Values Research: Swartz Values from code comments

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Human Values Research: Swartz Values from code comments](#human-values-research-swartz-values-from-code-comments)
    - [-](#-)
        - [Label single comment using text area](#label-single-comment-using-text-area)
        - [Retrieve and predict all comment from git repository for human value mentions](#retrieve-and-predict-all-comment-from-git-repository-for-human-value-mentions)
        - [Upload and predict CSV files by specifying name of column](#upload-and-predict-csv-files-by-specifying-name-of-column)
        - [Requirements](#requirements)
    - [Machine learn](#machine-learn)
    - [Steps](#steps)
        - [Data Collection](#data-collection)
        - [Create Features](#create-features)
        - [Outlier Removal](#outlier-removal)
        - [Case normalisation](#case-normalisation)
        - [Tokenisation](#tokenisation)
        - [Stop word removal](#stop-word-removal)
        - [Split Compound words](#split-compound-words)
        - [Lemmatization](#lemmatization)
        - [Sample Data](#sample-data)
        - [Binarize Labels](#binarize-labels)
        - [Create Models](#create-models)
        - [Training Models](#training-models)
        - [Tune Models](#tune-models)
        - [Evaluate Models](#evaluate-models)
        - [Select Models](#select-models)
        - [Deploy Models](#deploy-models)

<!-- markdown-toc end -->

![label applier](readme_files/pic4.png) 

### How to use

#### Label single comment using text area
Simply place the comment that need labelling into the text area and submit
![label applier](readme_files/pic1.png') 

#### Retrieve and predict all comment from git repository for human value mentions
Select git repo link and enter name of branch in a similar fashion to cloning a git repository. A background queue will complete and create a download file once finish. **This could take a lone time**
![label applier](readme_files/pic2.png) 


#### Upload and predict CSV files by specifying name of column
Upload a csv file and specify a column to label in the csv file.
![label applier](readme_files/pic3.png) 

### Requirements
**celery** - For background queue and workers to handle background jobs for process heaving machine learning and file processing tasks <br />
**Flask** - For backend <br />
**Flask-WTF** - For validating data on frontend <br />
**pytest** - for testing <br />
**flower** - A dashboard to visualise process and tasks from background works in celery <br />
**chardet** - Helps with decoding different types of files <br />
**Flask-DebugToolbar** - Flask toolbar useful for debugging <br />
**GitPython** - Tool used to retrieve files from branches in github repositories <br />
**gunicorn** - WSGI python http server for UNIX based systems <br />
**Jinja2** - Tool used to help flask render templates <br />
**joblib** - used to dump machine learning models and vocabulary <br />
**matplotlib** - used to help visualise date and plotting <br />
**missingno** - used to help with visualising missing or empty data <br />
**nltk** - natural language processing toolkit <br />
**numpy** - used to facilitate mathematics operations inside python <br />
**pandas** - used to create dataframe and read csv files  <br />
**regex** - used to for regular expressions <br />
**scikit-learn** - machien learning models  <br />
**scipy** - helped with combining sparse matrices <br />
**seaborn** <br />
**sklearn** - used for creating machine learning models such as gbdt, knn, svc, decision trees, multiple layer perceptron and model selection <br />
**Werkzeug** - securely save files <br />
**redis** - a ram based database system to handle background workers and databases <br />



## Machine learn

## Steps

### Data Collection

### Create Features

### Outlier Removal

### Case normalisation

### Tokenisation

### Stop word removal

### Split Compound words

### Lemmatization

### Sample Data

### Binarize Labels

### Create Models

### Training Models

### Tune Models

### Evaluate Models

### Select Models

### Deploy Models


