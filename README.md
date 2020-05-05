# Anime Genre Classification Project

This personal project aims to develop a **image classification model** to predict the genre of an anime based on the poster of the anime.
- The problem is formulated as a multi-label classification problem.
- The anime poster and genre information are obtained from [anime.net](https://myanimelist.net/anime/) through web scraping.
- The network is coded in PyTorch and implemented transfer learning based on pre-trained ResNet18.
- The model is deployed as a Cloud Function and served on a Flask App at [https://shi-wang-dot-euphoric-oath-172818.appspot.com/anime](https://shi-wang-dot-euphoric-oath-172818.appspot.com/anime).

# [Part I: Web Scraping](https://drive.google.com/open?id=1kkbBwR9xUn99p9BSWLV6jQ3TTMmovvWW)

<img src="./notebooks/Data Preparation.png" width="600">

- The first step is to extract anime data from [anime.net](https://myanimelist.net/anime/), including anime name, genre, rating, etc.
- The web scraping is implemented through the well-known *BeautifulSoup* package.
- The poster of each anime is downloaded as a figure and saved at a Google Drive folder.
- The summary table including anime genre and info is saved as a csv file.

# [Part II: Model Development](https://drive.google.com/open?id=1UyZtcORjIV4pWlilYxlSdTm9CPybB3hD)

- This part aims to develop a model to predict the genre of an anime based only on the poster of the anime. The problem is formulated as a multi-label classification problem as each anime could have multiple genres.


- ***Preprocessing***: the images are preprocessed before feeding to the model include:
  - Resize to 256X256
  - Normalize with mean=0.5 and std=0.5 for each of the three channels.

<img src="/notebooks/Data Preprocessing.png" width="750">

- ***Programming Language***: *PyTorch* is used as the language to write and train the neural network.

- ***Network Architecture***: Two approaches are implemented to compare their performance
  - A model written from scratch with several Conv, Pooling and FC layers.
  - Transfer Learning with ResNet18, and only the weights in the last FC layers are updated during training.


<img src="/notebooks/Model Training.png" width="700">



- ***Loss function***: *MultiLabelSoftMarginLoss* is used as the loss function of this multi-label classification problem.

- ***Evaluation metric***: the *weighted F1-score* is used as the evaluation metric to select best network and hyperparameters.

- ***Environment***: The model is trained on GPU as provided by Google Colab.
- ***Monitoring Tool***: The model performance is monitored by utilizing *TensorBoard*.

*The model is still under improvement*

<img src="/notebooks/tensor_board.png" width="500">

# [Part III: Model Deployment](https://drive.google.com/open?id=1-EJAcL6p8TItZIdZXgcJRLrt-7UnapQC)

<img src="/notebooks/Model Deployment.png" width="500">

- This part aims to deploy the trained deep learning model as a Cloud Function on Google Cloud Platform. The deployment requires the input of two files:
  - *requirement.txt*: which specifies the dependencies that need to be installed
  - *main.py*: which takes a HTTP request as input, calls the trained model saved on Google Cloud Storage, and generates the predicted results.

- After deploying the trained model as a Cloud Function, the prediction can be retrieved by simply using:
  - `CLOUD_FUNCTION_URL = 'https://us-central1-euphoric-oath-172818.cloudfunctions.net/test_pytorch'`
  - `requests.post(CLOUD_FUNCTION_URL, json={'name':PATH_TO_FIGURE})`
