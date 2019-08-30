FROM python:3.6

# Install dependencies
RUN pip install --upgrade pip
RUN pip install pandas

# Move to the app folder
RUN mkdir /app
WORKDIR /app

# Copy our python program for training and inference
COPY ./Mortality-Prediction.py .
COPY ./adding_values.py .

#CMD ["python", "./Mortality-Prediction.py", "-f", "/data", "-p" "top_10000_synpuf"]